import psycopg2

conn = psycopg2.connect(
    host='34.9.71.174',
    database='degen_digest',
    user='postgres',
    password='DegenDigest2024!',
    port='5432'
)

cursor = conn.cursor()

# Test the updated query the API uses
cursor.execute("""
    SELECT DISTINCT ON (symbol) id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
           network, contract_address, last_updated_at
    FROM crypto_tokens 
    WHERE price_change_24h > 0 
    AND price_usd > 0
    AND last_updated_at >= NOW() - INTERVAL '24 hours'
    ORDER BY symbol, last_updated_at DESC, price_change_24h DESC
    LIMIT 20
""")

rows = cursor.fetchall()
print('Updated API Query Results (Top Gainers):')
print('=' * 80)
for row in rows:
    id_val, symbol, name, price, change, market_cap, volume, network, contract, updated = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Updated: {updated}')

print(f'\nTotal results: {len(rows)}')

# Test updated trending query
cursor.execute("""
    SELECT DISTINCT ON (symbol) id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
           network, contract_address, last_updated_at
    FROM crypto_tokens 
    WHERE volume_24h > 0 
    AND price_usd > 0
    AND last_updated_at >= NOW() - INTERVAL '24 hours'
    ORDER BY symbol, last_updated_at DESC, volume_24h DESC
    LIMIT 20
""")

rows = cursor.fetchall()
print('\nUpdated API Query Results (Trending):')
print('=' * 80)
for row in rows:
    id_val, symbol, name, price, change, market_cap, volume, network, contract, updated = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Vol: ${volume:,.0f} - Updated: {updated}')

print(f'\nTotal results: {len(rows)}')

cursor.close()
conn.close() 