FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/downloads \
    /app/downloads/temp \
    /app/thumbs \
    /app/logs \
    /app/Rexbots \
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

# Copy project files
COPY . .

# Create additional required directories from the code
RUN mkdir -p /app/downloads \
    && chmod 755 /app/downloads \
    && mkdir -p /app/thumbs \
    && chmod 755 /app/thumbs

# Check if Rexbots directory exists, if not create it
RUN if [ ! -d "/app/Rexbots" ]; then mkdir -p /app/Rexbots; fi

# Set proper permissions for all created directories
RUN find /app -type d -exec chmod 755 {} \; && \
    find /app -type f -exec chmod 644 {} \; && \
    chmod +x /app/*.py

# Expose port for Flask app
EXPOSE 8080

# Start both Flask app and Telegram bot
CMD gunicorn --bind 0.0.0.0:8080 --workers=2 --threads=4 --timeout 120 --access-logfile - --error-logfile - app:app & \
    python3 bot.py

# Rexbots
# Don't Remove Credit 🥺
# Telegram Channel @RexBots_Official
