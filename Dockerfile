# Medical Visualization Platform - Docker Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for medical imaging and 3D rendering
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY static/ static/
COPY templates/ templates/

# Create upload directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Expose port (Hugging Face Spaces will use this)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Create startup script for Xvfb + Flask
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\nsleep 2\nexec python app.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Start application
CMD ["/app/start.sh"]

