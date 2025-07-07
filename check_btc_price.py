import psycopg2

conn = psycopg2.connect(
    host='34.9.71.174',
    database='degen_digest',
    user='postgres',
    password='DegenDigest2024!',
    port='5432'
)

cursor = conn.cursor()

# Check BTC data
cursor.execute("""
    SELECT symbol, name, price_usd, price_change_24h, last_updated_at, network 
    FROM crypto_tokens 
    WHERE symbol = 'BTC' 
    ORDER BY last_updated_at DESC 
    LIMIT 5
""")

rows = cursor.fetchall()
print('Latest BTC data in crypto_tokens table:')
for row in rows:
    symbol, name, price, change, updated, network = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Updated: {updated}')

# Check all recent crypto data
cursor.execute("""
    SELECT symbol, name, price_usd, price_change_24h, last_updated_at, network 
    FROM crypto_tokens 
    WHERE last_updated_at >= NOW() - INTERVAL '1 hour'
    ORDER BY last_updated_at DESC 
    LIMIT 10
""")

rows = cursor.fetchall()
print('\nAll recent crypto data (last hour):')
for row in rows:
    symbol, name, price, change, updated, network = row
    print(f'{symbol} ({network}): ${price:,.2f} ({change:+.2f}%) - Updated: {updated}')

cursor.close()
conn.close() 