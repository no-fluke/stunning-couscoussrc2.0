FROM python:3.12-slim

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    gcc \
    g++ \
    make \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/downloads \
    /app/thumbs \
    /app/logs \
    && chmod -R 755 /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOWNLOAD_PATH=/app/downloads \
    MAX_DOWNLOAD_SIZE=2147483648 \
    COOLDOWN_SECONDS=30

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies (optional, to reduce image size)
RUN apt-get purge -y \
    gcc \
    g++ \
    make \
    build-essential \
    python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Set proper permissions
RUN chown -R 1001:1001 /app && \
    chmod -R 755 /app

# Create a non-root user for security
RUN useradd -m -u 1001 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port for Flask app
EXPOSE 8080

# Start both services
CMD gunicorn --bind 0.0.0.0:8080 --workers=2 --threads=4 --timeout 120 --access-logfile - --error-logfile - app:app & \
    python3 bot.py

# Rexbots
# Don't Remove Credit 🥺
# Telegram Channel @RexBots_Official
