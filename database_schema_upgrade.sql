-- Database Schema Upgrade for Crypto Token Data
-- This adds a dedicated table for crypto token information

-- Create crypto_tokens table
CREATE TABLE IF NOT EXISTS crypto_tokens (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price_usd DECIMAL(20, 8),
    price_change_24h DECIMAL(10, 4),
    price_change_percentage_24h DECIMAL(10, 4),
    market_cap_usd DECIMAL(30, 2),
    volume_24h_usd DECIMAL(30, 2),
    rank INTEGER,
    image_url TEXT,
    source VARCHAR(50) NOT NULL, -- 'coingecko', 'dexpaprika', 'dexscreener'
    external_id VARCHAR(100), -- ID from the source API
    raw_data JSONB, -- Keep original data for reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    UNIQUE(symbol, source, external_id),
    INDEX idx_crypto_tokens_symbol (symbol),
    INDEX idx_crypto_tokens_source (source),
    INDEX idx_crypto_tokens_rank (rank),
    INDEX idx_crypto_tokens_updated_at (updated_at)
);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_crypto_tokens_updated_at 
    BEFORE UPDATE ON crypto_tokens 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add a view for easy querying of latest token data
CREATE OR REPLACE VIEW latest_crypto_tokens AS
SELECT DISTINCT ON (symbol, source) 
    id, symbol, name, price_usd, price_change_24h, price_change_percentage_24h,
    market_cap_usd, volume_24h_usd, rank, image_url, source, external_id,
    raw_data, created_at, updated_at
FROM crypto_tokens 
ORDER BY symbol, source, updated_at DESC;

-- Add function to upsert crypto token data
CREATE OR REPLACE FUNCTION upsert_crypto_token(
    p_symbol VARCHAR(20),
    p_name VARCHAR(100),
    p_price_usd DECIMAL(20, 8),
    p_price_change_24h DECIMAL(10, 4),
    p_price_change_percentage_24h DECIMAL(10, 4),
    p_market_cap_usd DECIMAL(30, 2),
    p_volume_24h_usd DECIMAL(30, 2),
    p_rank INTEGER,
    p_image_url TEXT,
    p_source VARCHAR(50),
    p_external_id VARCHAR(100),
    p_raw_data JSONB
) RETURNS INTEGER AS $$
DECLARE
    token_id INTEGER;
BEGIN
    INSERT INTO crypto_tokens (
        symbol, name, price_usd, price_change_24h, price_change_percentage_24h,
        market_cap_usd, volume_24h_usd, rank, image_url, source, external_id, raw_data
    ) VALUES (
        p_symbol, p_name, p_price_usd, p_price_change_24h, p_price_change_percentage_24h,
        p_market_cap_usd, p_volume_24h_usd, p_rank, p_image_url, p_source, p_external_id, p_raw_data
    )
    ON CONFLICT (symbol, source, external_id) 
    DO UPDATE SET
        name = EXCLUDED.name,
        price_usd = EXCLUDED.price_usd,
        price_change_24h = EXCLUDED.price_change_24h,
        price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
        market_cap_usd = EXCLUDED.market_cap_usd,
        volume_24h_usd = EXCLUDED.volume_24h_usd,
        rank = EXCLUDED.rank,
        image_url = EXCLUDED.image_url,
        raw_data = EXCLUDED.raw_data,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id INTO token_id;
    
    RETURN token_id;
END;
$$ LANGUAGE plpgsql; 