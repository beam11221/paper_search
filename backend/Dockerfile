# FastAPI server
FROM python:3.12.0-slim

WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     gcc \
#     librdkafka-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY . /app/backend

# Set environment variables
ENV PYTHONPATH=/app
ENV APP_PORT=7890
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 7890

# Command to run the FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7890"]