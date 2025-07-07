-- Create dedicated tables for each crawler type
-- This provides better data structure and easier migration from buckets

-- ========================================
-- TWITTER CRAWLER TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE NOT NULL,  -- Twitter's original ID
    author_username VARCHAR(255) NOT NULL,
    author_display_name VARCHAR(255),
    author_verified BOOLEAN DEFAULT FALSE,
    author_followers_count INTEGER DEFAULT 0,
    content TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Engagement metrics
    likes_count INTEGER DEFAULT 0,
    retweets_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    
    -- Analysis scores
    engagement_score DECIMAL(10,4) DEFAULT 0,
    virality_score DECIMAL(10,4) DEFAULT 0,
    sentiment_score DECIMAL(5,4) DEFAULT 0,
    
    -- Viral analysis
    viral_keywords JSONB,  -- Array of viral keywords found
    category VARCHAR(100), -- memecoin, launchpad, airdrop, farming, etc.
    urgency VARCHAR(50),   -- high, medium, low
    
    -- Raw data from Twitter
    raw_data JSONB,
    
    -- Indexes for performance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- REDDIT CRAWLER TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS reddit_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE NOT NULL,  -- Reddit's original ID
    subreddit VARCHAR(255) NOT NULL,
    author_username VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    is_original_content BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Engagement metrics
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    
    -- Analysis scores
    engagement_score DECIMAL(10,4) DEFAULT 0,
    virality_score DECIMAL(10,4) DEFAULT 0,
    sentiment_score DECIMAL(5,4) DEFAULT 0,
    
    -- Viral analysis
    viral_keywords JSONB,  -- Array of viral keywords found
    category VARCHAR(100), -- memecoin, launchpad, airdrop, farming, etc.
    urgency VARCHAR(50),   -- high, medium, low
    
    -- Raw data from Reddit
    raw_data JSONB,
    
    -- Indexes for performance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- NEWS CRAWLER TABLE (Enhanced)
-- ========================================
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Search query that found this article
    query TEXT,
    source_type VARCHAR(50) DEFAULT 'news',
    
    -- Analysis scores
    engagement_score DECIMAL(10,4) DEFAULT 0,
    virality_score DECIMAL(10,4) DEFAULT 0,
    sentiment_score DECIMAL(5,4) DEFAULT 0,
    
    -- Viral analysis
    viral_keywords JSONB,
    sentiment VARCHAR(50),
    urgency VARCHAR(50),
    category VARCHAR(100),
    
    -- Additional metadata
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10),
    api_source VARCHAR(50) DEFAULT 'newsapi.org',
    
    -- Raw data
    raw_data JSONB,
    
    -- Indexes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- CRYPTO CRAWLER TABLES
-- ========================================

-- CoinGecko tokens
CREATE TABLE IF NOT EXISTS coingecko_tokens (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    price_usd DECIMAL(20,8),
    price_change_24h DECIMAL(10,4),
    price_change_percentage_24h DECIMAL(10,4),
    market_cap DECIMAL(20,2),
    volume_24h DECIMAL(20,2),
    rank INTEGER,
    image_url TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional data
    circulating_supply DECIMAL(20,2),
    total_supply DECIMAL(20,2),
    max_supply DECIMAL(20,2),
    ath DECIMAL(20,8),
    ath_change_percentage DECIMAL(10,4),
    atl DECIMAL(20,8),
    atl_change_percentage DECIMAL(10,4),
    
    -- Raw data
    raw_data JSONB,
    
    -- Indexes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DexScreener pairs
CREATE TABLE IF NOT EXISTS dexscreener_pairs (
    id SERIAL PRIMARY KEY,
    pair_id VARCHAR(255) UNIQUE NOT NULL,
    chain_id VARCHAR(50) NOT NULL,
    dex_id VARCHAR(100) NOT NULL,
    pair_address VARCHAR(255),
    base_token_symbol VARCHAR(20) NOT NULL,
    base_token_name VARCHAR(100),
    base_token_address VARCHAR(255),
    quote_token_symbol VARCHAR(20) NOT NULL,
    quote_token_name VARCHAR(100),
    quote_token_address VARCHAR(255),
    
    -- Price data
    price_usd DECIMAL(20,8),
    price_change_24h DECIMAL(10,4),
    volume_24h DECIMAL(20,2),
    liquidity_usd DECIMAL(20,2),
    fdv DECIMAL(20,2),
    
    -- Additional metrics
    txns_24h INTEGER DEFAULT 0,
    buys_24h INTEGER DEFAULT 0,
    sells_24h INTEGER DEFAULT 0,
    
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Raw data
    raw_data JSONB,
    
    -- Indexes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DexPaprika pairs
CREATE TABLE IF NOT EXISTS dexpaprika_pairs (
    id SERIAL PRIMARY KEY,
    pair_id VARCHAR(255) UNIQUE NOT NULL,
    chain_id VARCHAR(50) NOT NULL,
    dex_id VARCHAR(100) NOT NULL,
    pair_address VARCHAR(255),
    base_token_symbol VARCHAR(20) NOT NULL,
    base_token_name VARCHAR(100),
    base_token_address VARCHAR(255),
    quote_token_symbol VARCHAR(20) NOT NULL,
    quote_token_name VARCHAR(100),
    quote_token_address VARCHAR(255),
    
    -- Price data
    price_usd DECIMAL(20,8),
    price_change_24h DECIMAL(10,4),
    volume_24h DECIMAL(20,2),
    liquidity_usd DECIMAL(20,2),
    
    -- Additional metrics
    txns_24h INTEGER DEFAULT 0,
    market_cap DECIMAL(20,2),
    
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Raw data
    raw_data JSONB,
    
    -- Indexes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- CREATE INDEXES FOR PERFORMANCE
-- ========================================

-- Twitter indexes
CREATE INDEX IF NOT EXISTS idx_tweets_tweet_id ON tweets(tweet_id);
CREATE INDEX IF NOT EXISTS idx_tweets_author_username ON tweets(author_username);
CREATE INDEX IF NOT EXISTS idx_tweets_published_at ON tweets(published_at);
CREATE INDEX IF NOT EXISTS idx_tweets_engagement_score ON tweets(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_tweets_virality_score ON tweets(virality_score DESC);
CREATE INDEX IF NOT EXISTS idx_tweets_category ON tweets(category);
CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at);

-- Reddit indexes
CREATE INDEX IF NOT EXISTS idx_reddit_posts_post_id ON reddit_posts(post_id);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_subreddit ON reddit_posts(subreddit);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_author_username ON reddit_posts(author_username);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_published_at ON reddit_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_engagement_score ON reddit_posts(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_virality_score ON reddit_posts(virality_score DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_category ON reddit_posts(category);
CREATE INDEX IF NOT EXISTS idx_reddit_posts_created_at ON reddit_posts(created_at);

-- News indexes
CREATE INDEX IF NOT EXISTS idx_news_articles_url ON news_articles(url);
CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source_name);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_engagement_score ON news_articles(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_news_articles_collected_at ON news_articles(collected_at);

-- Crypto indexes
CREATE INDEX IF NOT EXISTS idx_coingecko_tokens_symbol ON coingecko_tokens(symbol);
CREATE INDEX IF NOT EXISTS idx_coingecko_tokens_rank ON coingecko_tokens(rank);
CREATE INDEX IF NOT EXISTS idx_coingecko_tokens_price_change ON coingecko_tokens(price_change_percentage_24h DESC);
CREATE INDEX IF NOT EXISTS idx_coingecko_tokens_collected_at ON coingecko_tokens(collected_at);

CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_pair_id ON dexscreener_pairs(pair_id);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_chain ON dexscreener_pairs(chain_id);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_base_symbol ON dexscreener_pairs(base_token_symbol);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_volume ON dexscreener_pairs(volume_24h DESC);
CREATE INDEX IF NOT EXISTS idx_dexscreener_pairs_collected_at ON dexscreener_pairs(collected_at);

CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_pair_id ON dexpaprika_pairs(pair_id);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_chain ON dexpaprika_pairs(chain_id);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_base_symbol ON dexpaprika_pairs(base_token_symbol);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_volume ON dexpaprika_pairs(volume_24h DESC);
CREATE INDEX IF NOT EXISTS idx_dexpaprika_pairs_collected_at ON dexpaprika_pairs(collected_at);

-- ========================================
-- UPDATE TRIGGERS
-- ========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_tweets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_reddit_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE FUNCTION update_dex_pairs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_tweets_updated_at 
    BEFORE UPDATE ON tweets 
    FOR EACH ROW 
    EXECUTE FUNCTION update_tweets_updated_at();

CREATE TRIGGER update_reddit_posts_updated_at 
    BEFORE UPDATE ON reddit_posts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_reddit_posts_updated_at();

CREATE TRIGGER update_news_articles_updated_at 
    BEFORE UPDATE ON news_articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_tweets_updated_at();

CREATE TRIGGER update_coingecko_tokens_updated_at 
    BEFORE UPDATE ON coingecko_tokens 
    FOR EACH ROW 
    EXECUTE FUNCTION update_tweets_updated_at();

CREATE TRIGGER update_dexscreener_pairs_updated_at 
    BEFORE UPDATE ON dexscreener_pairs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_dex_pairs_updated_at();

CREATE TRIGGER update_dexpaprika_pairs_updated_at 
    BEFORE UPDATE ON dexpaprika_pairs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_dex_pairs_updated_at();

-- ========================================
-- COMMENTS FOR DOCUMENTATION
-- ========================================

COMMENT ON TABLE tweets IS 'Dedicated table for Twitter tweets with engagement metrics and viral analysis';
COMMENT ON TABLE reddit_posts IS 'Dedicated table for Reddit posts with engagement metrics and viral analysis';
COMMENT ON TABLE news_articles IS 'Dedicated table for news articles with rich metadata and analysis';
COMMENT ON TABLE coingecko_tokens IS 'Dedicated table for CoinGecko cryptocurrency data';
COMMENT ON TABLE dexscreener_pairs IS 'Dedicated table for DexScreener DEX trading pairs';
COMMENT ON TABLE dexpaprika_pairs IS 'Dedicated table for DexPaprika DEX trading pairs';

-- ========================================
-- MIGRATION HELPER FUNCTIONS
-- ========================================

-- Function to migrate data from content_items to dedicated tables
CREATE OR REPLACE FUNCTION migrate_to_dedicated_tables()
RETURNS INTEGER AS $$
DECLARE
    migrated_count INTEGER := 0;
    item RECORD;
BEGIN
    -- Migrate Twitter posts
    FOR item IN 
        SELECT ci.*, ds.name as source_name
        FROM content_items ci
        JOIN data_sources ds ON ci.source_id = ds.id
        WHERE ds.name = 'twitter'
    LOOP
        BEGIN
            INSERT INTO tweets (
                tweet_id, author_username, content, url, published_at,
                engagement_score, virality_score, sentiment_score, raw_data
            ) VALUES (
                item.external_id, item.author, item.content, item.url, item.published_at,
                item.engagement_score, item.virality_score, item.sentiment_score, item.raw_data
            ) ON CONFLICT (tweet_id) DO NOTHING;
            
            migrated_count := migrated_count + 1;
        EXCEPTION WHEN OTHERS THEN
            -- Log error but continue
            RAISE NOTICE 'Error migrating Twitter post %: %', item.external_id, SQLERRM;
        END;
    END LOOP;
    
    -- Migrate Reddit posts
    FOR item IN 
        SELECT ci.*, ds.name as source_name
        FROM content_items ci
        JOIN data_sources ds ON ci.source_id = ds.id
        WHERE ds.name = 'reddit'
    LOOP
        BEGIN
            INSERT INTO reddit_posts (
                post_id, subreddit, author_username, title, content, url, published_at,
                engagement_score, virality_score, sentiment_score, raw_data
            ) VALUES (
                item.external_id, 
                COALESCE((item.raw_data->>'subreddit'), 'unknown'),
                item.author, item.title, item.content, item.url, item.published_at,
                item.engagement_score, item.virality_score, item.sentiment_score, item.raw_data
            ) ON CONFLICT (post_id) DO NOTHING;
            
            migrated_count := migrated_count + 1;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error migrating Reddit post %: %', item.external_id, SQLERRM;
        END;
    END LOOP;
    
    -- Migrate News articles
    FOR item IN 
        SELECT ci.*, ds.name as source_name
        FROM content_items ci
        JOIN data_sources ds ON ci.source_id = ds.id
        WHERE ds.name = 'news'
    LOOP
        BEGIN
            INSERT INTO news_articles (
                title, description, content, url, source_name, author, published_at,
                engagement_score, virality_score, sentiment_score, raw_data
            ) VALUES (
                item.title, NULL, item.content, item.url, 
                COALESCE((item.raw_data->>'source'), 'unknown'),
                item.author, item.published_at,
                item.engagement_score, item.virality_score, item.sentiment_score, item.raw_data
            ) ON CONFLICT (url) DO NOTHING;
            
            migrated_count := migrated_count + 1;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error migrating news article %: %', item.url, SQLERRM;
        END;
    END LOOP;
    
    RETURN migrated_count;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- STATUS UPDATE FUNCTIONS
-- ========================================

-- Update crawler counts for dedicated tables
CREATE OR REPLACE FUNCTION update_dedicated_crawler_counts()
RETURNS VOID AS $$
BEGIN
    -- Update Twitter crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM tweets 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM tweets 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'twitter';
    
    -- Update Reddit crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM reddit_posts 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM reddit_posts 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'reddit';
    
    -- Update News crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM news_articles 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM news_articles 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'news';
    
    -- Update Crypto crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM coingecko_tokens 
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM coingecko_tokens 
            WHERE collected_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'crypto';
    
    -- Update DexScreener crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM dexscreener_pairs 
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM dexscreener_pairs 
            WHERE collected_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'dexscreener';
    
    -- Update DexPaprika crawler counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM dexpaprika_pairs 
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM dexpaprika_pairs 
            WHERE collected_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'dexpaprika';
END;
$$ LANGUAGE plpgsql;

-- Add unique constraint for crypto_tokens
ALTER TABLE IF EXISTS crypto_tokens ADD CONSTRAINT IF NOT EXISTS unique_symbol UNIQUE(symbol);

-- Add unique constraint for dex_pairs
ALTER TABLE IF EXISTS dex_pairs ADD CONSTRAINT IF NOT EXISTS unique_pair_id UNIQUE(pair_id); 