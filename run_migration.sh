#!/bin/bash

echo "🚀 Running Data Migration"
echo "========================"

# Check if we're in the right directory
if [ ! -f "migrate_data.py" ]; then
    echo "❌ Error: migrate_data.py not found. Please run this from the DegenDigest directory."
    exit 1
fi

# Run the migration
echo "📊 Starting migration..."
python3 migrate_data.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "🔍 To check the results, run:"
    echo "PGPASSWORD='DegenDigest2024!' psql -h 34.9.71.174 -U postgres -d degen_digest -c \"SELECT ds.name, COUNT(*) as item_count FROM data_sources ds LEFT JOIN content_items ci ON ds.id = ci.source_id GROUP BY ds.name ORDER BY item_count DESC;\""
else
    echo ""
    echo "❌ Migration failed!"
    exit 1
fi
