FROM python:3.11-slim

ARG BUILD_ID=2025-12-28-01
ENV BUILD_ID=$BUILD_ID

WORKDIR /app

# Install system dependencies for psycopg
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install PhonePe Node bridge dependencies
RUN npm --prefix phonepe install --omit=dev

# Expose port
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
