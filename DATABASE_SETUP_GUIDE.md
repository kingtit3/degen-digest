# Database Setup Guide for DegenDigest

## Quick Start

### Option 1: Local PostgreSQL (Recommended for Development)

1. **Install PostgreSQL locally:**

   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql

   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create database:**

   ```bash
   createdb degen_digest
   ```

3. **Install Python dependencies:**

   ```bash
   pip install psycopg2-binary google-cloud-storage
   ```

4. **Set environment variables:**

   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=degen_digest
   export DB_USER=your_username
   export DB_PASSWORD=your_password
   ```

5. **Run migration:**
   ```bash
   python3 scripts/setup_database.py
   ```

### Option 2: Cloud SQL (Recommended for Production)

1. **Create Cloud SQL instance:**

   ```bash
   gcloud sql instances create degen-digest-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --root-password=your_secure_password
   ```

2. **Create database:**

   ```bash
   gcloud sql databases create degen_digest --instance=degen-digest-db
   ```

3. **Get connection info:**

   ```bash
   gcloud sql instances describe degen-digest-db
   ```

4. **Set environment variables:**

   ```bash
   export DB_HOST=<INSTANCE_IP>
   export DB_PORT=5432
   export DB_NAME=degen_digest
   export DB_USER=postgres
   export DB_PASSWORD=your_secure_password
   ```

5. **Run migration:**
   ```bash
   python3 scripts/setup_database.py
   ```

## Verification

After migration, verify the setup:

```bash
# Connect to database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM content_items;
SELECT COUNT(*) FROM data_collections;
SELECT name, COUNT(*) FROM data_sources GROUP BY name;
```

## Expected Results

After successful migration, you should see:

- **6-7 data sources** (twitter, reddit, news, crypto, etc.)
- **Multiple collections** (one per consolidated file)
- **Thousands of content items** (depending on your data volume)

## Troubleshooting

### Common Issues

1. **Connection refused:**

   - Check if PostgreSQL is running
   - Verify host/port settings
   - Check firewall rules

2. **Authentication failed:**

   - Verify username/password
   - Check pg_hba.conf for local connections

3. **Permission denied:**
   - Ensure user has CREATE privileges
   - Check database ownership

### Debug Mode

Run with verbose logging:

```bash
export PYTHONPATH=/Users/king/DegenDigest
python3 -u scripts/setup_database.py
```

## Next Steps

After successful migration:

1. **Update crawlers** to write to both GCS and SQL
2. **Modify dashboard** to query SQL database
3. **Add indexes** for performance optimization
4. **Set up monitoring** and alerts

## Cost Estimation

- **Local PostgreSQL**: Free
- **Cloud SQL (db-f1-micro)**: ~$7/month
- **Cloud SQL (db-g1-small)**: ~$25/month (recommended for production)

## Benefits Achieved

✅ **Faster queries** (sub-second vs minutes)
✅ **Advanced analytics** (trends, correlations)
✅ **Data relationships** (cross-source analysis)
✅ **Scalability** (handles millions of records)
✅ **Data integrity** (ACID compliance)
