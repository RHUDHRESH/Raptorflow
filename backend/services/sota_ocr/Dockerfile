# Dockerfile for GCP Deployment
# Multi-stage build for SOTA OCR System

# Base image with CUDA support
FROM nvidia/cuda:11.8-devel-ubuntu20.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libffi-dev \
    libssl-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    libwebp-dev \
    zlib1g-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY backend/services/sota_ocr/requirements.txt .

# Install Python dependencies
RUN python3.9 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copy application code
COPY backend/services/sota_ocr /app/services/sota_ocr/
COPY backend/config.py /app/config.py

# Create directories
RUN mkdir -p /app/data /app/logs /app/cache /app/models

# Download OCR models (placeholder - implement actual model download)
RUN echo "Downloading OCR models..." && \
    mkdir -p /app/models && \
    # Add actual model download commands here
    # wget -O /app/models/chandra-ocr-8b.pt https://models.raptorflow.ai/chandra-ocr-8b.pt
    # wget -O /app/models/dots-ocr.pt https://models.raptorflow.ai/dots-ocr.pt
    # wget -O /app/models/deepseek-ocr-3b.pt https://models.raptorflow.ai/deepseek-ocr-3b.pt
    echo "Model downloads completed"

# Production stage
FROM base as production

# Copy virtual environment from base stage
COPY --from=base /app/venv /app/venv
COPY --from=base /app/services /app/services
COPY --from=base /app/config.py /app/config.py
COPY --from=base /app/models /app/models

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/venv/bin:$PATH"
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_CUDA_ARCH_LIST=8.0

# Create non-root user
RUN useradd -m -u 1000 ocr && \
    chown -R ocr:ocr /app

# Switch to non-root user
USER ocr

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "services.sota_ocr.api:router", "--host", "0.0.0.0", "--port", "8000"]

# Worker stage
FROM production as worker

# Override start command for worker
CMD ["python", "-m", "services.sota_ocr.worker"]

# Monitor stage
FROM production as monitor

# Override start command for monitor
CMD ["python", "-m", "services.sota_ocr.monitor"]
