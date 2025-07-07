-- Create dedicated articles table for news stories
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    url TEXT,
    source_name VARCHAR(255),  -- NewsAPI source name (e.g., "CoinDesk", "Cointelegraph")
    author VARCHAR(255),
    published_at TIMESTAMP,
    query TEXT,  -- The search query that found this article
    source_type VARCHAR(50) DEFAULT 'news',
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Viral analysis metadata
    viral_keywords JSONB,  -- Array of viral keywords found
    sentiment VARCHAR(50),  -- positive, negative, neutral
    urgency VARCHAR(50),   -- high, medium, low
    category VARCHAR(100), -- memecoin, launchpad, airdrop, farming, etc.
    
    -- Engagement metrics (if available)
    engagement_score DECIMAL(10,2) DEFAULT 0,
    virality_score DECIMAL(10,2) DEFAULT 0,
    sentiment_score DECIMAL(10,2) DEFAULT 0,
    
    -- Additional metadata
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10),
    api_source VARCHAR(50) DEFAULT 'newsapi.org',
    
    -- Raw data from NewsAPI
    raw_data JSONB,
    
    -- Indexes for performance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_source_name ON articles(source_name);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_sentiment ON articles(sentiment);
CREATE INDEX IF NOT EXISTS idx_articles_urgency ON articles(urgency);
CREATE INDEX IF NOT EXISTS idx_articles_engagement_score ON articles(engagement_score);
CREATE INDEX IF NOT EXISTS idx_articles_virality_score ON articles(virality_score);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE articles IS 'Dedicated table for news articles with rich metadata from NewsAPI';
COMMENT ON COLUMN articles.viral_keywords IS 'JSON array of viral keywords found in the article';
COMMENT ON COLUMN articles.sentiment IS 'Sentiment analysis result: positive, negative, neutral';
COMMENT ON COLUMN articles.urgency IS 'Urgency level: high, medium, low';
COMMENT ON COLUMN articles.category IS 'Article category: memecoin, launchpad, airdrop, farming, etc.';
COMMENT ON COLUMN articles.raw_data IS 'Complete raw data from NewsAPI response'; 