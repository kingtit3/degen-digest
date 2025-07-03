# 🚀 Degen Digest Dashboard

A clean, simple dashboard for viewing your daily crypto intelligence digest with analytics and trending content.

## ✨ Features

- **📰 Current Digest**: View the latest digest with fresh generation button
- **📊 Analytics**: Visual charts and metrics from your data sources
- **🔥 Trending**: Twitter-style feed of top content with engagement scores

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-streamlit.txt
```

### 2. Generate a Digest (if you don't have one)

```bash
python3 main.py
```

### 3. Start the Dashboard

```bash
python3 start_dashboard.py
```

The dashboard will be available at: **http://localhost:8501**

## 📱 Dashboard Tabs

### 📰 Current Digest

- View the latest digest content
- Generate fresh digest with new data
- Download digest as markdown file

### 📊 Analytics

- Data source distribution charts
- Engagement score analysis
- Data quality metrics
- Real-time statistics

### 🔥 Trending

- Twitter-style content feed
- Filter by source (Twitter, Reddit, etc.)
- Sort by engagement score
- Viral content badges
- Sentiment analysis

## 🎨 Design Features

- **Clean, modern interface** with gradient headers
- **Responsive design** that works on all devices
- **Smooth animations** and hover effects
- **Twitter-style cards** for trending content
- **Interactive charts** with Plotly
- **Real-time data** updates

## 🔧 Customization

The dashboard uses:

- **Streamlit** for the web interface
- **Plotly** for interactive charts
- **Custom CSS** for styling
- **JSON data** from your scrapers

## 📊 Data Sources

The dashboard automatically reads from:

- `output/twitter_raw.json`
- `output/reddit_raw.json`
- `output/telegram_raw.json`
- `output/newsapi_raw.json`

## 🚀 Tips

- **Generate fresh digest** to see the latest content
- **Use filters** in the Trending tab to find specific content
- **Check analytics** to understand your data quality
- **Download digests** for offline reading

---

**Degen Digest Dashboard** - Your crypto intelligence companion 🚀
