# Development Guide

This document provides comprehensive development information for the Degen Digest platform.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Git Workflow](#git-workflow)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)
- [Security Guidelines](#security-guidelines)
- [Contributing](#contributing)

## Development Setup

### Prerequisites

```bash
# Required software
- Python 3.11+
- Git
- Docker (optional)
- Node.js 18+ (for frontend development)

# Recommended tools
- VS Code with Python extension
- PyCharm Professional
- Postman (for API testing)
- DBeaver (for database management)
```

### Environment Setup

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/degen-digest.git
cd degen-digest
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-crawler.txt
pip install -r requirements-streamlit.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

#### 4. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables for development:

```bash
# Core configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_FORMAT=console

# Database
DATABASE_URL=sqlite:///output/degen_digest.db

# API keys (get from team lead)
OPENROUTER_API_KEY=your_openrouter_key
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password

# Google Cloud (optional for local development)
GOOGLE_CLOUD_PROJECT=your_project_id
GCS_BUCKET_NAME=degen-digest-data-dev
```

#### 5. Initialize Development Environment

```bash
# Create necessary directories
mkdir -p logs output tests/data

# Initialize database
python recreate_db.py

# Run initial setup
python setup_project.py
```

### Development Tools Setup

#### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

#### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

#### PyCharm Configuration

1. Set project interpreter to virtual environment
2. Configure pytest as test runner
3. Enable code inspection
4. Set up run configurations for main components

## Project Structure

```
degen-digest/
├── dashboard/                 # Streamlit dashboard application
│   ├── app.py                # Main dashboard application
│   ├── pages/                # Dashboard pages
│   │   ├── Analytics.py      # Analytics page
│   │   ├── Live_Feed.py      # Live feed page
│   │   └── Health_Monitor.py # Health monitoring page
│   └── components/           # Reusable dashboard components
├── scrapers/                 # Data collection modules
│   ├── twitter_playwright_enhanced.py  # Twitter crawler
│   ├── reddit_rss.py         # Reddit scraper
│   ├── telegram_telethon.py  # Telegram scraper
│   └── newsapi_headlines.py  # News API scraper
├── processor/                # Data processing and AI analysis
│   ├── classifier.py         # Content classification
│   ├── scorer.py             # Engagement scoring
│   ├── summarizer.py         # Content summarization
│   ├── viral_predictor.py    # Viral prediction
│   └── content_clustering.py # Content clustering
├── storage/                  # Database and storage layer
│   └── db.py                 # Database operations
├── utils/                    # Shared utilities
│   ├── enterprise_logging.py # Enterprise logging system
│   ├── health_monitor.py     # Health monitoring
│   ├── data_quality_monitor.py # Data quality monitoring
│   └── rate_limiter.py       # Rate limiting
├── config/                   # Configuration files
│   ├── app_config.yaml       # Application configuration
│   ├── keywords.py           # Keywords for filtering
│   └── influencers.py        # Influential accounts
├── scripts/                  # Automation and utility scripts
│   ├── automated_data_pipeline.py # Automated data processing
│   ├── cloud_storage_sync.py # Cloud storage synchronization
│   └── continuous_solana_crawler.py # Continuous crawling
├── tests/                    # Test suite
│   ├── conftest.py           # Test configuration
│   ├── test_crawler.py       # Crawler tests
│   ├── test_processor.py     # Processor tests
│   └── test_dashboard.py     # Dashboard tests
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   ├── CONFIGURATION.md     # Configuration guide
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── MONITORING.md        # Monitoring guide
├── logs/                     # Application logs
├── output/                   # Generated outputs
├── requirements.txt          # Main dependencies
├── requirements-crawler.txt  # Crawler dependencies
├── requirements-streamlit.txt # Dashboard dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Project configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── Dockerfile               # Main Dockerfile
├── Dockerfile.crawler       # Crawler Dockerfile
├── Dockerfile.dashboard     # Dashboard Dockerfile
└── docker-compose.yml       # Docker Compose configuration
```

## Coding Standards

### Python Style Guide

Follow PEP 8 with the following additions:

#### Code Formatting

```python
# Use Black for code formatting
# Line length: 88 characters
# Use double quotes for strings
# Use trailing commas in multi-line structures

# Good
def process_data(
    data: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Process data with given options."""
    pass

# Bad
def process_data(data:List[Dict[str,Any]],options:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
    pass
```

#### Type Hints

```python
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Always use type hints
def process_tweets(
    tweets: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Union[int, List[Dict[str, Any]]]]:
    """Process tweets with optional filters."""
    pass

# Use type aliases for complex types
TweetData = Dict[str, Union[str, int, float, datetime]]
TweetList = List[TweetData]

def analyze_tweets(tweets: TweetList) -> Dict[str, float]:
    """Analyze tweet sentiment and engagement."""
    pass
```

#### Docstrings

```python
def calculate_engagement_score(
    likes: int,
    retweets: int,
    replies: int,
    followers: int,
) -> float:
    """
    Calculate engagement score for a tweet.

    Args:
        likes: Number of likes
        retweets: Number of retweets
        replies: Number of replies
        followers: Number of followers

    Returns:
        Engagement score between 0 and 1

    Raises:
        ValueError: If followers is zero

    Example:
        >>> calculate_engagement_score(100, 50, 25, 10000)
        0.0175
    """
    if followers == 0:
        raise ValueError("Followers cannot be zero")

    total_engagement = likes + retweets + replies
    return total_engagement / followers
```

#### Error Handling

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_api_call(func):
    """Decorator for safe API calls with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}", exc_info=True)
            raise
        except ValueError as e:
            logger.warning(f"Invalid input: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error: {e}", exc_info=True)
            raise

    return wrapper

@safe_api_call
def fetch_twitter_data(username: str) -> Optional[Dict[str, Any]]:
    """Fetch Twitter data for given username."""
    # Implementation
    pass
```

### Logging Standards

```python
from utils.enterprise_logging import get_logger, log_function_call

logger = get_logger(__name__)

@log_function_call()
def process_data_batch(
    data: List[Dict[str, Any]],
    batch_id: str,
) -> Dict[str, Any]:
    """Process a batch of data with comprehensive logging."""

    logger.info(
        "Starting data batch processing",
        batch_id=batch_id,
        batch_size=len(data),
        data_types=list(set(item.get('type') for item in data))
    )

    try:
        # Processing logic
        result = process_items(data)

        logger.info(
            "Data batch processing completed",
            batch_id=batch_id,
            processed_count=len(result),
            success=True
        )

        return result

    except Exception as e:
        logger.error(
            "Data batch processing failed",
            batch_id=batch_id,
            error=str(e),
            error_type=type(e).__name__,
            success=False
        )
        raise
```

### Configuration Management

```python
import os
from typing import Dict, Any
from pathlib import Path
import yaml

class ConfigManager:
    """Manage application configuration."""

    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables
        config = self._override_with_env(config)

        return config

    def _override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override config values with environment variables."""
        env_mappings = {
            'LOG_LEVEL': 'logging.level',
            'DATABASE_URL': 'database.url',
            'OPENROUTER_API_KEY': 'ai.api_key',
        }

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config, config_path, env_value)

        return config

    def _set_nested_value(self, obj: Dict[str, Any], path: str, value: Any):
        """Set nested dictionary value using dot notation."""
        keys = path.split('.')
        for key in keys[:-1]:
            obj = obj.setdefault(key, {})
        obj[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

# Usage
config = ConfigManager()
log_level = config.get('logging.level', 'INFO')
api_key = config.get('ai.api_key')
```

## Testing

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_scrapers/       # Scraper unit tests
│   ├── test_processor/      # Processor unit tests
│   └── test_utils/          # Utility unit tests
├── integration/             # Integration tests
│   ├── test_data_pipeline/  # Data pipeline tests
│   ├── test_api/            # API integration tests
│   └── test_database/       # Database integration tests
├── e2e/                     # End-to-end tests
│   ├── test_crawler_e2e.py  # Crawler end-to-end tests
│   └── test_dashboard_e2e.py # Dashboard end-to-end tests
└── fixtures/                # Test data and fixtures
    ├── sample_tweets.json   # Sample tweet data
    ├── sample_reddit.json   # Sample Reddit data
    └── test_config.yaml     # Test configuration
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_tweets():
    """Load sample tweet data."""
    import json
    with open("tests/fixtures/sample_tweets.json", "r") as f:
        return json.load(f)

@pytest.fixture
def mock_twitter_api():
    """Mock Twitter API responses."""
    with patch('scrapers.twitter_playwright_enhanced.TwitterAPI') as mock:
        mock.return_value.get_tweets.return_value = [
            {
                "id": "12345",
                "text": "Test tweet",
                "username": "test_user",
                "likes": 10,
                "retweets": 5,
                "replies": 2
            }
        ]
        yield mock

@pytest.fixture
def test_database():
    """Create test database."""
    import sqlite3
    db_path = ":memory:"
    conn = sqlite3.connect(db_path)

    # Create test tables
    conn.execute("""
        CREATE TABLE tweets (
            id TEXT PRIMARY KEY,
            text TEXT,
            username TEXT,
            likes INTEGER,
            retweets INTEGER,
            replies INTEGER,
            created_at TIMESTAMP
        )
    """)

    yield conn
    conn.close()
```

### Unit Tests

```python
# tests/unit/test_scrapers/test_twitter_scraper.py
import pytest
from unittest.mock import Mock, patch
from scrapers.twitter_playwright_enhanced import TwitterScraper

class TestTwitterScraper:
    """Test Twitter scraper functionality."""

    def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = TwitterScraper()
        assert scraper is not None
        assert hasattr(scraper, 'browser')

    def test_login_success(self, mock_twitter_api):
        """Test successful login."""
        scraper = TwitterScraper()
        result = scraper.login("test_user", "test_pass")
        assert result is True

    def test_login_failure(self, mock_twitter_api):
        """Test login failure."""
        mock_twitter_api.return_value.login.return_value = False

        scraper = TwitterScraper()
        result = scraper.login("test_user", "wrong_pass")
        assert result is False

    def test_extract_tweet_data(self, sample_tweets):
        """Test tweet data extraction."""
        scraper = TwitterScraper()

        for tweet_html in sample_tweets:
            tweet_data = scraper.extract_tweet_data(tweet_html)

            assert 'id' in tweet_data
            assert 'text' in tweet_data
            assert 'username' in tweet_data
            assert 'likes' in tweet_data
            assert 'retweets' in tweet_data
            assert 'replies' in tweet_data

    @pytest.mark.parametrize("input_text,expected_sentiment", [
        ("I love Solana!", 0.8),
        ("Solana is terrible", -0.6),
        ("Solana price update", 0.0),
    ])
    def test_sentiment_analysis(self, input_text, expected_sentiment):
        """Test sentiment analysis with various inputs."""
        scraper = TwitterScraper()
        sentiment = scraper.analyze_sentiment(input_text)
        assert abs(sentiment - expected_sentiment) < 0.2
```

### Integration Tests

```python
# tests/integration/test_data_pipeline/test_pipeline.py
import pytest
from processor.classifier import ContentClassifier
from processor.scorer import EngagementScorer
from processor.summarizer import ContentSummarizer

class TestDataPipeline:
    """Test data processing pipeline."""

    def test_full_pipeline(self, sample_tweets):
        """Test complete data processing pipeline."""
        # Initialize components
        classifier = ContentClassifier()
        scorer = EngagementScorer()
        summarizer = ContentSummarizer()

        # Process tweets
        processed_tweets = []

        for tweet in sample_tweets:
            # Classify content
            category = classifier.classify(tweet['text'])

            # Score engagement
            score = scorer.score(tweet)

            # Add processed data
            processed_tweet = {
                **tweet,
                'category': category,
                'engagement_score': score
            }
            processed_tweets.append(processed_tweet)

        # Verify results
        assert len(processed_tweets) == len(sample_tweets)

        for tweet in processed_tweets:
            assert 'category' in tweet
            assert 'engagement_score' in tweet
            assert 0 <= tweet['engagement_score'] <= 1

    def test_pipeline_performance(self, sample_tweets):
        """Test pipeline performance with large dataset."""
        import time

        classifier = ContentClassifier()
        scorer = EngagementScorer()

        start_time = time.time()

        for tweet in sample_tweets:
            classifier.classify(tweet['text'])
            scorer.score(tweet)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process 1000 tweets in under 10 seconds
        assert processing_time < 10.0
        assert len(sample_tweets) == 1000
```

### End-to-End Tests

```python
# tests/e2e/test_crawler_e2e.py
import pytest
import time
import requests
from pathlib import Path

class TestCrawlerE2E:
    """End-to-end tests for crawler functionality."""

    @pytest.fixture(autouse=True)
    def setup_crawler(self):
        """Setup crawler for testing."""
        # Start crawler service
        self.crawler_url = "http://localhost:8080"

        # Wait for service to be ready
        for _ in range(30):
            try:
                response = requests.get(f"{self.crawler_url}/status")
                if response.status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(1)
        else:
            pytest.fail("Crawler service not ready")

    def test_crawler_start_stop(self):
        """Test crawler start and stop functionality."""
        # Start crawler
        response = requests.post(f"{self.crawler_url}/start", json={
            "max_tweets": 10,
            "keywords": ["solana"]
        })
        assert response.status_code == 200

        # Check status
        response = requests.get(f"{self.crawler_url}/status")
        assert response.status_code == 200
        status = response.json()
        assert status['data']['crawler_running'] is True

        # Wait for completion
        for _ in range(60):  # Wait up to 60 seconds
            response = requests.get(f"{self.crawler_url}/status")
            status = response.json()
            if not status['data']['crawler_running']:
                break
            time.sleep(1)

        # Verify data was collected
        assert status['data']['tweets_collected'] > 0

        # Stop crawler
        response = requests.post(f"{self.crawler_url}/stop")
        assert response.status_code == 200

    def test_data_flow(self):
        """Test complete data flow from crawler to storage."""
        # Start crawler
        requests.post(f"{self.crawler_url}/start", json={
            "max_tweets": 5,
            "keywords": ["solana"]
        })

        # Wait for completion
        time.sleep(30)

        # Check data files
        data_files = list(Path("output").glob("twitter_playwright_enhanced_*.json"))
        assert len(data_files) > 0

        # Verify data format
        import json
        with open(data_files[-1], 'r') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) > 0

        for tweet in data:
            assert 'id' in tweet
            assert 'text' in tweet
            assert 'username' in tweet
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_scrapers/test_twitter_scraper.py

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l
```

## Code Quality

### Linting

```bash
# Install linting tools
pip install ruff black isort mypy

# Run Ruff (fast Python linter)
ruff check .

# Fix issues automatically
ruff check . --fix

# Run Black (code formatter)
black .

# Run isort (import sorter)
isort .

# Run mypy (type checker)
mypy .
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

### Code Review Checklist

- [ ] Code follows PEP 8 and project style guide
- [ ] Type hints are used for all functions
- [ ] Docstrings are present and complete
- [ ] Error handling is appropriate
- [ ] Logging is implemented
- [ ] Tests are written and passing
- [ ] No hardcoded secrets or credentials
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed
- [ ] Documentation is updated

## Git Workflow

### Branch Naming

```
feature/component-description
bugfix/issue-description
hotfix/critical-fix
release/version-number
```

### Commit Messages

```
feat: add new crawler functionality
fix: resolve database connection issue
docs: update API documentation
test: add unit tests for processor
refactor: improve error handling
style: format code with black
perf: optimize data processing
chore: update dependencies
```

### Pull Request Process

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**

   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Run Tests**

   ```bash
   pytest
   ruff check .
   mypy .
   ```

4. **Push and Create PR**

   ```bash
   git push origin feature/new-feature
   # Create PR on GitHub/GitLab
   ```

5. **Code Review**

   - Address review comments
   - Update documentation if needed
   - Ensure all tests pass

6. **Merge**
   - Squash commits if needed
   - Delete feature branch

### Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

# Run pre-commit hooks
pre-commit run --all-files

# Run tests
pytest tests/unit/ --tb=short

echo "Pre-commit checks passed!"
```

## Debugging

### Debug Configuration

```python
# utils/debug.py
import logging
import traceback
from typing import Any, Dict
from functools import wraps

def debug_function(func):
    """Decorator to add debugging information."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)

        logger.debug(
            f"Entering {func.__name__}",
            extra={
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
        )

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.error(
                f"Error in {func.__name__}: {e}",
                extra={
                    'function': func.__name__,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
            )
            raise

    return wrapper

def debug_variables(**variables):
    """Debug helper to log variable values."""
    logger = logging.getLogger(__name__)

    for name, value in variables.items():
        logger.debug(f"DEBUG {name}: {value}")

# Usage
@debug_function
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    debug_variables(data_size=len(data), data_keys=list(data.keys()))
    # Processing logic
    return result
```

### VS Code Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "LOG_LEVEL": "DEBUG"
      }
    },
    {
      "name": "Python: Dashboard",
      "type": "python",
      "request": "launch",
      "program": "start_dashboard.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "LOG_LEVEL": "DEBUG"
      }
    },
    {
      "name": "Python: Crawler",
      "type": "python",
      "request": "launch",
      "program": "crawler_server.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

### Logging for Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use structured logging for debugging
from utils.enterprise_logging import get_logger

logger = get_logger(__name__)

def debug_data_processing(data):
    """Debug data processing with detailed logging."""
    logger.debug(
        "Processing data",
        data_type=type(data).__name__,
        data_length=len(data) if hasattr(data, '__len__') else 'N/A',
        data_keys=list(data.keys()) if isinstance(data, dict) else 'N/A'
    )

    # Process data with step-by-step logging
    for i, item in enumerate(data):
        logger.debug(f"Processing item {i}", item_id=item.get('id'))

        try:
            result = process_item(item)
            logger.debug(f"Item {i} processed successfully", result=result)
        except Exception as e:
            logger.error(f"Failed to process item {i}", error=str(e))
            raise
```

## Performance Optimization

### Profiling

```python
# utils/profiler.py
import cProfile
import pstats
import io
import time
from functools import wraps
from typing import Callable, Any

def profile_function(func: Callable) -> Callable:
    """Decorator to profile function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        pr = cProfile.Profile()
        pr.enable()

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        pr.disable()

        # Print profiling results
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(20)

        print(f"Function: {func.__name__}")
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        print("Profiling results:")
        print(s.getvalue())

        return result

    return wrapper

def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        result = func(*args, **kwargs)

        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory

        print(f"Function: {func.__name__}")
        print(f"Memory used: {memory_used:.2f} MB")

        return result

    return wrapper

# Usage
@profile_function
@profile_memory
def process_large_dataset(data):
    """Process large dataset with profiling."""
    # Processing logic
    pass
```

### Performance Monitoring

```python
# utils/performance_monitor.py
import time
import threading
from typing import Dict, Any, List
from collections import defaultdict

class PerformanceMonitor:
    """Monitor application performance."""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()

    def time_function(self, func_name: str):
        """Decorator to time function execution."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception:
                    success = False
                    raise
                finally:
                    end_time = time.time()
                    duration = end_time - start_time

                    with self.lock:
                        self.metrics[func_name].append({
                            'duration': duration,
                            'success': success,
                            'timestamp': time.time()
                        })

                return result
            return wrapper
        return decorator

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}

        with self.lock:
            for func_name, metrics in self.metrics.items():
                if metrics:
                    durations = [m['duration'] for m in metrics]
                    success_rate = sum(1 for m in metrics if m['success']) / len(metrics)

                    summary[func_name] = {
                        'count': len(metrics),
                        'avg_duration': sum(durations) / len(durations),
                        'min_duration': min(durations),
                        'max_duration': max(durations),
                        'success_rate': success_rate
                    }

        return summary

# Global performance monitor
performance_monitor = PerformanceMonitor()

# Usage
@performance_monitor.time_function('data_processing')
def process_data(data):
    """Process data with performance monitoring."""
    # Processing logic
    pass
```

## Security Guidelines

### Input Validation

```python
import re
from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class ValidationError(Exception):
    """Custom validation error."""
    field: str
    message: str

class InputValidator:
    """Validate and sanitize input data."""

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username format."""
        if not username:
            raise ValidationError("username", "Username cannot be empty")

        if len(username) > 50:
            raise ValidationError("username", "Username too long")

        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("username", "Invalid username format")

        return username.strip()

    @staticmethod
    def validate_tweet_content(content: str) -> str:
        """Validate tweet content."""
        if not content:
            raise ValidationError("content", "Content cannot be empty")

        if len(content) > 280:
            raise ValidationError("content", "Content too long")

        # Remove potentially dangerous content
        content = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

        return content.strip()

    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """Validate API key format."""
        if not api_key:
            raise ValidationError("api_key", "API key cannot be empty")

        if len(api_key) < 32:
            raise ValidationError("api_key", "API key too short")

        return api_key.strip()

# Usage
validator = InputValidator()

try:
    username = validator.validate_username(user_input)
    content = validator.validate_tweet_content(tweet_content)
    api_key = validator.validate_api_key(api_key_input)
except ValidationError as e:
    logger.error(f"Validation error: {e.field} - {e.message}")
    raise
```

### Secure Configuration

```python
import os
from typing import Optional
from cryptography.fernet import Fernet

class SecureConfig:
    """Secure configuration management."""

    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv('ENCRYPTION_KEY')
        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key.encode())

    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive configuration value."""
        if not self.encryption_key:
            return value

        return self.cipher.encrypt(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive configuration value."""
        if not self.encryption_key:
            return encrypted_value

        return self.cipher.decrypt(encrypted_value.encode()).decode()

    def get_secure_config(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value with encryption support."""
        value = os.getenv(key, default)

        if value and value.startswith('encrypted:'):
            encrypted_value = value[10:]  # Remove 'encrypted:' prefix
            return self.decrypt_value(encrypted_value)

        return value

# Usage
secure_config = SecureConfig()

# Store encrypted value
api_key = "your-secret-api-key"
encrypted_api_key = secure_config.encrypt_value(api_key)
print(f"encrypted:{encrypted_api_key}")

# Retrieve decrypted value
decrypted_api_key = secure_config.get_secure_config('API_KEY')
```

### Rate Limiting

```python
import time
import threading
from typing import Dict, Tuple
from collections import defaultdict

class RateLimiter:
    """Rate limiting implementation."""

    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed."""
        now = time.time()

        with self.lock:
            # Clean old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]

            # Check if limit exceeded
            if len(self.requests[key]) >= limit:
                return False

            # Add current request
            self.requests[key].append(now)
            return True

    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests allowed."""
        now = time.time()

        with self.lock:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]

            return max(0, limit - len(self.requests[key]))

# Usage
rate_limiter = RateLimiter()

def api_call_with_rate_limit(user_id: str):
    """Make API call with rate limiting."""
    if not rate_limiter.is_allowed(user_id, limit=100, window=3600):
        raise Exception("Rate limit exceeded")

    # Make API call
    pass
```

## Contributing

### Contribution Guidelines

1. **Fork the Repository**

   ```bash
   git clone https://github.com/your-username/degen-digest.git
   cd degen-digest
   ```

2. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**

   - Follow coding standards
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

4. **Commit Changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request
   ```

### Development Workflow

```bash
# Daily development workflow
git pull origin main
git checkout -b feature/daily-work

# Make changes
# Run tests
pytest

# Run linting
ruff check .
black .
isort .

# Commit changes
git add .
git commit -m "feat: implement new feature"

# Push changes
git push origin feature/daily-work

# Create pull request
# Address review comments
# Merge when approved
```

### Code Review Process

1. **Self Review**

   - Run all tests
   - Check code quality
   - Review documentation
   - Test functionality

2. **Peer Review**

   - Request review from team member
   - Address feedback
   - Update code as needed

3. **Final Review**

   - Senior developer review
   - Security review if needed
   - Performance review if needed

4. **Merge**
   - Squash commits if needed
   - Update documentation
   - Deploy to staging

---

_For more information, see the [API Documentation](API.md) and [Deployment Guide](DEPLOYMENT.md)._
