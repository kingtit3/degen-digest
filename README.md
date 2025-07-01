# 🚀 Degen Digest v2.0 - Crypto Intelligence Hub

A modern, AI-powered crypto market intelligence platform that distills the spiciest 🍿 alpha, memes, and whale moves from Crypto Twitter, Reddit, and Telegram into actionable insights.

## ✨ New Features in v2.0

### 🎨 **Modern Futuristic UI**
- **Dark theme** with gradient accents and glassmorphism effects
- **Responsive design** optimized for all devices
- **Interactive charts** and real-time data visualization
- **Animated components** with hover effects and smooth transitions

### 📊 **Advanced Analytics Dashboard**
- **Real-time engagement tracking** with interactive charts
- **Sentiment analysis** using VADER sentiment scoring
- **Source performance comparison** across platforms
- **Market insights** with trend analysis and predictions
- **Content clustering** and topic modeling

### 🔍 **Smart Data Management**
- **Advanced filtering** by date, source, engagement, and content type
- **Duplicate detection and removal** with configurable similarity thresholds
- **Intelligent sorting** by engagement, date, source, and viral prediction
- **Pagination** for large datasets
- **Real-time search** with keyword filtering

### 📈 **Enhanced Live Feed**
- **Real-time content streaming** from multiple sources
- **Engagement metrics** with detailed breakdowns
- **Source attribution** with direct links
- **Content categorization** and tagging
- **Performance analytics** sidebar

### 🏥 **Health Monitoring System**
- **System performance tracking** (CPU, memory, disk usage)
- **Data freshness monitoring** with automated alerts
- **Database health checks** and connectivity monitoring
- **LLM service monitoring** with cost tracking
- **Automated alerting** for critical issues

### 📋 **Human-Friendly Digests**
- **Executive summaries** written in clear, professional language
- **Key takeaways** section for quick insights
- **Market overview** with comprehensive metrics
- **Categorized stories** by market impact
- **Professional formatting** with improved readability

### ⚡ **Performance Improvements**
- **Async LLM processing** (5x faster content generation)
- **Rate limiting** to prevent API abuse
- **Smart caching** with fallback mechanisms
- **Concurrent data processing** for better throughput
- **Optimized database queries** for faster retrieval

## 🚀 Quick Start

```bash
# 1. Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the dashboard
cd dashboard
streamlit run app.py

# 4. Generate a digest
python main.py

# Or use the automated wrapper (recommended)
python generate_digest.py
```

## 📊 Dashboard Features

### **Main Dashboard**
- **Real-time metrics** with animated cards
- **Data source distribution** pie charts
- **Engagement trends** over time
- **Recent activity** feed
- **System health** overview

### **Live Feed**
- **Advanced filtering** by date, source, engagement
- **Duplicate removal** with similarity detection
- **Multiple sorting options** (engagement, date, source)
- **Real-time analytics** sidebar
- **Pagination** for large datasets

### **Analytics**
- **Engagement trends** analysis
- **Sentiment analysis** with VADER scoring
- **Source performance** comparison
- **Market insights** and trend analysis
- **Content clustering** (coming soon)

### **Health Monitor**
- **System metrics** (CPU, memory, disk)
- **Data freshness** monitoring
- **Database health** checks
- **LLM service** monitoring
- **Automated alerts** for issues

## 🔧 Configuration

### **Environment Variables**
```bash
# Required APIs
APIFY_API_TOKEN=your_apify_token
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.0-flash-001

# Optional
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id

# Budget Control
LLM_BUDGET_MONTHLY_USD=10.0
OPENROUTER_COST_PER_1K_USD=0.005
```

### **App Configuration**
Edit `config/app_config.yaml` to customize:
- Data source settings
- Processing parameters
- LLM configuration
- Dashboard options
- Monitoring thresholds

## 📈 Data Sources

### **Currently Supported**
- **Twitter/X** - Via Apify scraping
- **Reddit** - RSS feed monitoring
- **Telegram** - Channel monitoring (optional)
- **NewsAPI** - Financial news
- **CoinGecko** - Price and market data

### **Coming Soon**
- **Discord** - Alpha channel monitoring
- **YouTube** - Video content analysis
- **TikTok** - Short-form video content
- **On-chain data** - DEX volumes, whale movements

## 🎯 Key Features

### **Content Processing**
- **AI-powered classification** into 6 categories
- **Engagement scoring** with weighted metrics
- **Viral prediction** using ML models
- **Content clustering** for topic identification
- **Sentiment analysis** for market mood

### **Data Visualization**
- **Interactive charts** with Plotly
- **Real-time updates** with auto-refresh
- **Customizable dashboards** with filters
- **Export capabilities** (PDF, CSV, JSON)
- **Mobile-responsive** design

### **Performance & Reliability**
- **Health monitoring** with automated alerts
- **Rate limiting** to prevent API abuse
- **Error recovery** with fallback mechanisms
- **Caching system** for improved performance
- **Async processing** for better throughput

## 🚀 Deployment

### **Local Development**
```bash
# Start dashboard
cd dashboard && streamlit run app.py

# Generate digest
python main.py

# Run health check
python -c "from utils.health_monitor import health_monitor; print(health_monitor.get_health_summary())"
```

### **Automated Digest Workflow**
```bash
# Recommended: Use the automated wrapper
python generate_digest.py

# This will:
# 1. Check environment variables
# 2. Generate the digest
# 3. Automatically rename with date (digest-YYYY-MM-DD.md)
# 4. Show preview and status
# 5. Handle errors gracefully
```

### **Scheduled Generation**
```bash
# Add to crontab for daily generation at 10 AM EST
0 10 * * * cd /path/to/DegenDigest && python generate_digest.py >> logs/cron.log 2>&1

# Or use the trigger script
python trigger_digest.py
```

### **Docker Deployment**
```bash
# Build and run
docker build -t degen-digest .
docker run -p 8501:8501 --env-file .env degen-digest
```

### **Cloud Deployment**
```bash
# Google Cloud Run
gcloud run deploy degen-digest --source . --platform managed

# AWS Lambda
serverless deploy

# Heroku
heroku create degen-digest
git push heroku main
```

## 📊 Monitoring & Alerts

### **Health Checks**
- **System metrics** monitoring
- **Data freshness** validation
- **API connectivity** testing
- **Performance** tracking
- **Cost monitoring** for LLM usage

### **Alerting**
- **High CPU/memory** usage alerts
- **Stale data** notifications
- **API failures** alerts
- **Budget exceeded** warnings
- **Database connectivity** issues

## 🔮 Roadmap

### **Phase 1 (Current)**
- ✅ Modern UI/UX redesign
- ✅ Advanced analytics dashboard
- ✅ Health monitoring system
- ✅ Async processing improvements
- ✅ Human-friendly digest format

### **Phase 2 (Next Month)**
- 🔄 Discord integration
- 🔄 Real-time WebSocket updates
- 🔄 Email digest delivery
- 🔄 REST API development
- 🔄 Mobile app development

### **Phase 3 (Next Quarter)**
- 📋 Advanced ML pipeline
- 📋 Predictive analytics
- 📋 Social features
- 📋 Enterprise version
- 📋 White-label solution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `docs/` folder
- **Issues**: Create a GitHub issue
- **Discord**: Join our community server
- **Email**: support@degendigest.com

---

🚀 **Degen Digest v2.0** - Your daily crypto intelligence companion

*Built with ❤️ for the crypto community* 