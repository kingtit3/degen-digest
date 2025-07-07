import psycopg2

conn = psycopg2.connect(
    host='34.9.71.174',
    database='degen_digest',
    user='postgres',
    password='DegenDigest2024!',
    port='5432'
)

cursor = conn.cursor()

# Test the exact query the API uses
cursor.execute("""
    SELECT id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
           network, contract_address, last_updated_at
    FROM crypto_tokens 
    WHERE price_change_24h > 0 
    AND price_usd > 0
    AND last_updated_at >= NOW() - INTERVAL '24 hours'
    ORDER BY price_change_24h DESC 
    LIMIT 20
""")

rows = cursor.fetchall()
print('API Query Results (Top Gainers):')
print('=' * 80)
for row in rows:
    id_val, symbol, name, price, change, market_cap, volume, network, contract, updated = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Updated: {updated}')

print(f'\nTotal results: {len(rows)}')

# Test trending query
cursor.execute("""
    SELECT id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
           network, contract_address, last_updated_at
    FROM crypto_tokens 
    WHERE volume_24h > 0 
    AND price_usd > 0
    AND last_updated_at >= NOW() - INTERVAL '24 hours'
    ORDER BY volume_24h DESC, last_updated_at DESC
    LIMIT 20
""")

rows = cursor.fetchall()
print('\nAPI Query Results (Trending):')
print('=' * 80)
for row in rows:
    id_val, symbol, name, price, change, market_cap, volume, network, contract, updated = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Vol: ${volume:,.0f} - Updated: {updated}')

print(f'\nTotal results: {len(rows)}')

cursor.close()
conn.close() 