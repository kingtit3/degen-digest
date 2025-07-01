# Google Cloud Storage Setup Guide

## 🎯 Project Configuration

**Project ID**: `lucky-union-463615-t3`  
**Bucket Name**: `degen-digest-data`  
**Region**: Default (us-central1)

## 🔧 Setup Steps

### 1. Authentication Setup

First, ensure you're authenticated with Google Cloud:

```bash
# Check current authentication
gcloud auth list

# If not authenticated, run:
gcloud auth application-default login

# Set the project
gcloud config set project lucky-union-463615-t3

# Verify project is set
gcloud config get-value project
```

### 2. Enable Required APIs

Enable the Cloud Storage API:

```bash
gcloud services enable storage.googleapis.com
```

### 3. Test Setup

Run the test script to verify everything is working:

```bash
python test_cloud_setup.py
```

This will:
- ✅ Test Google Cloud Storage imports
- ✅ Verify authentication
- ✅ Check bucket access
- ✅ List existing files (if any)
- ✅ Test local data files

## 🚀 Usage Commands

### List Cloud Files
```bash
python scripts/cloud_storage_sync.py --list
```

### Upload All Data to Cloud
```bash
python scripts/cloud_storage_sync.py --direction upload
```

### Download All Data from Cloud
```bash
python scripts/cloud_storage_sync.py --direction download
```

### Create Database Backup
```bash
python scripts/cloud_storage_sync.py --backup
```

### Restore Database from Backup
```bash
python scripts/cloud_storage_sync.py --restore 20250630_154312
```

### Bidirectional Sync (Upload + Download)
```bash
python scripts/cloud_storage_sync.py --direction both
```

## 📁 Cloud Storage Structure

The data will be organized in the cloud bucket as follows:

```
degen-digest-data/
├── data/
│   ├── twitter_raw.json
│   ├── reddit_raw.json
│   ├── telegram_raw.json
│   ├── newsapi_raw.json
│   ├── coingecko_raw.json
│   ├── enhanced_twitter_data.json
│   ├── health_metrics.json
│   ├── health_alerts.json
│   └── consolidated_data.json
├── database/
│   └── degen_digest.db
├── enhanced_pipeline/
│   ├── viral_predictions.json
│   ├── processed_data.json
│   ├── summary_report.json
│   ├── trends_analysis.json
│   └── pipeline_stats.json
└── backups/
    └── degen_digest_YYYYMMDD_HHMMSS.db
```

## 🔍 Dashboard Integration

The Data Sync dashboard page provides:

1. **Visual Data Overview**: Charts showing data distribution
2. **Sync Status**: Real-time file status monitoring
3. **One-Click Operations**: Buttons for merge, upload, download
4. **Analytics**: Enhanced viral predictions and trends
5. **Export Tools**: Download data as JSON or CSV

Access via: `http://localhost:8501` → "Data Sync" page

## 🛠️ Troubleshooting

### Authentication Issues
```bash
# Re-authenticate
gcloud auth application-default login

# Check credentials
gcloud auth list
```

### Permission Issues
```bash
# Check if you have storage admin role
gcloud projects get-iam-policy lucky-union-463615-t3
```

### Bucket Creation Issues
```bash
# Create bucket manually
gsutil mb gs://degen-digest-data

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://degen-digest-data
```

### Import Errors
```bash
# Reinstall Google Cloud Storage
pip install --upgrade google-cloud-storage
```

## 📊 Data Sync Workflow

### Daily Workflow
1. **Run Scrapers**: Collect fresh data
2. **Merge Data**: `python scripts/merge_local_cloud_data.py`
3. **Upload to Cloud**: `python scripts/cloud_storage_sync.py --direction upload`
4. **Check Dashboard**: Verify data in Data Sync page

### Recovery Workflow
1. **Download from Cloud**: `python scripts/cloud_storage_sync.py --direction download`
2. **Verify Data**: Check file integrity
3. **Restore if Needed**: Use backup restoration

## 🔐 Security Considerations

- **Access Control**: Bucket is private by default
- **Backup Strategy**: Database backups stored in cloud
- **Data Encryption**: All data encrypted at rest
- **Audit Logging**: Access logs available in Cloud Console

## 📈 Monitoring

### Cloud Console Monitoring
- Go to: https://console.cloud.google.com/storage/browser
- Select bucket: `degen-digest-data`
- Monitor usage, access patterns, and costs

### Local Monitoring
- Check `output/merge_report.json` for sync status
- Use Data Sync dashboard for real-time monitoring
- Review logs in `logs/degen_digest.log`

## 🎉 Success Indicators

✅ **Authentication**: `gcloud auth list` shows active account  
✅ **Project Access**: `gcloud config get-value project` returns correct ID  
✅ **Bucket Access**: `gsutil ls gs://degen-digest-data` works  
✅ **Data Sync**: Files upload/download successfully  
✅ **Dashboard**: Data Sync page shows all data  

---

*Setup completed for project: lucky-union-463615-t3* 