# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements-streamlit.txt ./
RUN pip install --upgrade pip && pip install -r requirements-streamlit.txt

# Copy dashboard and essential files
COPY dashboard/ ./dashboard/
COPY start_dashboard.py ./
COPY main.py ./
COPY utils/ ./utils/
COPY storage/ ./storage/
COPY processor/ ./processor/
COPY config/ ./config/
COPY output/ ./output/

# Create necessary directories
RUN mkdir -p logs output

# Expose port for Cloud Run
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Entrypoint
CMD ["python3", "start_dashboard.py"]
