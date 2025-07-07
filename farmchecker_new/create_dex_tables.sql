-- Create separate tables for DexScreener and DexPaprika data

-- DexScreener pairs table
CREATE TABLE IF NOT EXISTS dexscreener_pairs (
    id SERIAL PRIMARY KEY,
    pair_id VARCHAR(255) UNIQUE NOT NULL,
    base_token_symbol VARCHAR(50),
    base_token_name VARCHAR(255),
    base_token_address VARCHAR(255),
    quote_token_symbol VARCHAR(50),
    quote_token_name VARCHAR(255),
    quote_token_address VARCHAR(255),
    dex_name VARCHAR(100),
    chain_name VARCHAR(100),
    price_usd NUMERIC,
    price_change_24h NUMERIC,
    volume_24h NUMERIC,
    liquidity_usd NUMERIC,
    market_cap NUMERIC,
    txns_24h INTEGER,
    fdv NUMERIC,
    source VARCHAR(50) DEFAULT 'dexscreener',
    published_at TIMESTAMP,
    collected_at TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DexPaprika pairs table
CREATE TABLE IF NOT EXISTS dexpaprika_pairs (
    id SERIAL PRIMARY KEY,
    pair_id VARCHAR(255) UNIQUE NOT NULL,
    base_token_symbol VARCHAR(50),
    base_token_name VARCHAR(255),
    base_token_address VARCHAR(255),
    quote_token_symbol VARCHAR(50),
    quote_token_name VARCHAR(255),
    quote_token_address VARCHAR(255),
    dex_name VARCHAR(100),
    chain_name VARCHAR(100),
    price_usd NUMERIC,
    price_change_24h NUMERIC,
    volume_24h NUMERIC,
    liquidity_usd NUMERIC,
    market_cap NUMERIC,
    txns_24h INTEGER,
    fdv NUMERIC,
    source VARCHAR(50) DEFAULT 'dexpaprika',
    published_at TIMESTAMP,
    collected_at TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_symbol ON dexscreener_pairs(base_token_symbol);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_address ON dexscreener_pairs(base_token_address);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_chain ON dexscreener_pairs(chain_name);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_dex ON dexscreener_pairs(dex_name);

CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_symbol ON dexpaprika_pairs(base_token_symbol);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_address ON dexpaprika_pairs(base_token_address);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_chain ON dexpaprika_pairs(chain_name);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_dex ON dexpaprika_pairs(dex_name); 