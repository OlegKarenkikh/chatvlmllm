# ChatVLMLLM Dockerfile
# Multi-stage build supporting both CPU and CUDA modes
#
# CPU Mode (default):
#   docker build -t chatvlmllm:cpu .
#   docker run -p 8501:8501 chatvlmllm:cpu
#
# CUDA Mode:
#   docker build -f Dockerfile.cuda -t chatvlmllm:cuda .
#   docker run --gpus all -p 8501:8501 chatvlmllm:cuda
#
# For CUDA/WSL support, use Dockerfile.cuda instead

FROM python:3.10-slim

LABEL maintainer="OlegKarenkikh"
LABEL description="ChatVLMLLM - Vision Language Models for Document OCR (CPU version)"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    # HuggingFace cache
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    git \
    wget \
    curl \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Additional libraries
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: For CPU mode, PyTorch CPU version is installed
RUN pip install --no-cache-dir \
    torch==2.2.0 \
    torchvision==0.17.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/examples/invoices \
    /app/examples/passports \
    /app/examples/receipts \
    /root/.cache/huggingface

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
