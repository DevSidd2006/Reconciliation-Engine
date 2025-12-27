# Banking Reconciliation Backend - FastAPI Application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/start.sh

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8002

# Health check with longer timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=5 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the startup script
CMD ["/app/start.sh"]