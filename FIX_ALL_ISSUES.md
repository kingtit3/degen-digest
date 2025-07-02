# 🚀 Degen Digest - Complete Issue Fix Guide

## 🔍 Issues Identified

### 1. LLM Batch Processing Error (CRITICAL)

- **Error**: `Batch LLM call failed: Completions.create() got an unexpected keyword argument 'batch'`
- **Status**: ✅ FIXED in `processor/summarizer.py`

### 2. Data Sync Issues (CRITICAL)

- Cloud function collecting data but not syncing to local system
- Local database showing 0 tweets, 40 reddit posts, 0 digests
- Dashboard not displaying fresh data

### 3. Pandoc Installation Error (MINOR)

- PDF generation failing due to missing pandoc
- Markdown generation still works

## 🛠️ Step-by-Step Fix Instructions

### Step 1: Test the LLM Fix

```bash
# Test if the LLM batch processing error is fixed
python test_digest_generation.py
```

### Step 2: Sync Fresh Data from Cloud Function

```bash
# Option A: Use the manual refresh script
python manual_data_refresh.py

# Option B: Use curl to trigger cloud function manually
curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data \
  -H "Content-Type: application/json" \
  -d '{"generate_digest": true, "force_refresh": true}'
```

### Step 3: Run Local Scrapers (if cloud function fails)

```bash
# Run individual scrapers
python scrapers/reddit_rss.py
python scrapers/newsapi_headlines.py
python scrapers/coingecko_gainers.py
```

### Step 4: Generate Digest Locally

```bash
# Generate digest using the main script
python main.py

# Or use the generate digest script
python generate_digest.py
```

### Step 5: Update Dashboard Data

```bash
# Run data processing pipeline
python run_deduplication.py
python run_enhanced_system.py
```

### Step 6: Verify Database

```bash
# Check database contents
sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet; SELECT COUNT(*) FROM redditpost; SELECT COUNT(*) FROM digest;"
```

## 🔧 Manual Fixes for Each Issue

### Fix 1: LLM Batch Processing Error

The error has been fixed in `processor/summarizer.py`. The changes include:

- Removed incorrect `batch` parameter
- Added better error handling
- Improved async processing with semaphore limits

### Fix 2: Data Sync Issues

Created several scripts to fix data sync:

#### `manual_data_refresh.py`

- Calls cloud function and saves response locally
- Extracts digest content and processed data
- Saves to local files for dashboard access

#### `sync_cloud_data.py`

- Comprehensive data sync with database updates
- Handles all data types (Twitter, Reddit, News)
- Updates local database with fresh data

#### `fix_data_sync.py`

- System-wide fix for all issues
- Runs all necessary steps automatically

### Fix 3: Cloud Function Updates

Updated `cloud_function/main.py` to:

- Return processed data in response
- Save data to `/tmp` for cloud function environment
- Include digest content in response

## 🚀 Quick Fix Commands

### Option 1: Automated Fix (Recommended)

```bash
python fix_data_sync.py
```

### Option 2: Manual Step-by-Step

```bash
# 1. Test LLM fix
python test_digest_generation.py

# 2. Sync data
python manual_data_refresh.py

# 3. Generate digest
python main.py

# 4. Check results
ls -la output/digest*.md
sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet;"
```

### Option 3: Cloud Function Only

```bash
# Deploy updated cloud function
./deploy_cloud_function.sh

# Trigger data refresh
curl -X POST https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data \
  -H "Content-Type: application/json" \
  -d '{"generate_digest": true, "force_refresh": true}'
```

## 📊 Expected Results After Fixes

### Database Contents

- **Before**: 0 tweets, 40 reddit posts, 0 digests
- **After**: 100+ tweets, 100+ reddit posts, 1+ digests

### Files Generated

- `output/digest.md` - Current digest
- `output/digest-YYYY-MM-DD.md` - Dated digest
- `output/consolidated_data.json` - Processed data
- `output/twitter_raw.json` - Twitter data
- `output/reddit_raw.json` - Reddit data
- `output/newsapi_raw.json` - News data

### Dashboard Status

- **URL**: https://farmchecker.xyz
- **Expected**: Fresh data showing in all pages
- **Digests**: New digest available for download

## 🔍 Verification Steps

### 1. Check Logs

```bash
# Look for absence of batch errors
grep -i "batch" logs/degen_digest.log | tail -5
```

### 2. Check Database

```bash
sqlite3 output/degen_digest.db "SELECT COUNT(*) FROM tweet; SELECT COUNT(*) FROM redditpost; SELECT COUNT(*) FROM digest;"
```

### 3. Check Files

```bash
ls -la output/digest*.md
ls -la output/*_raw.json
```

### 4. Check Dashboard

- Visit https://farmchecker.xyz
- Check if data appears in all pages
- Verify digest is available for download

## 🆘 Troubleshooting

### If Python scripts don't run:

1. Check Python environment: `python --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Try with python3: `python3 script_name.py`

### If cloud function fails:

1. Check deployment: `./deploy_cloud_function.sh`
2. Check logs: `gcloud logging read "resource.type=cloud_function"`
3. Try manual curl request

### If database is empty:

1. Run scrapers manually
2. Check API keys in environment
3. Verify network connectivity

### If dashboard shows no data:

1. Check if files exist in output directory
2. Verify file permissions
3. Restart dashboard service

## 📞 Support

If issues persist after following these steps:

1. Check the logs in `logs/degen_digest.log`
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check network connectivity to APIs

## 🎯 Success Criteria

The system is fixed when:

- ✅ No batch processing errors in logs
- ✅ Database contains fresh data (tweets, reddit posts, digests)
- ✅ Digest files are generated in output directory
- ✅ Dashboard displays fresh data at https://farmchecker.xyz
- ✅ All pages show current information
