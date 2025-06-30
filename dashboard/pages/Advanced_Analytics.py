import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

from storage.db import engine, Tweet, RedditPost
from sqlmodel import Session, select, func
from processor.viral_predictor import predictor
from processor.content_clustering import clusterer
from processor.scorer import degen_score

st.set_page_config(page_title="🧠 Advanced Analytics", layout="wide")
st.title("🧠 Advanced Analytics & ML Insights")

# Load data
@st.cache_data(ttl=300)
def load_analytics_data():
    with Session(engine) as session:
        # Get recent data
        tweets = session.exec(select(Tweet)).all()
        reddit_posts = session.exec(select(RedditPost)).all()
        
        # Convert to dict format for processing
        items = []
        for tweet in tweets:
            items.append({
                'text': tweet.text,
                'title': tweet.text[:100],
                'published': tweet.published.isoformat() if tweet.published else None,
                'likeCount': tweet.like_count,
                'retweetCount': tweet.retweet_count,
                'replyCount': tweet.reply_count,
                'viewCount': tweet.view_count,
                'userFollowersCount': tweet.user_followers_count,
                'userVerified': tweet.user_verified,
                '_source': 'twitter',
                '_engagement_score': tweet.engagement_score or 0,
                'link': f"https://twitter.com/user/status/{tweet.tweet_id}" if tweet.tweet_id else None
            })
        
        for post in reddit_posts:
            items.append({
                'text': post.title,
                'title': post.title,
                'summary': post.selftext,
                'published': post.published.isoformat() if post.published else None,
                'likeCount': post.score,
                'retweetCount': 0,
                'replyCount': post.num_comments,
                'viewCount': 0,
                'userFollowersCount': 0,
                'userVerified': False,
                '_source': 'reddit',
                '_engagement_score': post.engagement_score or 0,
                'link': post.url
            })
        
        return items

# Load data
items = load_analytics_data()

if not items:
    st.warning("No data available. Please run scrapers first.")
    st.stop()

# Sidebar controls
st.sidebar.header("📊 Analytics Controls")

# Time range filter
st.sidebar.subheader("Time Range")
days_back = st.sidebar.slider("Days back", 1, 30, 7)
cutoff_date = datetime.now() - timedelta(days=days_back)

# Filter items by date
filtered_items = [
    item for item in items 
    if item.get('published') and datetime.fromisoformat(item['published'].replace('Z', '+00:00')) > cutoff_date
]

st.sidebar.metric("Items Analyzed", len(filtered_items))

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Engagement Trends")
    
    # Create engagement timeline
    df = pd.DataFrame(filtered_items)
    df['published'] = pd.to_datetime(df['published'])
    df['date'] = df['published'].dt.date
    
    daily_engagement = df.groupby('date').agg({
        '_engagement_score': ['mean', 'sum', 'count']
    }).reset_index()
    daily_engagement.columns = ['date', 'avg_engagement', 'total_engagement', 'post_count']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Average Engagement', 'Daily Post Volume'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=daily_engagement['date'], y=daily_engagement['avg_engagement'], 
                  mode='lines+markers', name='Avg Engagement'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=daily_engagement['date'], y=daily_engagement['post_count'], 
               name='Post Count'),
        row=2, col=1
    )
    
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Source Distribution")
    
    source_counts = df['_source'].value_counts()
    fig = px.pie(values=source_counts.values, names=source_counts.index, 
                 title="Posts by Source")
    st.plotly_chart(fig, use_container_width=True)

# Viral Prediction Section
st.subheader("🔮 Viral Prediction Analysis")

# Train predictor if needed
if st.button("🔄 Train Viral Prediction Models"):
    with st.spinner("Training models..."):
        predictor.train(filtered_items)
        predictor.save_models()
    st.success("Models trained!")

# Load existing models
predictor.load_models()

# Add predictions to items
for item in filtered_items:
    item['_predicted_viral_score'] = predictor.predict_viral_score(item)

# Show prediction vs actual
df['predicted_score'] = [item.get('_predicted_viral_score', 0) for item in filtered_items]

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Prediction vs Actual")
    
    fig = px.scatter(
        df, x='_engagement_score', y='predicted_score',
        color='_source', size='likeCount',
        hover_data=['text'],
        title="Predicted vs Actual Engagement"
    )
    fig.add_trace(go.Scatter(x=[0, df['_engagement_score'].max()], 
                            y=[0, df['_engagement_score'].max()], 
                            mode='lines', name='Perfect Prediction',
                            line=dict(dash='dash', color='red')))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Top Predicted Viral Posts")
    
    # Sort by predicted score
    top_predicted = sorted(filtered_items, 
                          key=lambda x: x.get('_predicted_viral_score', 0), 
                          reverse=True)[:10]
    
    for i, item in enumerate(top_predicted[:5]):
        with st.expander(f"#{i+1} - {item.get('title', 'No title')[:50]}..."):
            st.write(f"**Predicted Score:** {item.get('_predicted_viral_score', 0):.2f}")
            st.write(f"**Actual Score:** {item.get('_engagement_score', 0):.2f}")
            st.write(f"**Source:** {item.get('_source', 'unknown')}")
            st.write(f"**Text:** {item.get('text', '')[:200]}...")
            if item.get('link'):
                st.write(f"**Link:** {item['link']}")

# Content Clustering Section
st.subheader("🔍 Content Clustering & Topics")

if st.button("🔄 Run Content Clustering"):
    with st.spinner("Clustering content..."):
        clusters = clusterer.cluster_content(filtered_items)
        topics = clusterer.extract_topics(filtered_items)
    st.success("Clustering complete!")

# Show cluster summary
if hasattr(clusterer, 'clusters') and clusterer.clusters:
    st.subheader("📋 Content Clusters")
    
    cluster_summary = clusterer.get_cluster_summary()
    
    for cluster in cluster_summary[:5]:  # Show top 5 clusters
        with st.expander(f"Cluster {cluster['cluster_id']} - {cluster['size']} items"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Size", cluster['size'])
                st.metric("Avg Engagement", cluster['avg_engagement'])
            
            with col2:
                st.write("**Top Tickers:**")
                for ticker in cluster['top_tickers']:
                    st.write(f"• {ticker}")
            
            with col3:
                st.write("**Top Sources:**")
                for source in cluster['top_sources']:
                    st.write(f"• {source}")
            
            st.write("**Sample Titles:**")
            for title in cluster['sample_titles']:
                st.write(f"• {title}")

# Topic Analysis
if hasattr(clusterer, 'topics') and clusterer.topics:
    st.subheader("📚 Topic Analysis")
    
    # Create topic visualization
    topic_data = []
    for topic_id, topic_info in clusterer.topics.items():
        topic_data.append({
            'topic_id': topic_id,
            'words': ', '.join(topic_info['words'][:5]),
            'strength': topic_info['strength']
        })
    
    topic_df = pd.DataFrame(topic_data)
    
    fig = px.bar(topic_df, x='topic_id', y='strength', 
                 title="Topic Strength Distribution",
                 labels={'topic_id': 'Topic ID', 'strength': 'Topic Strength'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Show topic words
    col1, col2 = st.columns(2)
    
    for i, (topic_id, topic_info) in enumerate(clusterer.topics.items()):
        with col1 if i % 2 == 0 else col2:
            with st.expander(f"Topic {topic_id}"):
                st.write("**Top Words:**")
                for word in topic_info['words']:
                    st.write(f"• {word}")

# Similarity Search
st.subheader("🔍 Find Similar Content")

search_text = st.text_input("Enter text to find similar content:")
if search_text:
    search_item = {'text': search_text, 'title': search_text}
    similar_items = clusterer.find_similar_content(search_item, filtered_items, top_k=5)
    
    if similar_items:
        st.write("**Similar Content:**")
        for item, similarity in similar_items:
            with st.expander(f"Similarity: {similarity:.3f} - {item.get('title', 'No title')[:50]}..."):
                st.write(f"**Source:** {item.get('_source', 'unknown')}")
                st.write(f"**Engagement:** {item.get('_engagement_score', 0):.2f}")
                st.write(f"**Text:** {item.get('text', '')[:200]}...")
                if item.get('link'):
                    st.write(f"**Link:** {item['link']}")
    else:
        st.info("No similar content found.")

# Performance Metrics
st.subheader("📊 Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Posts", len(filtered_items))
    st.metric("Avg Engagement", f"{df['_engagement_score'].mean():.2f}")

with col2:
    st.metric("Max Engagement", f"{df['_engagement_score'].max():.2f}")
    st.metric("Median Engagement", f"{df['_engagement_score'].median():.2f}")

with col3:
    st.metric("Twitter Posts", len(df[df['_source'] == 'twitter']))
    st.metric("Reddit Posts", len(df[df['_source'] == 'reddit']))

with col4:
    st.metric("Prediction Accuracy", f"{np.corrcoef(df['_engagement_score'], df['predicted_score'])[0,1]:.3f}")
    st.metric("Viral Posts (>100)", len(df[df['_engagement_score'] > 100])) 