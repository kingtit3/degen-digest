.PHONY: help install install-dev test lint format clean deploy dashboard digest setup-db backup-db restore-db logs health-check docker-build docker-run docker-stop docker-clean

# Default target
help:
	@echo "Degen Digest - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean cache and temporary files"
	@echo ""
	@echo "Application:"
	@echo "  dashboard    - Start the Streamlit dashboard"
	@echo "  digest       - Generate a new digest"
	@echo "  setup-db     - Initialize database"
	@echo "  logs         - View application logs"
	@echo "  health-check - Run system health check"
	@echo ""
	@echo "Database:"
	@echo "  backup-db    - Backup database"
	@echo "  restore-db   - Restore database from backup"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker-stop  - Stop Docker container"
	@echo "  docker-clean - Clean Docker resources"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy       - Deploy to cloud"
	@echo "  deploy-local - Deploy locally"

# Development
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

lint:
	ruff check .
	mypy .

format:
	black .
	isort .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# Application
dashboard:
	cd dashboard && streamlit run app.py

digest:
	python main.py

setup-db:
	python -c "from storage.db import init_db; init_db()"

logs:
	tail -f logs/degen_digest.log

health-check:
	python -c "from utils.health_monitor import health_monitor; print(health_monitor.get_health_summary())"

# Database
backup-db:
	cp output/degen_digest.db output/degen_digest.backup.$(shell date +%Y%m%d_%H%M%S).db

restore-db:
	@echo "Available backups:"
	@ls -la output/degen_digest.backup.*.db 2>/dev/null || echo "No backups found"
	@echo ""
	@echo "Usage: make restore-db BACKUP_FILE=output/degen_digest.backup.YYYYMMDD_HHMMSS.db"
ifdef BACKUP_FILE
	cp $(BACKUP_FILE) output/degen_digest.db
	@echo "Database restored from $(BACKUP_FILE)"
else
	@echo "Please specify BACKUP_FILE parameter"
endif

# Docker
docker-build:
	docker build -t degen-digest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker system prune -f

# Deployment
deploy:
	@echo "Deploying to cloud..."
	@if [ -f deploy.sh ]; then \
		bash deploy.sh; \
	else \
		echo "Deploy script not found. Please run: bash deploy_cloud_function.sh"; \
	fi

deploy-local:
	@echo "Starting local deployment..."
	docker-compose up -d
	@echo "Dashboard available at: http://localhost:8501"

# Additional utilities
check-env:
	@echo "Checking environment variables..."
	@python -c "from utils.env import check_env; check_env()"

run-scrapers:
	@echo "Running all scrapers..."
	python -m scrapers.twitter_apify
	python -m scrapers.reddit_rss
	python -m scrapers.newsapi_headlines
	python -m scrapers.coingecko_gainers

monitor:
	@echo "Starting system monitoring..."
	python monitor_deployment.py

# Quick setup for new developers
setup-dev:
	@echo "Setting up development environment..."
	python -m venv .venv
	@echo "Virtual environment created. Activate it with: source .venv/bin/activate"
	@echo "Then run: make install-dev"
	@echo "Copy .env.example to .env and configure your API keys"

# Production setup
setup-prod:
	@echo "Setting up production environment..."
	make install
	make setup-db
	@echo "Production setup complete. Run 'make deploy' to deploy."

# Emergency commands
emergency-stop:
	@echo "Emergency stop - killing all related processes..."
	pkill -f "streamlit"
	pkill -f "python.*main.py"
	docker-compose down
	@echo "All processes stopped."

emergency-clean:
	@echo "Emergency cleanup..."
	make clean
	make docker-clean
	rm -rf output/*.json output/*.md output/*.pdf
	@echo "Emergency cleanup complete." 