# Multi-stage build for CHIMERA AUTARCH
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  g++ \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY chimera_autarch.py .
COPY ws_client.py .
COPY config.py* ./

# Create directories for persistence
RUN mkdir -p /app/backups /app/logs /app/ssl

# Expose ports
EXPOSE 8765 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/metrics')" || exit 1

# Run as non-root user for security
RUN useradd -m -u 1000 chimera && \
  chown -R chimera:chimera /app
USER chimera

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  CHIMERA_PERSISTENCE_DATABASE_PATH=/app/chimera_memory.db \
  CHIMERA_PERSISTENCE_BACKUP_DIR=/app/backups \
  CHIMERA_LOGGING_FILE_PATH=/app/logs/chimera.log

# Start CHIMERA
CMD ["python", "chimera_autarch.py"]
