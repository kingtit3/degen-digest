import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from storage.db import engine, Tweet, RedditPost, Digest
from sqlmodel import Session, select, func
from sqlalchemy import desc, and_, or_, extract
import humanize
from utils.advanced_logging import get_logger
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = get_logger(__name__)

def calculate_engagement_score(tweet):
    """Calculate engagement score for a tweet"""
    likes = tweet.like_count or 0
    retweets = tweet.retweet_count or 0
    replies = tweet.reply_count or 0
    views = tweet.view_count or 0
    
    return likes + (retweets * 2) + (replies * 3) + (views * 0.1)

def analyze_sentiment(text):
    """Analyze sentiment of text using VADER"""
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores['compound']

def main():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 class="gradient-text">📊 Advanced Analytics</h1>
        <p style="color: #888; font-size: 18px;">Deep insights and market intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 📅 Time Range")
        time_range = st.selectbox(
            "Select time range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"],
            index=0
        )
        
        if time_range == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("To", value=datetime.now())
        else:
            days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
            start_date = datetime.now() - timedelta(days=days_map[time_range])
            end_date = datetime.now()
        
        st.markdown("### 📊 Data Sources")
        sources = st.multiselect(
            "Select sources",
            ["Twitter", "Reddit"],
            default=["Twitter", "Reddit"]
        )
        
        st.markdown("### 📈 Analysis Type")
        analysis_type = st.selectbox(
            "Choose analysis",
            ["Engagement Trends", "Sentiment Analysis", "Content Clustering", "Source Performance", "Market Insights"]
        )
    
    # Main content
    if analysis_type == "Engagement Trends":
        show_engagement_trends(start_date, end_date, sources)
    elif analysis_type == "Sentiment Analysis":
        show_sentiment_analysis(start_date, end_date, sources)
    elif analysis_type == "Content Clustering":
        show_content_clustering(start_date, end_date, sources)
    elif analysis_type == "Source Performance":
        show_source_performance(start_date, end_date, sources)
    elif analysis_type == "Market Insights":
        show_market_insights(start_date, end_date, sources)

def show_engagement_trends(start_date, end_date, sources):
    """Show engagement trends over time"""
    st.markdown("## 📈 Engagement Trends Analysis")
    
    with st.spinner("Loading engagement data..."):
        data = []
        
        if "Twitter" in sources:
            with Session(engine) as sess:
                tweets = sess.exec(
                    select(Tweet)
                    .where(
                        and_(
                            Tweet.created_at >= start_date,
                            Tweet.created_at <= end_date
                        )
                    )
                    .order_by(Tweet.created_at)
                ).all()
                
                for tweet in tweets:
                    engagement = calculate_engagement_score(tweet)
                    data.append({
                        'date': tweet.created_at.date(),
                        'engagement': engagement,
                        'likes': tweet.like_count or 0,
                        'retweets': tweet.retweet_count or 0,
                        'replies': tweet.reply_count or 0,
                        'views': tweet.view_count or 0,
                        'source': 'Twitter'
                    })
        
        if "Reddit" in sources:
            with Session(engine) as sess:
                posts = sess.exec(
                    select(RedditPost)
                    .where(
                        and_(
                            RedditPost.created_at >= start_date,
                            RedditPost.created_at <= end_date
                        )
                    )
                    .order_by(RedditPost.created_at)
                ).all()
                
                for post in posts:
                    engagement = (post.score or 0) + (post.numComments or 0) * 2
                    data.append({
                        'date': post.created_at.date(),
                        'engagement': engagement,
                        'likes': post.score or 0,
                        'retweets': 0,
                        'replies': post.numComments or 0,
                        'views': 0,
                        'source': 'Reddit'
                    })
    
    if data:
        df = pd.DataFrame(data)
        
        # Daily engagement trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Daily Engagement")
            daily_engagement = df.groupby('date')['engagement'].sum().reset_index()
            
            fig = px.line(
                daily_engagement,
                x='date',
                y='engagement',
                title="Daily Total Engagement",
                color_discrete_sequence=['#00d4ff']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Engagement by Source")
            source_engagement = df.groupby('source')['engagement'].sum().reset_index()
            
            fig = px.bar(
                source_engagement,
                x='source',
                y='engagement',
                title="Total Engagement by Source",
                color_discrete_sequence=['#ff6b6b', '#4ecdc4']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Engagement metrics breakdown
        st.markdown("### 📊 Engagement Metrics Breakdown")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Engagement", f"{df['engagement'].sum():,}")
        with col2:
            st.metric("Avg Daily Engagement", f"{df.groupby('date')['engagement'].sum().mean():.0f}")
        with col3:
            st.metric("Peak Daily Engagement", f"{df.groupby('date')['engagement'].sum().max():,}")
        with col4:
            st.metric("Total Posts", len(df))
        
        # Engagement distribution
        st.markdown("### 📈 Engagement Distribution")
        fig = px.histogram(
            df,
            x='engagement',
            nbins=30,
            title="Engagement Score Distribution",
            color_discrete_sequence=['#00d4ff']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No engagement data available for the selected time range")

def show_sentiment_analysis(start_date, end_date, sources):
    """Show sentiment analysis"""
    st.markdown("## 😊 Sentiment Analysis")
    
    with st.spinner("Analyzing sentiment..."):
        data = []
        
        if "Twitter" in sources:
            with Session(engine) as sess:
                tweets = sess.exec(
                    select(Tweet)
                    .where(
                        and_(
                            Tweet.created_at >= start_date,
                            Tweet.created_at <= end_date
                        )
                    )
                    .limit(1000)  # Limit for performance
                ).all()
                
                for tweet in tweets:
                    sentiment = analyze_sentiment(tweet.full_text or "")
                    data.append({
                        'date': tweet.created_at.date(),
                        'sentiment': sentiment,
                        'text': tweet.full_text,
                        'source': 'Twitter',
                        'engagement': calculate_engagement_score(tweet)
                    })
        
        if "Reddit" in sources:
            with Session(engine) as sess:
                posts = sess.exec(
                    select(RedditPost)
                    .where(
                        and_(
                            RedditPost.created_at >= start_date,
                            RedditPost.created_at <= end_date
                        )
                    )
                    .limit(500)  # Limit for performance
                ).all()
                
                for post in posts:
                    text = f"{post.title}"
                    sentiment = analyze_sentiment(text)
                    data.append({
                        'date': post.created_at.date(),
                        'sentiment': sentiment,
                        'text': text,
                        'source': 'Reddit',
                        'engagement': (post.score or 0) + (post.numComments or 0) * 2
                    })
    
    if data:
        df = pd.DataFrame(data)
        
        # Sentiment distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Sentiment Distribution")
            
            # Categorize sentiment
            df['sentiment_category'] = pd.cut(
                df['sentiment'],
                bins=[-1, -0.1, 0.1, 1],
                labels=['Negative', 'Neutral', 'Positive']
            )
            
            sentiment_counts = df['sentiment_category'].value_counts()
            
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Sentiment Distribution",
                color_discrete_sequence=['#ff6b6b', '#f39c12', '#4ecdc4']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Daily Sentiment Trend")
            daily_sentiment = df.groupby('date')['sentiment'].mean().reset_index()
            
            fig = px.line(
                daily_sentiment,
                x='date',
                y='sentiment',
                title="Average Daily Sentiment",
                color_discrete_sequence=['#00d4ff']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            fig.add_hline(y=0, line_dash="dash", line_color="white")
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment vs Engagement
        st.markdown("### 📊 Sentiment vs Engagement")
        fig = px.scatter(
            df,
            x='sentiment',
            y='engagement',
            color='source',
            title="Sentiment vs Engagement",
            color_discrete_sequence=['#00d4ff', '#ff6b6b']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Sentiment", f"{df['sentiment'].mean():.3f}")
        with col2:
            st.metric("Positive Posts", f"{len(df[df['sentiment'] > 0.1]):,}")
        with col3:
            st.metric("Negative Posts", f"{len(df[df['sentiment'] < -0.1]):,}")
        with col4:
            st.metric("Neutral Posts", f"{len(df[(df['sentiment'] >= -0.1) & (df['sentiment'] <= 0.1)]):,}")
    
    else:
        st.info("No sentiment data available for the selected time range")

def show_content_clustering(start_date, end_date, sources):
    """Show content clustering analysis"""
    st.markdown("## 🎯 Content Clustering Analysis")
    
    st.info("Content clustering analysis coming soon...")
    st.markdown("""
    This feature will include:
    - Topic modeling and clustering
    - Keyword extraction and analysis
    - Content similarity analysis
    - Trending topics identification
    """)

def show_source_performance(start_date, end_date, sources):
    """Show source performance comparison"""
    st.markdown("## 📊 Source Performance Analysis")
    
    with st.spinner("Analyzing source performance..."):
        data = []
        
        if "Twitter" in sources:
            with Session(engine) as sess:
                tweets = sess.exec(
                    select(Tweet)
                    .where(
                        and_(
                            Tweet.created_at >= start_date,
                            Tweet.created_at <= end_date
                        )
                    )
                ).all()
                
                for tweet in tweets:
                    engagement = calculate_engagement_score(tweet)
                    data.append({
                        'source': 'Twitter',
                        'engagement': engagement,
                        'likes': tweet.like_count or 0,
                        'retweets': tweet.retweet_count or 0,
                        'replies': tweet.reply_count or 0,
                        'views': tweet.view_count or 0,
                        'date': tweet.created_at.date()
                    })
        
        if "Reddit" in sources:
            with Session(engine) as sess:
                posts = sess.exec(
                    select(RedditPost)
                    .where(
                        and_(
                            RedditPost.created_at >= start_date,
                            RedditPost.created_at <= end_date
                        )
                    )
                ).all()
                
                for post in posts:
                    engagement = (post.score or 0) + (post.numComments or 0) * 2
                    data.append({
                        'source': 'Reddit',
                        'engagement': engagement,
                        'likes': post.score or 0,
                        'retweets': 0,
                        'replies': post.numComments or 0,
                        'views': 0,
                        'date': post.created_at.date()
                    })
    
    if data:
        df = pd.DataFrame(data)
        
        # Source comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Total Engagement by Source")
            source_totals = df.groupby('source')['engagement'].sum().reset_index()
            
            fig = px.bar(
                source_totals,
                x='source',
                y='engagement',
                title="Total Engagement",
                color_discrete_sequence=['#00d4ff', '#ff6b6b']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Average Engagement by Source")
            source_avg = df.groupby('source')['engagement'].mean().reset_index()
            
            fig = px.bar(
                source_avg,
                x='source',
                y='engagement',
                title="Average Engagement per Post",
                color_discrete_sequence=['#4ecdc4', '#f39c12']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        st.markdown("### 📊 Performance Metrics")
        
        metrics_data = []
        for source in df['source'].unique():
            source_df = df[df['source'] == source]
            metrics_data.append({
                'Source': source,
                'Total Posts': len(source_df),
                'Total Engagement': source_df['engagement'].sum(),
                'Avg Engagement': source_df['engagement'].mean(),
                'Max Engagement': source_df['engagement'].max(),
                'Engagement Rate': source_df['engagement'].sum() / len(source_df)
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        # Daily performance comparison
        st.markdown("### 📈 Daily Performance Comparison")
        daily_performance = df.groupby(['date', 'source'])['engagement'].sum().reset_index()
        
        fig = px.line(
            daily_performance,
            x='date',
            y='engagement',
            color='source',
            title="Daily Engagement by Source",
            color_discrete_sequence=['#00d4ff', '#ff6b6b']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No performance data available for the selected time range")

def show_market_insights(start_date, end_date, sources):
    """Show market insights and trends"""
    st.markdown("## 💡 Market Insights & Trends")
    
    with st.spinner("Generating market insights..."):
        data = []
        
        if "Twitter" in sources:
            with Session(engine) as sess:
                tweets = sess.exec(
                    select(Tweet)
                    .where(
                        and_(
                            Tweet.created_at >= start_date,
                            Tweet.created_at <= end_date
                        )
                    )
                    .order_by(desc(Tweet.created_at))
                    .limit(1000)
                ).all()
                
                for tweet in tweets:
                    engagement = calculate_engagement_score(tweet)
                    sentiment = analyze_sentiment(tweet.full_text or "")
                    data.append({
                        'date': tweet.created_at.date(),
                        'text': tweet.full_text,
                        'engagement': engagement,
                        'sentiment': sentiment,
                        'source': 'Twitter'
                    })
        
        if "Reddit" in sources:
            with Session(engine) as sess:
                posts = sess.exec(
                    select(RedditPost)
                    .where(
                        and_(
                            RedditPost.created_at >= start_date,
                            RedditPost.created_at <= end_date
                        )
                    )
                    .order_by(desc(RedditPost.created_at))
                    .limit(500)
                ).all()
                
                for post in posts:
                    text = f"{post.title}"
                    engagement = (post.score or 0) + (post.numComments or 0) * 2
                    sentiment = analyze_sentiment(text)
                    data.append({
                        'date': post.created_at.date(),
                        'text': text,
                        'engagement': engagement,
                        'sentiment': sentiment,
                        'source': 'Reddit'
                    })
    
    if data:
        df = pd.DataFrame(data)
        
        # Market sentiment trend
        st.markdown("### 📊 Market Sentiment Trend")
        daily_sentiment = df.groupby('date')['sentiment'].mean().reset_index()
        
        fig = px.line(
            daily_sentiment,
            x='date',
            y='sentiment',
            title="Market Sentiment Over Time",
            color_discrete_sequence=['#00d4ff']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        fig.add_hline(y=0, line_dash="dash", line_color="white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top performing content
        st.markdown("### 🔥 Top Performing Content")
        top_content = df.nlargest(10, 'engagement')
        
        for i, row in top_content.iterrows():
            with st.expander(f"#{i+1} - Engagement: {row['engagement']:.0f} ({row['source']})"):
                st.markdown(f"**Content:** {row['text'][:200]}...")
                st.markdown(f"**Sentiment:** {row['sentiment']:.3f}")
                st.markdown(f"**Date:** {row['date']}")
        
        # Market insights summary
        st.markdown("### 💡 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Engagement Insights:**")
            avg_engagement = df['engagement'].mean()
            max_engagement = df['engagement'].max()
            st.markdown(f"• Average engagement: {avg_engagement:.0f}")
            st.markdown(f"• Peak engagement: {max_engagement:.0f}")
            st.markdown(f"• Total posts analyzed: {len(df):,}")
        
        with col2:
            st.markdown("**😊 Sentiment Insights:**")
            positive_posts = len(df[df['sentiment'] > 0.1])
            negative_posts = len(df[df['sentiment'] < -0.1])
            neutral_posts = len(df[(df['sentiment'] >= -0.1) & (df['sentiment'] <= 0.1)])
            
            st.markdown(f"• Positive posts: {positive_posts:,}")
            st.markdown(f"• Negative posts: {negative_posts:,}")
            st.markdown(f"• Neutral posts: {neutral_posts:,}")
        
        # Trend analysis
        st.markdown("### 📊 Trend Analysis")
        
        # Weekly trends
        df['week'] = pd.to_datetime(df['date']).dt.isocalendar().week
        weekly_trends = df.groupby('week').agg({
            'engagement': 'sum',
            'sentiment': 'mean',
            'text': 'count'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Weekly Engagement", "Weekly Sentiment"),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=weekly_trends['week'], y=weekly_trends['engagement'], 
                      mode='lines+markers', name='Engagement'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=weekly_trends['week'], y=weekly_trends['sentiment'], 
                      mode='lines+markers', name='Sentiment'),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No market insights data available for the selected time range")

if __name__ == "__main__":
    main() 