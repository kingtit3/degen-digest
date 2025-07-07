@app.route("/api/news-posts")
def get_news_posts():
    """Get top news posts with rich metadata from articles table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'published_at')
        
        # Validate sort field
        valid_sort_fields = ["published_at", "engagement_score", "virality_score", "sentiment_score", "created_at", "urgency", "sentiment"]
        if sort_by not in valid_sort_fields:
            sort_by = "published_at"
        
        order_clause = f"ORDER BY a.{sort_by} DESC NULLS LAST"

        # Get top news posts with rich metadata
        cursor.execute(
            f"""
            SELECT 
                a.id, a.title, a.description, a.content, a.url, 
                a.source_name, a.author, a.published_at, a.query,
                a.viral_keywords, a.sentiment, a.urgency, a.category,
                a.engagement_score, a.virality_score, a.sentiment_score,
                a.language, a.country, a.api_source, a.raw_data,
                a.created_at, a.collected_at
            FROM articles a
            WHERE a.source_type = 'news'
            AND a.created_at >= NOW() - INTERVAL '30 days'
            {order_clause}
            LIMIT 50
        """
        )

        posts = []
        for row in cursor.fetchall():
            # Clean the content and title
            clean_title = clean_post_title(row[1])
            clean_content = clean_post_content(row[3] or row[2])  # Use content, fallback to description
            
            # Only include posts with readable content
            if clean_content or clean_title:
                post = {
                    "id": row[0],
                    "title": clean_title,
                    "description": row[2] or "",
                    "content": clean_content,
                    "url": row[4] or "",
                    "source_name": row[5] or "Unknown",
                    "author": row[6] or "Anonymous",
                    "published_at": row[7].isoformat() if row[7] else None,
                    "query": row[8] or "",
                    "viral_keywords": row[9] if row[9] else [],
                    "sentiment": row[10] or "neutral",
                    "urgency": row[11] or "low",
                    "category": row[12] or "general",
                    "engagement_score": float(row[13] or 0),
                    "virality_score": float(row[14] or 0),
                    "sentiment_score": float(row[15] or 0),
                    "language": row[16] or "en",
                    "country": row[17],
                    "api_source": row[18] or "newsapi.org",
                    "raw_data": row[19],
                    "created_at": row[20].isoformat() if row[20] else None,
                    "collected_at": row[21].isoformat() if row[21] else None,
                }
                posts.append(post)

        cursor.close()
        conn.close()

        # If no clean posts found, provide fallback data
        if not posts:
            logger.warning("No news posts found, returning empty list")
            posts = []

        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting news posts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/news/stats")
def get_news_stats():
    """Get news statistics and analytics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get various statistics
        stats = {}
        
        # Total articles
        cursor.execute("SELECT COUNT(*) FROM articles WHERE source_type = 'news'")
        stats["total_articles"] = cursor.fetchone()[0]
        
        # Articles by source
        cursor.execute("""
            SELECT source_name, COUNT(*) as count 
            FROM articles 
            WHERE source_type = 'news' 
            GROUP BY source_name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats["sources"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Articles by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            WHERE source_type = 'news' AND category IS NOT NULL
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats["categories"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Articles by sentiment
        cursor.execute("""
            SELECT sentiment, COUNT(*) as count 
            FROM articles 
            WHERE source_type = 'news' AND sentiment IS NOT NULL
            GROUP BY sentiment 
            ORDER BY count DESC
        """)
        stats["sentiments"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Articles by urgency
        cursor.execute("""
            SELECT urgency, COUNT(*) as count 
            FROM articles 
            WHERE source_type = 'news' AND urgency IS NOT NULL
            GROUP BY urgency 
            ORDER BY count DESC
        """)
        stats["urgency_levels"] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM articles 
            WHERE source_type = 'news' 
            AND created_at >= NOW() - INTERVAL '24 hours'
        """)
        stats["articles_last_24h"] = cursor.fetchone()[0]
        
        # Top viral keywords
        cursor.execute("""
            SELECT keyword, COUNT(*) as count
            FROM articles a,
                 jsonb_array_elements_text(a.viral_keywords) as keyword
            WHERE a.source_type = 'news' AND a.viral_keywords IS NOT NULL
            GROUP BY keyword
            ORDER BY count DESC
            LIMIT 20
        """)
        stats["top_viral_keywords"] = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.close()
        conn.close()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting news stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/news/filter")
def get_filtered_news():
    """Get filtered news posts based on various criteria"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get filter parameters
        source = request.args.get('source')
        category = request.args.get('category')
        sentiment = request.args.get('sentiment')
        urgency = request.args.get('urgency')
        keyword = request.args.get('keyword')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100

        # Build WHERE clause
        where_conditions = ["a.source_type = 'news'"]
        params = []
        
        if source:
            where_conditions.append("a.source_name ILIKE %s")
            params.append(f"%{source}%")
        
        if category:
            where_conditions.append("a.category = %s")
            params.append(category)
        
        if sentiment:
            where_conditions.append("a.sentiment = %s")
            params.append(sentiment)
        
        if urgency:
            where_conditions.append("a.urgency = %s")
            params.append(urgency)
        
        if keyword:
            where_conditions.append("a.viral_keywords::text ILIKE %s")
            params.append(f"%{keyword}%")

        where_clause = " AND ".join(where_conditions)

        # Execute query
        query = f"""
            SELECT 
                a.id, a.title, a.description, a.content, a.url, 
                a.source_name, a.author, a.published_at, a.query,
                a.viral_keywords, a.sentiment, a.urgency, a.category,
                a.engagement_score, a.virality_score, a.sentiment_score,
                a.language, a.country, a.api_source, a.raw_data,
                a.created_at, a.collected_at
            FROM articles a
            WHERE {where_clause}
            ORDER BY a.published_at DESC NULLS LAST
            LIMIT %s
        """
        params.append(limit)

        cursor.execute(query, params)

        posts = []
        for row in cursor.fetchall():
            clean_title = clean_post_title(row[1])
            clean_content = clean_post_content(row[3] or row[2])
            
            if clean_content or clean_title:
                post = {
                    "id": row[0],
                    "title": clean_title,
                    "description": row[2] or "",
                    "content": clean_content,
                    "url": row[4] or "",
                    "source_name": row[5] or "Unknown",
                    "author": row[6] or "Anonymous",
                    "published_at": row[7].isoformat() if row[7] else None,
                    "query": row[8] or "",
                    "viral_keywords": row[9] if row[9] else [],
                    "sentiment": row[10] or "neutral",
                    "urgency": row[11] or "low",
                    "category": row[12] or "general",
                    "engagement_score": float(row[13] or 0),
                    "virality_score": float(row[14] or 0),
                    "sentiment_score": float(row[15] or 0),
                    "language": row[16] or "en",
                    "country": row[17],
                    "api_source": row[18] or "newsapi.org",
                    "raw_data": row[19],
                    "created_at": row[20].isoformat() if row[20] else None,
                    "collected_at": row[21].isoformat() if row[21] else None,
                }
                posts.append(post)

        cursor.close()
        conn.close()

        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting filtered news: {e}")
        return jsonify({"error": str(e)}), 500 