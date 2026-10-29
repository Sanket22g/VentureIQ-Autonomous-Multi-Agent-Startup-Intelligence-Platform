# ==============================================================================
# VentureIQ — Production Multi-Agent Intelligence Platform
# Containerized Streamlit + CrewAI Application (v1.0.0 Production Release)
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install essential system dependencies (curl for healthchecks, Chromium for Selenium tool)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    chromium \
    chromium-driver \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install official Astral uv binary for ultra-fast, deterministic dependency installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Cache dependency layer: copy configuration and lock file first
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the root project itself first (Docker layer cache)
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code and assets
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY knowledge/ ./knowledge/
COPY README.md LICENSE ./

# Complete uv sync to install the project package in editable/local mode
RUN uv sync --frozen --no-dev

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck endpoint (Streamlit built-in endpoint utilized by AWS ALB Target Group)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit with headless settings tailored for AWS ALB & reverse proxies
CMD ["uv", "run", "streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
