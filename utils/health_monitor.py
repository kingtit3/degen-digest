"""Health monitoring system for Degen Digest."""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
from utils.advanced_logging import get_logger

logger = get_logger(__name__)

class HealthMonitor:
    """Monitor system health and performance metrics."""
    
    def __init__(self, output_dir: Path = Path("output")):
        self.output_dir = output_dir
        self.metrics_file = output_dir / "health_metrics.json"
        self.alerts_file = output_dir / "health_alerts.json"
        self.start_time = time.time()
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []
        
    def collect_system_metrics(self) -> Dict:
        """Collect current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def check_data_freshness(self) -> Dict:
        """Check if data files are fresh and accessible."""
        checks = {}
        files_to_check = [
            "twitter_raw.json",
            "reddit_raw.json", 
            "telegram_raw.json",
            "newsapi_raw.json",
            "coingecko_raw.json"
        ]
        
        for filename in files_to_check:
            file_path = self.output_dir / filename
            if file_path.exists():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_hours = (datetime.now() - mtime).total_seconds() / 3600
                file_size = file_path.stat().st_size
                
                checks[filename] = {
                    "exists": True,
                    "age_hours": age_hours,
                    "size_bytes": file_size,
                    "is_fresh": age_hours < 24,  # Consider fresh if < 24 hours
                    "has_content": file_size > 100
                }
            else:
                checks[filename] = {
                    "exists": False,
                    "age_hours": None,
                    "size_bytes": 0,
                    "is_fresh": False,
                    "has_content": False
                }
        
        return checks
    
    def check_database_health(self) -> Dict:
        """Check database connectivity and performance."""
        try:
            from storage.db import engine
            from sqlmodel import Session, select, func
            from storage.db import Tweet, RedditPost
            
            with Session(engine) as session:
                # Check table sizes
                tweet_count = session.exec(select(func.count()).select_from(Tweet)).one()
                reddit_count = session.exec(select(func.count()).select_from(RedditPost)).one()
                
                # Check recent activity
                recent_tweets = session.exec(
                    select(Tweet).order_by(Tweet.created_at.desc()).limit(1)
                ).first()
                
                return {
                    "connected": True,
                    "tweet_count": tweet_count,
                    "reddit_count": reddit_count,
                    "last_tweet_age_hours": (
                        (datetime.utcnow() - recent_tweets.created_at).total_seconds() / 3600 
                        if recent_tweets else None
                    ),
                    "database_size_mb": self._get_db_size()
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"connected": False, "error": str(e)}
    
    def _get_db_size(self) -> Optional[float]:
        """Get database file size in MB."""
        try:
            db_path = self.output_dir / "degen_digest.db"
            if db_path.exists():
                return db_path.stat().st_size / (1024 * 1024)
        except Exception:
            pass
        return None
    
    def check_llm_health(self) -> Dict:
        """Check LLM service health and usage."""
        try:
            from storage.db import get_month_usage
            from datetime import datetime
            
            month = datetime.utcnow().strftime("%Y-%m")
            usage = get_month_usage(month)
            
            return {
                "api_available": True,
                "monthly_tokens": usage.tokens if usage else 0,
                "monthly_cost_usd": usage.cost_usd if usage else 0.0,
                "budget_remaining_usd": 10.0 - (usage.cost_usd if usage else 0.0)
            }
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {"api_available": False, "error": str(e)}
    
    def run_health_check(self) -> Dict:
        """Run comprehensive health check."""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": self.collect_system_metrics(),
            "data_freshness": self.check_data_freshness(),
            "database": self.check_database_health(),
            "llm": self.check_llm_health()
        }
        
        # Store metrics
        self.metrics_history.append(health_data)
        if len(self.metrics_history) > 100:  # Keep last 100 entries
            self.metrics_history = self.metrics_history[-100:]
        
        # Check for alerts
        alerts = self._check_alerts(health_data)
        if alerts:
            self.alerts.extend(alerts)
            logger.warning(f"Health alerts detected: {alerts}")
        
        # Save to files
        self._save_metrics()
        self._save_alerts()
        
        return health_data
    
    def _check_alerts(self, health_data: Dict) -> List[Dict]:
        """Check for conditions that should trigger alerts."""
        alerts = []
        
        # System alerts
        if health_data["system"].get("cpu_percent", 0) > 80:
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "warning",
                "category": "system",
                "message": f"High CPU usage: {health_data['system']['cpu_percent']}%"
            })
        
        if health_data["system"].get("memory_percent", 0) > 85:
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "warning", 
                "category": "system",
                "message": f"High memory usage: {health_data['system']['memory_percent']}%"
            })
        
        # Data freshness alerts
        for filename, status in health_data["data_freshness"].items():
            if not status["is_fresh"] and status["exists"]:
                alerts.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "warning",
                    "category": "data",
                    "message": f"Stale data file: {filename} (age: {status['age_hours']:.1f}h)"
                })
        
        # Database alerts
        if not health_data["database"].get("connected", False):
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "error",
                "category": "database", 
                "message": "Database connection failed"
            })
        
        # LLM alerts
        llm_data = health_data["llm"]
        if llm_data.get("budget_remaining_usd", 10.0) < 1.0:
            alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "warning",
                "category": "llm",
                "message": f"Low LLM budget remaining: ${llm_data['budget_remaining_usd']:.2f}"
            })
        
        return alerts
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            self.metrics_file.write_text(json.dumps(self.metrics_history, indent=2))
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _save_alerts(self):
        """Save alerts to file."""
        try:
            self.alerts_file.write_text(json.dumps(self.alerts, indent=2))
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def get_health_summary(self) -> Dict:
        """Get a summary of current health status."""
        health_data = self.run_health_check()
        
        # Calculate overall health score (0-100)
        score = 100
        
        # Deduct points for issues
        if health_data["system"].get("cpu_percent", 0) > 80:
            score -= 20
        if health_data["system"].get("memory_percent", 0) > 85:
            score -= 20
        if not health_data["database"].get("connected", False):
            score -= 30
        if not health_data["llm"].get("api_available", False):
            score -= 15
        
        # Check data freshness
        stale_files = sum(1 for status in health_data["data_freshness"].values() 
                         if not status.get("is_fresh", True))
        score -= stale_files * 5
        
        return {
            "overall_score": max(0, score),
            "status": "healthy" if score >= 80 else "warning" if score >= 60 else "critical",
            "last_check": health_data["timestamp"],
            "active_alerts": len([a for a in self.alerts if a.get("level") == "error"]),
            "warnings": len([a for a in self.alerts if a.get("level") == "warning"])
        }

# Global health monitor instance
health_monitor = HealthMonitor() 