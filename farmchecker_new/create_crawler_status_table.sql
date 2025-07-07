-- Create crawler status tracking table
CREATE TABLE IF NOT EXISTS crawler_status (
    id SERIAL PRIMARY KEY,
    crawler_name VARCHAR(50) NOT NULL UNIQUE,
    last_run_at TIMESTAMP,
    last_successful_run_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unknown', -- online, offline, error, running
    items_collected INTEGER DEFAULT 0,
    items_collected_24h INTEGER DEFAULT 0,
    items_collected_1h INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial crawler records
INSERT INTO crawler_status (crawler_name, status) VALUES
    ('twitter', 'unknown'),
    ('reddit', 'unknown'),
    ('news', 'unknown'),
    ('crypto', 'unknown'),
    ('dexpaprika', 'unknown'),
    ('dexscreener', 'unknown'),
    ('migration_service', 'unknown')
ON CONFLICT (crawler_name) DO NOTHING;

-- Create function to update crawler status
CREATE OR REPLACE FUNCTION update_crawler_status(
    p_crawler_name VARCHAR(50),
    p_status VARCHAR(20),
    p_items_collected INTEGER DEFAULT 0,
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE crawler_status 
    SET 
        last_run_at = CURRENT_TIMESTAMP,
        last_successful_run_at = CASE WHEN p_status = 'online' THEN CURRENT_TIMESTAMP ELSE last_successful_run_at END,
        status = p_status,
        items_collected = p_items_collected,
        error_message = p_error_message,
        updated_at = CURRENT_TIMESTAMP
    WHERE crawler_name = p_crawler_name;
    
    -- If no rows were updated, insert a new record
    IF NOT FOUND THEN
        INSERT INTO crawler_status (crawler_name, last_run_at, last_successful_run_at, status, items_collected, error_message)
        VALUES (p_crawler_name, CURRENT_TIMESTAMP, 
                CASE WHEN p_status = 'online' THEN CURRENT_TIMESTAMP ELSE NULL END,
                p_status, p_items_collected, p_error_message);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to update hourly/daily counts
CREATE OR REPLACE FUNCTION update_crawler_counts()
RETURNS VOID AS $$
BEGIN
    -- Update 24h and 1h counts for all crawlers
    UPDATE crawler_status cs
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM content_items ci 
            JOIN data_sources ds ON ci.source_id = ds.id 
            WHERE ds.name = cs.crawler_name 
            AND ci.created_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM content_items ci 
            JOIN data_sources ds ON ci.source_id = ds.id 
            WHERE ds.name = cs.crawler_name 
            AND ci.created_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name IN ('twitter', 'reddit', 'news', 'crypto', 'dexpaprika', 'dexscreener');
    
    -- Update migration service counts
    UPDATE crawler_status 
    SET 
        items_collected_24h = (
            SELECT COUNT(*) 
            FROM digests 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        ),
        items_collected_1h = (
            SELECT COUNT(*) 
            FROM digests 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
        )
    WHERE crawler_name = 'migration_service';
END;
$$ LANGUAGE plpgsql; 