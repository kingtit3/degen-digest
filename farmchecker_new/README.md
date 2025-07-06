# FarmChecker.xyz - Crypto Intelligence Platform

A modern, clean news website that aggregates and displays crypto intelligence from Twitter, Reddit, News, and market data sources.

## Features

- **Real-time Data**: Pulls data directly from Cloud SQL database
- **Clean Design**: Modern, responsive news website aesthetic
- **Twitter Feed**: Scrollable feed of top Twitter posts with engagement metrics
- **System Status**: Live monitoring of crawler status and last run times
- **Analytics**: Visual charts showing data distribution and trends
- **Latest Digests**: Display of the most recent crypto digest
- **Auto-refresh**: Data updates every 5 minutes

## Architecture

```
Frontend (HTML/CSS/JS) → Flask API → Cloud SQL Database
```

- **Frontend**: Static HTML/CSS/JavaScript with Chart.js for visualizations
- **Backend**: Flask API server with PostgreSQL connection
- **Database**: Google Cloud SQL with consolidated data from all crawlers
- **Deployment**: Google Cloud Run for scalability

## Quick Start

### Prerequisites

- Google Cloud Project with Cloud SQL instance
- Docker installed
- gcloud CLI configured

### 1. Configure Database Connection

Update the database configuration in `server.py`:

```python
DB_CONFIG = {
    'host': 'your-cloud-sql-ip',
    'database': 'degendigest',
    'user': 'postgres',
    'password': 'your-password',
    'port': '5432'
}
```

### 2. Update Project ID

Edit `deploy.sh` and set your Google Cloud Project ID:

```bash
PROJECT_ID="your-actual-project-id"
```

### 3. Deploy

```bash
cd farmchecker_new
./deploy.sh
```

### 4. Access Your Website

The deployment script will output the URL where your website is available.

## Local Development

### Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export DB_HOST=your-cloud-sql-ip
export DB_NAME=degendigest
export DB_USER=postgres
export DB_PASSWORD=your-password
export DB_PORT=5432
```

3. Run the server:

```bash
python server.py
```

4. Open http://localhost:5000 in your browser

### Docker Development

```bash
docker build -t farmchecker .
docker run -p 5000:5000 farmchecker
```

## API Endpoints

- `GET /api/stats` - Overall statistics
- `GET /api/twitter-posts` - Top Twitter posts
- `GET /api/latest-digest` - Most recent digest
- `GET /api/system-status` - Crawler status
- `GET /api/digests` - All digests
- `GET /api/content/<source>` - Content by source

## Database Schema

The website expects the following tables in your Cloud SQL database:

### content_items

- id (primary key)
- title
- content
- author
- engagement_score
- upvotes
- comments
- created_at
- url
- source (twitter, reddit, news)

### digests

- id (primary key)
- title
- content
- created_at

## Customization

### Styling

- Edit `styles.css` to modify the appearance
- Uses Inter font family for modern typography
- Responsive design with mobile-first approach

### Data Sources

- Add new sources by updating the API endpoints
- Modify the frontend to display additional data types

### Charts

- Uses Chart.js for visualizations
- Customize charts in `app.js`

## Monitoring

The website includes:

- Real-time system status monitoring
- Last run times for each crawler
- Database connection health checks
- Auto-refresh functionality

## Security

- Database credentials stored as environment variables
- CORS enabled for API access
- Non-root Docker container
- Health checks for container monitoring

## Performance

- Static file serving for frontend assets
- Database connection pooling
- Gunicorn with multiple workers
- Cloud Run auto-scaling

## Troubleshooting

### Database Connection Issues

- Verify Cloud SQL instance is running
- Check network access and firewall rules
- Ensure credentials are correct

### Deployment Issues

- Check gcloud authentication
- Verify project ID is correct
- Ensure Docker is running

### Frontend Issues

- Check browser console for JavaScript errors
- Verify API endpoints are accessible
- Check CORS configuration

## Support

For issues or questions:

1. Check the logs in Google Cloud Console
2. Verify database connectivity
3. Test API endpoints directly
4. Review deployment configuration

## License

This project is part of the DegenDigest crypto intelligence platform.
