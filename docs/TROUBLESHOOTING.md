# Troubleshooting Guide

This document provides comprehensive troubleshooting information for the Degen Digest platform.

## Table of Contents

- [Quick Diagnostic Tools](#quick-diagnostic-tools)
- [Common Issues](#common-issues)
- [Service-Specific Issues](#service-specific-issues)
- [Performance Issues](#performance-issues)
- [Data Issues](#data-issues)
- [Security Issues](#security-issues)
- [Emergency Procedures](#emergency-procedures)
- [Debug Tools](#debug-tools)
- [Log Analysis](#log-analysis)
- [Recovery Procedures](#recovery-procedures)

## Quick Diagnostic Tools

### System Health Check

```bash
# Quick system health check
python test_current_status.py

# Detailed health check
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/health/detailed

# Check all services
./check_all_services.sh
```

### Log Analysis

```bash
# View recent errors
grep "ERROR" logs/degen_digest.log | tail -20

# View recent warnings
grep "WARNING" logs/degen_digest.log | tail -20

# View performance issues
grep "PERFORMANCE" logs/degen_digest.log | tail -20

# View security events
grep "SECURITY" logs/degen_digest.log | tail -20
```

### Service Status

```bash
# Check crawler status
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/crawler/status

# Check dashboard status
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/dashboard/status

# Check storage status
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/storage/health
```

## Common Issues

### 1. Crawler Not Starting

#### Symptoms

- Crawler service shows "stopped" status
- No new data being collected
- Error messages in crawler logs

#### Diagnostic Steps

```bash
# 1. Check crawler logs
tail -f logs/crawler.log

# 2. Check Twitter credentials
python test_twitter_login.py

# 3. Check system resources
htop
df -h
free -h

# 4. Check network connectivity
ping twitter.com
curl -I https://twitter.com

# 5. Check Playwright installation
python -c "import playwright; print('Playwright OK')"
```

#### Common Causes and Solutions

**A. Twitter Login Issues**

```bash
# Reset Twitter credentials
export TWITTER_USERNAME="your_username"
export TWITTER_PASSWORD="your_password"

# Test login
python test_twitter_login.py

# If login fails, check for:
# - 2FA enabled (disable temporarily)
# - Account locked (check email)
# - Rate limiting (wait 15 minutes)
```

**B. Playwright Issues**

```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium

# Check browser installation
playwright install --help
```

**C. System Resource Issues**

```bash
# Check available memory
free -h

# Check disk space
df -h

# Check CPU usage
top

# If resources are low:
# - Restart system
# - Increase Cloud Run memory allocation
# - Optimize crawler settings
```

#### Resolution Steps

```bash
# 1. Restart crawler service
./restart_crawler.sh

# 2. If that fails, redeploy crawler
./deploy_crawler_to_gcloud.sh

# 3. Verify crawler is running
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/crawler/status

# 4. Monitor logs
tail -f logs/crawler.log
```

### 2. Dashboard Not Loading

#### Symptoms

- Dashboard returns 404 or 500 errors
- Dashboard loads but shows no data
- Dashboard is slow to respond

#### Diagnostic Steps

```bash
# 1. Check dashboard logs
tail -f logs/dashboard.log

# 2. Check if dashboard is running
ps aux | grep streamlit
netstat -tulpn | grep 8501

# 3. Check dashboard health
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/dashboard/health

# 4. Check database connectivity
python test_database_connection.py
```

#### Common Causes and Solutions

**A. Port Conflicts**

```bash
# Check what's using port 8501
lsof -i :8501

# Kill conflicting process
sudo kill -9 <PID>

# Restart dashboard
./restart_dashboard.py
```

**B. Database Issues**

```bash
# Check database file
ls -la output/degen_digest.db

# Test database connection
python test_database_connection.py

# Recreate database if corrupted
python recreate_db.py
```

**C. Configuration Issues**

```bash
# Check environment variables
env | grep -E "(DASHBOARD|STREAMLIT)"

# Check configuration file
cat config/app_config.yaml

# Validate configuration
python validate_config.py
```

#### Resolution Steps

```bash
# 1. Restart dashboard
./restart_dashboard.py

# 2. If that fails, redeploy dashboard
./deploy_farmchecker_cloud.sh

# 3. Verify dashboard is accessible
curl -I https://farmchecker.xyz

# 4. Check dashboard logs
tail -f logs/dashboard.log
```

### 3. Data Processing Errors

#### Symptoms

- No new digests generated
- Data quality warnings in logs
- Missing or corrupted data files

#### Diagnostic Steps

```bash
# 1. Check data processing logs
grep "DATA_PROCESSING" logs/degen_digest.log | tail -20

# 2. Check data quality
python test_data_quality.py

# 3. Check data files
ls -la output/
ls -la storage/

# 4. Check data pipeline
python test_enhanced_pipeline.py
```

#### Common Causes and Solutions

**A. Missing Data Files**

```bash
# Check if crawler data exists
ls -la output/crawler_data/

# If missing, trigger data collection
python manual_data_refresh.py

# Or restart crawler
./restart_crawler.sh
```

**B. Data Format Issues**

```bash
# Validate data format
python validate_data_format.py

# Fix data format issues
python fix_data_format.py

# Reprocess data
python enhanced_data_pipeline.py
```

**C. AI/ML Model Issues**

```bash
# Check AI API connectivity
python test_ai_options.py

# Test AI models
python test_ai_models.py

# If API issues, check API key
echo $OPENROUTER_API_KEY
```

#### Resolution Steps

```bash
# 1. Fix data sync issues
python fix_data_sync.py

# 2. Regenerate missing data
python manual_data_refresh.py

# 3. Reprocess data pipeline
python enhanced_data_pipeline.py

# 4. Verify data quality
python test_data_quality.py
```

### 4. Performance Issues

#### Symptoms

- Slow response times
- High CPU/memory usage
- Timeout errors
- Rate limiting errors

#### Diagnostic Steps

```bash
# 1. Check system performance
htop
iostat 1 5
netstat -i

# 2. Check application performance
python test_performance.py

# 3. Check API performance
python test_api.py

# 4. Check database performance
python test_database_performance.py
```

#### Common Causes and Solutions

**A. High CPU Usage**

```bash
# Identify high CPU processes
top -p 1

# Check for infinite loops
grep "loop" logs/degen_digest.log

# Restart problematic services
./restart_crawler.sh
./restart_dashboard.py
```

**B. Memory Issues**

```bash
# Check memory usage
free -h

# Check for memory leaks
python test_memory_usage.py

# Restart services to free memory
./restart_all_services.sh
```

**C. Network Issues**

```bash
# Check network connectivity
ping google.com
curl -I https://api.farmchecker.xyz

# Check DNS resolution
nslookup farmchecker.xyz

# Check firewall rules
iptables -L
```

#### Resolution Steps

```bash
# 1. Optimize performance
python optimize_performance.py

# 2. Scale up resources (if on Cloud Run)
gcloud run services update degen-digest-crawler --memory 2Gi
gcloud run services update degen-digest-dashboard --memory 2Gi

# 3. Implement caching
python setup_caching.py

# 4. Monitor performance
python monitor_performance.py
```

## Service-Specific Issues

### Crawler Service Issues

#### Twitter Crawler Problems

```bash
# Check Twitter crawler specifically
python test_solana_crawler.py

# Check Playwright setup
python test_playwright_crawler.py

# Check Twitter login
python test_twitter_login.py

# Common Twitter issues:
# - Rate limiting: Wait 15 minutes
# - Login failures: Check credentials
# - Network issues: Check connectivity
# - Browser issues: Reinstall Playwright
```

#### Reddit Crawler Problems

```bash
# Check Reddit crawler
python test_reddit_crawler.py

# Check RSS feeds
curl -I https://www.reddit.com/r/solana/.rss

# Common Reddit issues:
# - RSS feed changes: Update feed URLs
# - Rate limiting: Implement delays
# - Format changes: Update parser
```

#### Telegram Crawler Problems

```bash
# Check Telegram crawler
python test_telegram_crawler.py

# Check Telegram API
python test_telegram_api.py

# Common Telegram issues:
# - API key issues: Check credentials
# - Channel access: Verify permissions
# - Rate limiting: Implement delays
```

### Dashboard Service Issues

#### Streamlit Problems

```bash
# Check Streamlit installation
python -c "import streamlit; print(streamlit.__version__)"

# Check Streamlit configuration
streamlit config show

# Common Streamlit issues:
# - Port conflicts: Change port
# - Memory issues: Increase memory
# - Cache issues: Clear cache
```

#### Data Display Issues

```bash
# Check data loading
python test_data_loading.py

# Check chart rendering
python test_charts.py

# Common display issues:
# - Missing data: Check data pipeline
# - Format issues: Check data format
# - Cache issues: Clear browser cache
```

### API Service Issues

#### Authentication Problems

```bash
# Check API key
echo $DEGEN_API_KEY

# Test authentication
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/health

# Common auth issues:
# - Invalid API key: Check key format
# - Expired key: Rotate API key
# - Rate limiting: Check usage limits
```

#### Rate Limiting Issues

```bash
# Check rate limit status
curl -H "X-API-Key: your_api_key" https://api.farmchecker.xyz/v1/rate-limit

# Common rate limiting issues:
# - Too many requests: Implement delays
# - Burst requests: Implement queuing
# - API abuse: Check for loops
```

## Performance Issues

### Database Performance

```bash
# Check database performance
python test_database_performance.py

# Optimize database
python optimize_database.py

# Common database issues:
# - Slow queries: Add indexes
# - Connection pool: Increase pool size
# - Lock contention: Optimize transactions
```

### API Performance

```bash
# Check API performance
python test_api_performance.py

# Load test API
python load_test_api.py

# Common API issues:
# - Slow responses: Optimize queries
# - Memory leaks: Check for leaks
# - Connection issues: Check networking
```

### Crawler Performance

```bash
# Check crawler performance
python test_crawler_performance.py

# Optimize crawler
python optimize_crawler.py

# Common crawler issues:
# - Slow crawling: Optimize selectors
# - Memory usage: Implement pagination
# - Network issues: Add retries
```

## Data Issues

### Data Quality Problems

```bash
# Check data quality
python test_data_quality.py

# Fix data quality issues
python fix_data_quality.py

# Common data quality issues:
# - Missing fields: Check data source
# - Invalid formats: Update parsers
# - Duplicate data: Implement deduplication
```

### Data Sync Issues

```bash
# Check data sync
python test_data_sync.py

# Fix sync issues
python fix_data_sync.py

# Common sync issues:
# - Missing files: Check file paths
# - Permission issues: Check permissions
# - Network issues: Check connectivity
```

### Data Processing Errors

```bash
# Check data processing
python test_data_processing.py

# Fix processing errors
python fix_data_processing.py

# Common processing issues:
# - AI API errors: Check API key
# - Memory issues: Implement batching
# - Format errors: Update processors
```

## Security Issues

### Authentication Problems

```bash
# Check authentication
python test_authentication.py

# Fix auth issues
python fix_authentication.py

# Common auth issues:
# - Invalid tokens: Check token format
# - Expired tokens: Refresh tokens
# - Permission issues: Check roles
```

### Authorization Problems

```bash
# Check authorization
python test_authorization.py

# Fix auth issues
python fix_authorization.py

# Common auth issues:
# - Missing permissions: Grant permissions
# - Role issues: Update roles
# - Policy issues: Update policies
```

### Security Events

```bash
# Check security events
grep "SECURITY" logs/degen_digest.log | tail -20

# Investigate security events
python investigate_security_events.py

# Common security issues:
# - Failed logins: Check credentials
# - Suspicious activity: Block IPs
# - Data breaches: Audit access
```

## Emergency Procedures

### System Outage

#### Immediate Response

```bash
# 1. Check all services
./check_all_services.sh

# 2. Identify the issue
python diagnose_outage.py

# 3. Restart critical services
./emergency_restart.sh

# 4. Notify stakeholders
python notify_outage.py
```

#### Rollback Procedure

```bash
# 1. Identify previous working version
git log --oneline -10

# 2. Rollback to previous version
./rollback_deployment.sh

# 3. Verify rollback
./verify_deployment.py

# 4. Monitor system
./monitor_deployment.py
```

#### Communication Plan

1. **Update Status Page**

   ```bash
   python update_status_page.py --status=degraded
   ```

2. **Notify Team**

   ```bash
   python notify_team.py --urgency=high
   ```

3. **Document Incident**
   ```bash
   python document_incident.py
   ```

### Data Loss

#### Immediate Response

```bash
# 1. Stop data processing
./stop_data_processing.sh

# 2. Assess data loss
python assess_data_loss.py

# 3. Restore from backup
python restore_from_backup.py

# 4. Verify data integrity
python verify_data_integrity.py
```

#### Recovery Procedure

```bash
# 1. Restore database
python restore_database.py

# 2. Restore files
python restore_files.py

# 3. Reprocess data
python reprocess_data.py

# 4. Verify recovery
python verify_recovery.py
```

### Security Breach

#### Immediate Response

```bash
# 1. Isolate affected systems
./isolate_systems.sh

# 2. Assess breach scope
python assess_breach.py

# 3. Block suspicious IPs
python block_suspicious_ips.py

# 4. Rotate credentials
python rotate_credentials.py
```

#### Investigation Procedure

```bash
# 1. Collect evidence
python collect_evidence.py

# 2. Analyze logs
python analyze_security_logs.py

# 3. Identify root cause
python identify_root_cause.py

# 4. Document findings
python document_findings.py
```

## Debug Tools

### System Debugging

```bash
# Debug system issues
python debug_system.py

# Debug performance issues
python debug_performance.py

# Debug memory issues
python debug_memory.py

# Debug network issues
python debug_network.py
```

### Application Debugging

```bash
# Debug crawler
python debug_crawler.py

# Debug dashboard
python debug_dashboard.py

# Debug API
python debug_api.py

# Debug data processing
python debug_data_processing.py
```

### Data Debugging

```bash
# Debug data issues
python debug_data.py

# Debug digest generation
python debug_digests.py

# Debug data quality
python debug_data_quality.py

# Debug data sync
python debug_data_sync.py
```

## Log Analysis

### Log Search Patterns

```bash
# Search for errors
grep "ERROR" logs/degen_digest.log

# Search for warnings
grep "WARNING" logs/degen_digest.log

# Search for specific service
grep "CRAWLER" logs/degen_digest.log

# Search for specific user
grep "user_id=123" logs/degen_digest.log

# Search for specific time
grep "2025-01-03" logs/degen_digest.log
```

### Log Analysis Tools

```bash
# Analyze log patterns
python analyze_logs.py

# Generate log reports
python generate_log_report.py

# Monitor log trends
python monitor_log_trends.py

# Alert on log patterns
python alert_log_patterns.py
```

### Performance Log Analysis

```bash
# Analyze performance logs
python analyze_performance_logs.py

# Identify bottlenecks
python identify_bottlenecks.py

# Generate performance reports
python generate_performance_report.py

# Monitor performance trends
python monitor_performance_trends.py
```

## Recovery Procedures

### Service Recovery

```bash
# Recover crawler service
python recover_crawler.py

# Recover dashboard service
python recover_dashboard.py

# Recover API service
python recover_api.py

# Recover all services
python recover_all_services.py
```

### Data Recovery

```bash
# Recover database
python recover_database.py

# Recover files
python recover_files.py

# Recover configuration
python recover_configuration.py

# Recover all data
python recover_all_data.py
```

### Configuration Recovery

```bash
# Recover environment variables
python recover_environment.py

# Recover configuration files
python recover_config_files.py

# Recover API keys
python recover_api_keys.py

# Recover all configuration
python recover_all_configuration.py
```

---

## Quick Reference

### Emergency Contacts

- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **System Administrator**: admin@farmchecker.xyz
- **Security Team**: security@farmchecker.xyz

### Critical Commands

```bash
# Check system health
python test_current_status.py

# Restart all services
./restart_all_services.sh

# Rollback deployment
./rollback_deployment.sh

# Emergency restart
./emergency_restart.sh
```

### Log Locations

- **Main Log**: `logs/degen_digest.log`
- **Crawler Log**: `logs/crawler.log`
- **Dashboard Log**: `logs/dashboard.log`
- **API Log**: `logs/api.log`
- **Error Log**: `logs/error.log`

### Configuration Files

- **Environment**: `.env`
- **App Config**: `config/app_config.yaml`
- **Keywords**: `config/keywords.py`
- **Influencers**: `config/influencers.py`

---

**Last Updated**: 2025-01-03
**Version**: 2.0.0
**Maintainer**: DevOps Team
