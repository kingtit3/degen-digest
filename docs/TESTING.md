# Testing Guide

This document provides comprehensive testing information for the Degen Digest platform.

## Table of Contents

- [Overview](#overview)
- [Testing Strategy](#testing-strategy)
- [Test Types](#test-types)
- [Test Environment](#test-environment)
- [Test Automation](#test-automation)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Data Quality Testing](#data-quality-testing)
- [Continuous Testing](#continuous-testing)
- [Best Practices](#best-practices)

## Overview

The Degen Digest platform implements a comprehensive testing strategy to ensure quality, reliability, and security across all components.

### Testing Principles

- **Test Early, Test Often** - Testing integrated into development workflow
- **Automation First** - Automated testing for all critical paths
- **Comprehensive Coverage** - Tests for all components and scenarios
- **Performance Focus** - Performance testing for scalability
- **Security Testing** - Security testing for vulnerability detection
- **Data Quality** - Testing for data accuracy and integrity

### Testing Pyramid

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Pyramid                          │
├─────────────────────────────────────────────────────────────┤
│                    E2E Tests (Few)                         │
│                 • User journey tests                        │
│                 • Integration tests                         │
│                 • Performance tests                         │
├─────────────────────────────────────────────────────────────┤
│                  Integration Tests (Some)                   │
│                 • API tests                                 │
│                 • Database tests                            │
│                 • External service tests                    │
├─────────────────────────────────────────────────────────────┤
│                   Unit Tests (Many)                         │
│                 • Function tests                            │
│                 • Component tests                           │
│                 • Utility tests                             │
└─────────────────────────────────────────────────────────────┘
```

## Testing Strategy

### Test Categories

1. **Unit Tests** - Test individual functions and components
2. **Integration Tests** - Test component interactions
3. **API Tests** - Test API endpoints and responses
4. **Performance Tests** - Test system performance and scalability
5. **Security Tests** - Test security vulnerabilities
6. **Data Quality Tests** - Test data accuracy and integrity
7. **End-to-End Tests** - Test complete user workflows

### Test Coverage Goals

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: All critical paths
- **API Tests**: All endpoints and error cases
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning
- **Data Quality Tests**: Data validation rules

## Test Types

### Unit Tests

#### Test Structure

```python
# tests/unit/test_crawler.py
import pytest
from unittest.mock import Mock, patch
from scrapers.twitter_playwright_enhanced import TwitterCrawler

class TestTwitterCrawler:
    """Test Twitter crawler functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.crawler = TwitterCrawler()
        self.mock_browser = Mock()

    def test_crawler_initialization(self):
        """Test crawler initialization"""
        assert self.crawler is not None
        assert hasattr(self.crawler, 'browser')
        assert hasattr(self.crawler, 'page')

    @patch('playwright.sync_api.sync_playwright')
    def test_login_success(self, mock_playwright):
        """Test successful login"""
        # Setup mock
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value.goto.return_value = None

        # Test login
        result = self.crawler.login("testuser", "testpass")
        assert result is True

    def test_login_failure(self):
        """Test login failure"""
        with pytest.raises(Exception):
            self.crawler.login("invalid", "invalid")

    def test_extract_tweets(self):
        """Test tweet extraction"""
        mock_page = Mock()
        mock_page.query_selector_all.return_value = [
            Mock(text_content="Test tweet 1"),
            Mock(text_content="Test tweet 2")
        ]

        tweets = self.crawler.extract_tweets(mock_page)
        assert len(tweets) == 2
        assert "Test tweet 1" in tweets
        assert "Test tweet 2" in tweets

    def test_save_tweets(self):
        """Test tweet saving"""
        tweets = ["Tweet 1", "Tweet 2"]
        result = self.crawler.save_tweets(tweets, "test_file.json")
        assert result is True

        # Verify file was created
        import os
        assert os.path.exists("test_file.json")
```

#### Test Utilities

```python
# tests/utils/test_helpers.py
import pytest
import tempfile
import json
from pathlib import Path

class TestHelpers:
    """Test helper utilities"""

    @staticmethod
    def create_temp_file(content: dict) -> str:
        """Create temporary file with content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(content, f)
            return f.name

    @staticmethod
    def load_test_data(filename: str) -> dict:
        """Load test data from fixtures"""
        fixture_path = Path(__file__).parent / 'fixtures' / filename
        with open(fixture_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def assert_dict_contains(actual: dict, expected: dict):
        """Assert that actual dict contains expected keys and values"""
        for key, value in expected.items():
            assert key in actual, f"Key '{key}' not found in actual dict"
            assert actual[key] == value, f"Value for key '{key}' does not match"
```

### Integration Tests

#### API Integration Tests

```python
# tests/integration/test_api.py
import pytest
import requests
from unittest.mock import patch

class TestAPIEndpoints:
    """Test API endpoint integration"""

    def setup_method(self):
        """Setup test environment"""
        self.base_url = "http://localhost:8080"
        self.session = requests.Session()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{self.base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_digest_generation(self):
        """Test digest generation endpoint"""
        data = {
            "date": "2025-07-03",
            "sources": ["twitter", "reddit"],
            "format": "json"
        }

        response = self.session.post(f"{self.base_url}/api/digest", json=data)
        assert response.status_code == 200

        result = response.json()
        assert "digest" in result
        assert "content" in result["digest"]

    def test_crawler_control(self):
        """Test crawler control endpoints"""
        # Start crawler
        response = self.session.post(f"{self.base_url}/start")
        assert response.status_code == 200

        # Check status
        response = self.session.get(f"{self.base_url}/status")
        assert response.status_code == 200
        assert response.json()["crawler_running"] is True

        # Stop crawler
        response = self.session.post(f"{self.base_url}/stop")
        assert response.status_code == 200

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid request
        response = self.session.post(f"{self.base_url}/api/digest", json={})
        assert response.status_code == 400

        # Test invalid endpoint
        response = self.session.get(f"{self.base_url}/invalid")
        assert response.status_code == 404
```

#### Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
import sqlite3
from storage.db import Database

class TestDatabaseIntegration:
    """Test database integration"""

    def setup_method(self):
        """Setup test database"""
        self.db = Database(":memory:")  # Use in-memory database for testing
        self.db.create_tables()

    def test_tweet_storage(self):
        """Test tweet storage and retrieval"""
        # Insert test tweet
        tweet_data = {
            "id": "12345",
            "text": "Test tweet",
            "user": "testuser",
            "timestamp": "2025-07-03T10:00:00Z",
            "likes": 10,
            "retweets": 5
        }

        self.db.insert_tweet(tweet_data)

        # Retrieve tweet
        stored_tweet = self.db.get_tweet("12345")
        assert stored_tweet is not None
        assert stored_tweet["text"] == "Test tweet"
        assert stored_tweet["user"] == "testuser"

    def test_bulk_operations(self):
        """Test bulk database operations"""
        tweets = [
            {"id": "1", "text": "Tweet 1", "user": "user1"},
            {"id": "2", "text": "Tweet 2", "user": "user2"},
            {"id": "3", "text": "Tweet 3", "user": "user3"}
        ]

        # Bulk insert
        self.db.bulk_insert_tweets(tweets)

        # Verify all tweets stored
        all_tweets = self.db.get_all_tweets()
        assert len(all_tweets) == 3

    def test_data_consistency(self):
        """Test data consistency constraints"""
        # Test unique constraint
        tweet_data = {"id": "123", "text": "Test", "user": "user1"}
        self.db.insert_tweet(tweet_data)

        # Try to insert duplicate
        with pytest.raises(sqlite3.IntegrityError):
            self.db.insert_tweet(tweet_data)
```

### Performance Tests

#### Load Testing

```python
# tests/performance/test_load.py
import pytest
import time
import concurrent.futures
import requests
from locust import HttpUser, task, between

class LoadTest:
    """Load testing for API endpoints"""

    def test_concurrent_requests(self):
        """Test concurrent API requests"""
        base_url = "http://localhost:8080"
        num_requests = 100
        concurrent_users = 10

        def make_request():
            response = requests.get(f"{base_url}/health")
            return response.status_code == 200

        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in futures]

        # Verify all requests succeeded
        assert all(results)

    def test_response_time(self):
        """Test API response times"""
        base_url = "http://localhost:8080"
        max_response_time = 1.0  # 1 second

        start_time = time.time()
        response = requests.get(f"{base_url}/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < max_response_time

    def test_digest_generation_performance(self):
        """Test digest generation performance"""
        base_url = "http://localhost:8080"
        data = {
            "date": "2025-07-03",
            "sources": ["twitter", "reddit"],
            "format": "json"
        }

        start_time = time.time()
        response = requests.post(f"{base_url}/api/digest", json=data)
        end_time = time.time()

        generation_time = end_time - start_time
        assert response.status_code == 200
        assert generation_time < 30.0  # 30 seconds max
```

#### Locust Load Testing

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class DegenDigestUser(HttpUser):
    """Locust user for load testing"""

    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")

    @task(2)
    def get_digest(self):
        """Get digest endpoint"""
        data = {
            "date": "2025-07-03",
            "sources": ["twitter"],
            "format": "json"
        }
        self.client.post("/api/digest", json=data)

    @task(1)
    def crawler_control(self):
        """Crawler control endpoints"""
        self.client.get("/status")
        self.client.post("/start")
        self.client.post("/stop")
```

### Security Tests

#### Vulnerability Testing

```python
# tests/security/test_vulnerabilities.py
import pytest
import requests
from utils.enterprise_logging import get_logger

logger = get_logger('security_tests')

class TestSecurityVulnerabilities:
    """Test for security vulnerabilities"""

    def setup_method(self):
        """Setup test environment"""
        self.base_url = "http://localhost:8080"
        self.session = requests.Session()

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        # Test SQL injection in query parameters
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]

        for malicious_input in malicious_inputs:
            response = self.session.get(f"{self.base_url}/api/search?q={malicious_input}")
            # Should not cause database errors
            assert response.status_code in [200, 400, 404]

    def test_xss_vulnerability(self):
        """Test for XSS vulnerabilities"""
        # Test XSS in input fields
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]

        for payload in xss_payloads:
            data = {"content": payload}
            response = self.session.post(f"{self.base_url}/api/content", json=data)
            # Response should not contain the script
            assert "<script>" not in response.text

    def test_csrf_protection(self):
        """Test CSRF protection"""
        # Test without CSRF token
        data = {"action": "delete", "id": "123"}
        response = self.session.post(f"{self.base_url}/api/admin", json=data)
        # Should be rejected
        assert response.status_code == 403

    def test_rate_limiting(self):
        """Test rate limiting"""
        # Make many requests quickly
        for _ in range(100):
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 429:  # Rate limited
                break
        else:
            pytest.fail("Rate limiting not working")

    def test_authentication_bypass(self):
        """Test authentication bypass attempts"""
        # Test accessing protected endpoints without auth
        protected_endpoints = [
            "/api/admin",
            "/api/users",
            "/api/settings"
        ]

        for endpoint in protected_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            assert response.status_code == 401

    def test_input_validation(self):
        """Test input validation"""
        # Test various malicious inputs
        malicious_inputs = [
            {"email": "invalid-email"},
            {"password": "123"},  # Too short
            {"username": "a" * 1000},  # Too long
            {"data": {"__proto__": {"admin": True}}}  # Prototype pollution
        ]

        for input_data in malicious_inputs:
            response = self.session.post(f"{self.base_url}/api/register", json=input_data)
            assert response.status_code == 400
```

### Data Quality Tests

#### Data Validation Tests

```python
# tests/data_quality/test_data_validation.py
import pytest
import json
from pathlib import Path
from utils.data_quality_monitor import DataQualityMonitor

class TestDataQuality:
    """Test data quality and validation"""

    def setup_method(self):
        """Setup test environment"""
        self.quality_monitor = DataQualityMonitor()
        self.test_data_dir = Path(__file__).parent / "fixtures"

    def test_tweet_data_quality(self):
        """Test tweet data quality"""
        # Load test tweet data
        with open(self.test_data_dir / "sample_tweets.json", "r") as f:
            tweets = json.load(f)

        # Validate tweet structure
        for tweet in tweets:
            assert "id" in tweet
            assert "text" in tweet
            assert "user" in tweet
            assert "timestamp" in tweet

            # Validate data types
            assert isinstance(tweet["id"], str)
            assert isinstance(tweet["text"], str)
            assert isinstance(tweet["user"], str)
            assert len(tweet["text"]) > 0
            assert len(tweet["text"]) <= 280  # Twitter limit

    def test_data_completeness(self):
        """Test data completeness"""
        # Test for missing required fields
        incomplete_data = [
            {"id": "123", "text": "Test"},  # Missing user
            {"id": "123", "user": "test"},  # Missing text
            {"text": "Test", "user": "test"}  # Missing id
        ]

        for data in incomplete_data:
            issues = self.quality_monitor.check_completeness(data)
            assert len(issues) > 0

    def test_data_consistency(self):
        """Test data consistency"""
        # Test for inconsistent data
        inconsistent_data = [
            {"id": "123", "text": "Test", "user": "user1", "likes": -1},  # Negative likes
            {"id": "123", "text": "Test", "user": "user1", "timestamp": "invalid-date"},  # Invalid date
            {"id": "123", "text": "", "user": "user1"}  # Empty text
        ]

        for data in inconsistent_data:
            issues = self.quality_monitor.check_consistency(data)
            assert len(issues) > 0

    def test_data_duplicates(self):
        """Test for duplicate data"""
        duplicate_data = [
            {"id": "123", "text": "Test 1", "user": "user1"},
            {"id": "123", "text": "Test 2", "user": "user1"},  # Same ID
            {"id": "124", "text": "Test 1", "user": "user1"}  # Same text
        ]

        duplicates = self.quality_monitor.find_duplicates(duplicate_data)
        assert len(duplicates) > 0
```

## Test Environment

### Test Configuration

```python
# tests/conftest.py
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "database_url": "sqlite:///:memory:",
        "log_level": "DEBUG",
        "test_mode": True,
        "api_keys": {
            "openrouter": "test_key",
            "twitter": "test_key"
        }
    }

@pytest.fixture(scope="function")
def temp_dir():
    """Temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture(scope="function")
def test_data():
    """Test data fixtures"""
    return {
        "tweets": [
            {"id": "1", "text": "Test tweet 1", "user": "user1"},
            {"id": "2", "text": "Test tweet 2", "user": "user2"}
        ],
        "users": [
            {"id": "user1", "name": "User 1"},
            {"id": "user2", "name": "User 2"}
        ]
    }

@pytest.fixture(scope="function")
def mock_external_services():
    """Mock external services"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}
        yield mock_get
```

### Test Database Setup

```python
# tests/database/conftest.py
import pytest
import sqlite3
from storage.db import Database

@pytest.fixture(scope="function")
def test_database():
    """Test database fixture"""
    db = Database(":memory:")
    db.create_tables()

    # Insert test data
    test_data = [
        {"id": "1", "text": "Test tweet 1", "user": "user1"},
        {"id": "2", "text": "Test tweet 2", "user": "user2"}
    ]

    for tweet in test_data:
        db.insert_tweet(tweet)

    yield db

    # Cleanup
    db.close()
```

## Test Automation

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          ruff check .
          ruff format --check .

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=. --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Run security tests
        run: |
          pytest tests/security/ -v

      - name: Run performance tests
        run: |
          pytest tests/performance/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Test Scripts

```bash
#!/bin/bash
# scripts/run_tests.sh

echo "Running comprehensive test suite..."

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit/ -v --cov=. --cov-report=html

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration/ -v

# Run security tests
echo "Running security tests..."
python -m pytest tests/security/ -v

# Run performance tests
echo "Running performance tests..."
python -m pytest tests/performance/ -v

# Run data quality tests
echo "Running data quality tests..."
python -m pytest tests/data_quality/ -v

# Generate test report
echo "Generating test report..."
python scripts/generate_test_report.py

echo "Test suite completed!"
```

## Continuous Testing

### Automated Testing

```python
# scripts/continuous_testing.py
import time
import subprocess
import sys
from pathlib import Path
from utils.enterprise_logging import get_logger

logger = get_logger('continuous_testing')

class ContinuousTester:
    """Continuous testing system"""

    def __init__(self):
        self.test_results = []
        self.failure_count = 0

    def run_test_suite(self):
        """Run complete test suite"""
        logger.info("Starting continuous test suite")

        test_commands = [
            ["python", "-m", "pytest", "tests/unit/", "-v"],
            ["python", "-m", "pytest", "tests/integration/", "-v"],
            ["python", "-m", "pytest", "tests/security/", "-v"],
            ["python", "-m", "pytest", "tests/performance/", "-v"]
        ]

        for command in test_commands:
            result = self.run_command(command)
            self.test_results.append(result)

            if result["returncode"] != 0:
                self.failure_count += 1
                logger.error(f"Test command failed: {' '.join(command)}")

        self.generate_report()

    def run_command(self, command):
        """Run a test command"""
        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
        except subprocess.TimeoutExpired:
            result = subprocess.CompletedProcess(
                command, -1, "", "Command timed out"
            )

        end_time = time.time()

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time
        }

    def generate_report(self):
        """Generate test report"""
        logger.info(f"Test suite completed. Failures: {self.failure_count}")

        # Save report to file
        report_path = Path("test_reports") / f"test_report_{int(time.time())}.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "failure_count": self.failure_count,
                "results": self.test_results
            }, f, indent=2)

        logger.info(f"Test report saved to {report_path}")

if __name__ == "__main__":
    tester = ContinuousTester()
    tester.run_test_suite()
```

## Best Practices

### 1. Test Organization

```python
# Organize tests by functionality
tests/
├── unit/                    # Unit tests
│   ├── test_crawler.py     # Crawler unit tests
│   ├── test_processor.py   # Processor unit tests
│   └── test_storage.py     # Storage unit tests
├── integration/             # Integration tests
│   ├── test_api.py         # API integration tests
│   ├── test_database.py    # Database integration tests
│   └── test_external.py    # External service tests
├── performance/             # Performance tests
│   ├── test_load.py        # Load testing
│   └── test_stress.py      # Stress testing
├── security/                # Security tests
│   ├── test_vulnerabilities.py  # Vulnerability tests
│   └── test_authentication.py   # Authentication tests
└── data_quality/            # Data quality tests
    ├── test_validation.py  # Data validation tests
    └── test_integrity.py   # Data integrity tests
```

### 2. Test Naming

```python
# Use descriptive test names
def test_crawler_should_extract_tweets_from_twitter_page():
    """Test that crawler extracts tweets from Twitter page"""
    pass

def test_crawler_should_handle_empty_page_gracefully():
    """Test that crawler handles empty pages without errors"""
    pass

def test_crawler_should_respect_rate_limits():
    """Test that crawler respects Twitter rate limits"""
    pass
```

### 3. Test Data Management

```python
# Use fixtures for test data
@pytest.fixture
def sample_tweets():
    """Sample tweet data for testing"""
    return [
        {
            "id": "1234567890",
            "text": "This is a test tweet",
            "user": "testuser",
            "timestamp": "2025-07-03T10:00:00Z",
            "likes": 10,
            "retweets": 5
        }
    ]

@pytest.fixture
def mock_twitter_response():
    """Mock Twitter API response"""
    return {
        "data": [
            {
                "id": "1234567890",
                "text": "Test tweet",
                "author_id": "user123"
            }
        ]
    }
```

### 4. Test Isolation

```python
# Ensure tests are isolated
class TestIsolated:
    """Tests with proper isolation"""

    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_env = os.environ.copy()
        os.environ['TEST_MODE'] = 'true'

    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_isolated_functionality(self):
        """Test that doesn't affect other tests"""
        # Test implementation
        pass
```

### 5. Error Testing

```python
# Test error conditions
def test_crawler_handles_network_errors():
    """Test crawler handles network errors gracefully"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError()

        with pytest.raises(ConnectionError):
            crawler.fetch_data()

def test_crawler_handles_invalid_response():
    """Test crawler handles invalid responses"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Server Error"

        with pytest.raises(Exception):
            crawler.fetch_data()
```

### 6. Performance Testing

```python
# Test performance characteristics
def test_crawler_performance():
    """Test crawler performance under load"""
    start_time = time.time()

    # Run crawler
    crawler.crawl_tweets(100)

    end_time = time.time()
    duration = end_time - start_time

    # Assert performance requirements
    assert duration < 60  # Should complete within 60 seconds
    assert crawler.tweets_collected == 100  # Should collect expected number

def test_memory_usage():
    """Test memory usage"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Run memory-intensive operation
    crawler.crawl_tweets(1000)

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Assert memory usage is reasonable (less than 100MB increase)
    assert memory_increase < 100 * 1024 * 1024
```

This comprehensive testing guide ensures the Degen Digest platform maintains high quality, reliability, and security through thorough testing practices.
