# 🚀 Degen Digest Dashboard Deployment Guide

This guide provides multiple options to deploy your Degen Digest dashboard online.

## Option 1: Streamlit Cloud (Recommended - Free & Easy)

Streamlit Cloud is the easiest way to deploy your dashboard for free.

### Steps:
1. **Push your code to GitHub** (if not already done)
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Sign in with GitHub**
4. **Click "New app"**
5. **Configure:**
   - Repository: `your-username/DegenDigest`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Python version: 3.11
6. **Click "Deploy"**

### Environment Variables (if needed):
Add these in the Streamlit Cloud settings:
- `APIFY_API_TOKEN`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `OPENAI_API_KEY`

## Option 2: Google Cloud Run (Production)

For production deployments with more control and scalability.

### Prerequisites:
- Google Cloud account
- gcloud CLI installed
- Docker installed

### Quick Deploy:
```bash
# Make sure you're authenticated
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Run the deployment script
./deploy.sh
```

### Manual Deploy:
```bash
# Build and push Docker image
docker build -f Dockerfile.dashboard -t gcr.io/YOUR_PROJECT_ID/degen_digest_dashboard:latest .
docker push gcr.io/YOUR_PROJECT_ID/degen_digest_dashboard:latest

# Deploy to Cloud Run
gcloud run deploy degen-digest-dashboard \
    --image gcr.io/YOUR_PROJECT_ID/degen_digest_dashboard:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 4Gi \
    --cpu 2
```

## Option 3: Docker Compose (Local/Server)

For running on your own server or locally.

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.dashboard.yml up -d
```

## Option 4: Railway (Alternative Cloud)

Railway is another great option for easy deployment.

1. **Go to [railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Deploy using the Dockerfile.dashboard**

## Environment Setup

Make sure your `.env` file contains the necessary API keys:

```bash
# Copy from example
cp .env.example .env

# Edit with your actual keys
nano .env
```

Required variables:
- `APIFY_API_TOKEN` - For Twitter scraping
- `TELEGRAM_API_ID` - For Telegram scraping
- `TELEGRAM_API_HASH` - For Telegram scraping
- `OPENAI_API_KEY` - For AI features

## Database Setup

The app will automatically create the SQLite database when first run. For production, consider using a cloud database like:

- **Google Cloud SQL**
- **AWS RDS**
- **PlanetScale**
- **Supabase**

## Monitoring & Logs

### Streamlit Cloud:
- Logs are available in the Streamlit Cloud dashboard

### Google Cloud Run:
```bash
# View logs
gcloud logs tail --service=degen-digest-dashboard --region=us-central1

# Monitor metrics
gcloud run services describe degen-digest-dashboard --region=us-central1
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Database Errors**: Check if the database file is writable
3. **API Errors**: Verify environment variables are set correctly
4. **Memory Issues**: Increase memory allocation in deployment settings

### Debug Mode:
```bash
# Run locally with debug info
streamlit run streamlit_app.py --logger.level debug
```

## Cost Estimation

- **Streamlit Cloud**: Free tier available
- **Google Cloud Run**: ~$5-20/month for moderate usage
- **Railway**: ~$5-15/month for moderate usage

## Security Considerations

1. **Environment Variables**: Never commit API keys to Git
2. **Database**: Use secure connections for production databases
3. **Authentication**: Consider adding user authentication for sensitive data
4. **HTTPS**: All cloud platforms provide HTTPS by default

## Next Steps

After deployment:
1. **Test all dashboard features**
2. **Set up automated data ingestion**
3. **Configure monitoring and alerts**
4. **Set up custom domain (optional)**
5. **Implement user authentication (if needed)** 