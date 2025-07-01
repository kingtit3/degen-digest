#!/usr/bin/env python3
"""
Automated Model Retraining System
Continuously improves viral prediction models
"""

import asyncio
import json
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging

from utils.advanced_logging import get_logger
from processor.enhanced_viral_predictor import enhanced_predictor
from scripts.enhanced_data_pipeline import EnhancedDataPipeline

logger = get_logger(__name__)

class AutomatedRetraining:
    """Automated model retraining system"""
    
    def __init__(self):
        self.retraining_config = {
            'retrain_frequency_hours': 24,
            'min_data_points': 100,
            'performance_threshold': 0.8,  # R² score threshold
            'drift_detection_threshold': 0.1,  # Performance degradation threshold
            'backup_models': True,
            'notify_on_retrain': True
        }
        
        self.performance_history = []
        self.last_retrain_time = None
        self.model_versions = []
        
    async def run_continuous_retraining(self):
        """Run continuous retraining loop"""
        
        logger.info("Starting automated retraining system...")
        
        # Schedule retraining
        schedule.every(self.retraining_config['retrain_frequency_hours']).hours.do(
            self.schedule_retraining
        )
        
        # Run initial retraining
        await self.retrain_model()
        
        # Continuous monitoring loop
        while True:
            try:
                schedule.run_pending()
                await asyncio.sleep(3600)  # Check every hour
                
            except KeyboardInterrupt:
                logger.info("Automated retraining stopped by user")
                break
            except Exception as e:
                logger.error(f"Retraining loop error: {e}")
                await asyncio.sleep(3600)  # Wait before retrying
    
    def schedule_retraining(self):
        """Schedule model retraining"""
        asyncio.create_task(self.retrain_model())
    
    async def retrain_model(self):
        """Retrain the viral prediction model"""
        
        logger.info("Starting automated model retraining...")
        
        try:
            # Step 1: Collect fresh data
            pipeline = EnhancedDataPipeline()
            await pipeline.run_full_pipeline()
            
            # Step 2: Check if we have enough data
            if len(pipeline.processed_data) < self.retraining_config['min_data_points']:
                logger.warning(f"Insufficient data for retraining. Need {self.retraining_config['min_data_points']}, got {len(pipeline.processed_data)}")
                return
            
            # Step 3: Backup current model
            if self.retraining_config['backup_models']:
                self.backup_current_model()
            
            # Step 4: Retrain model
            start_time = time.time()
            enhanced_predictor.train(pipeline.processed_data)
            training_time = time.time() - start_time
            
            # Step 5: Evaluate new model
            performance = self.evaluate_model_performance()
            
            # Step 6: Check for performance improvement
            if self.should_keep_new_model(performance):
                self.accept_new_model(performance, training_time)
                logger.info("New model accepted and deployed")
            else:
                self.revert_to_previous_model()
                logger.warning("New model rejected, reverted to previous version")
            
            # Step 7: Update retraining history
            self.update_retraining_history(performance, training_time)
            
            # Step 8: Save retraining report
            self.save_retraining_report()
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
            self.revert_to_previous_model()
    
    def backup_current_model(self):
        """Backup current model before retraining"""
        
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = f"models/backup/viral_predictor_{timestamp}.joblib"
            
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            enhanced_predictor.save_models(backup_path)
            
            logger.info(f"Model backed up to {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to backup model: {e}")
    
    def evaluate_model_performance(self) -> Dict[str, float]:
        """Evaluate current model performance"""
        
        try:
            # Get performance from the model
            performance = enhanced_predictor.model_performance.get('ensemble', {})
            
            if not performance:
                # Fallback to individual model performance
                for model_name, perf in enhanced_predictor.model_performance.items():
                    if perf.get('r2', 0) > 0:
                        performance = perf
                        break
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to evaluate model performance: {e}")
            return {'r2': 0, 'mse': float('inf'), 'mae': float('inf')}
    
    def should_keep_new_model(self, new_performance: Dict[str, float]) -> bool:
        """Determine if new model should be kept"""
        
        # Check if performance meets minimum threshold
        if new_performance.get('r2', 0) < self.retraining_config['performance_threshold']:
            logger.warning(f"New model performance below threshold: {new_performance.get('r2', 0)}")
            return False
        
        # Check for performance degradation
        if self.performance_history:
            last_performance = self.performance_history[-1]
            performance_degradation = last_performance.get('r2', 0) - new_performance.get('r2', 0)
            
            if performance_degradation > self.retraining_config['drift_detection_threshold']:
                logger.warning(f"Performance degradation detected: {performance_degradation}")
                return False
        
        return True
    
    def accept_new_model(self, performance: Dict[str, float], training_time: float):
        """Accept and deploy new model"""
        
        # Save the new model
        enhanced_predictor.save_models("models/enhanced_viral_predictor.joblib")
        
        # Update version tracking
        version_info = {
            'version': len(self.model_versions) + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'performance': performance,
            'training_time': training_time,
            'status': 'deployed'
        }
        
        self.model_versions.append(version_info)
        self.last_retrain_time = datetime.utcnow()
        
        logger.info(f"New model deployed - Version {version_info['version']}")
    
    def revert_to_previous_model(self):
        """Revert to previous model version"""
        
        try:
            # Find the most recent backup
            backup_dir = Path("models/backup")
            if backup_dir.exists():
                backup_files = list(backup_dir.glob("viral_predictor_*.joblib"))
                if backup_files:
                    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                    enhanced_predictor.load_models(str(latest_backup))
                    logger.info(f"Reverted to backup model: {latest_backup}")
            
        except Exception as e:
            logger.error(f"Failed to revert to previous model: {e}")
    
    def update_retraining_history(self, performance: Dict[str, float], training_time: float):
        """Update retraining history"""
        
        history_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'performance': performance,
            'training_time': training_time,
            'data_points': len(enhanced_predictor.model_performance) if enhanced_predictor.model_performance else 0
        }
        
        self.performance_history.append(history_entry)
        
        # Keep only last 30 entries
        if len(self.performance_history) > 30:
            self.performance_history = self.performance_history[-30:]
    
    def save_retraining_report(self):
        """Save retraining report"""
        
        try:
            report = {
                'retraining_config': self.retraining_config,
                'last_retrain_time': self.last_retrain_time.isoformat() if self.last_retrain_time else None,
                'model_versions': self.model_versions,
                'performance_history': self.performance_history,
                'current_performance': enhanced_predictor.model_performance
            }
            
            report_path = Path("output/enhanced_pipeline/retraining_report.json")
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Retraining report saved to {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save retraining report: {e}")
    
    def get_retraining_stats(self) -> Dict[str, Any]:
        """Get retraining statistics"""
        
        return {
            'total_retrains': len(self.model_versions),
            'last_retrain': self.last_retrain_time.isoformat() if self.last_retrain_time else None,
            'current_performance': enhanced_predictor.model_performance.get('ensemble', {}),
            'performance_trend': self.calculate_performance_trend(),
            'next_retrain': self.get_next_retrain_time()
        }
    
    def calculate_performance_trend(self) -> str:
        """Calculate performance trend"""
        
        if len(self.performance_history) < 2:
            return "insufficient_data"
        
        recent_performance = self.performance_history[-1]['performance'].get('r2', 0)
        previous_performance = self.performance_history[-2]['performance'].get('r2', 0)
        
        if recent_performance > previous_performance + 0.01:
            return "improving"
        elif recent_performance < previous_performance - 0.01:
            return "declining"
        else:
            return "stable"
    
    def get_next_retrain_time(self) -> str:
        """Get next scheduled retrain time"""
        
        if not self.last_retrain_time:
            return "unknown"
        
        next_retrain = self.last_retrain_time + timedelta(hours=self.retraining_config['retrain_frequency_hours'])
        return next_retrain.isoformat()

async def main():
    """Main function for automated retraining"""
    
    retraining_system = AutomatedRetraining()
    
    try:
        await retraining_system.run_continuous_retraining()
        
    except KeyboardInterrupt:
        logger.info("Automated retraining stopped")
    except Exception as e:
        logger.error(f"Automated retraining failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 