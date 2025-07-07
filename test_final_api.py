import requests
import json

# Test the API endpoints
urls = [
    "https://farmchecker.xyz/api/crypto/top-gainers",
    "https://farmchecker-website-128671663649.us-central1.run.app/api/crypto/top-gainers"
]

for url in urls:
    try:
        print(f"\nTesting: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code}")
            print("Top 3 results:")
            for i, item in enumerate(data[:3]):
                print(f"  {i+1}. {item.get('symbol')}: {item.get('price')} ({item.get('price_change_24h')})")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Also test the database directly
print("\n" + "="*50)
print("Database Direct Query Results:")
print("="*50)

import psycopg2

conn = psycopg2.connect(
    host='34.9.71.174',
    database='degen_digest',
    user='postgres',
    password='DegenDigest2024!',
    port='5432'
)

cursor = conn.cursor()

# Test the final query
cursor.execute("""
    SELECT DISTINCT ON (symbol) symbol, name, price_usd, price_change_24h, network, last_updated_at
    FROM crypto_tokens 
    WHERE price_change_24h > 0 
    AND price_usd > 0
    AND last_updated_at >= NOW() - INTERVAL '24 hours'
    ORDER BY symbol, last_updated_at DESC, price_change_24h DESC
    LIMIT 10
""")

rows = cursor.fetchall()
for row in rows:
    symbol, name, price, change, network, updated = row
    print(f"{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - {updated}")

cursor.close()
conn.close() 