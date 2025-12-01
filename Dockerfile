# Use Python 3.9 slim image to reduce base size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
# Use --no-cache-dir to reduce image size
# Install CPU-only PyTorch first (saves ~2GB compared to full PyTorch)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu --no-deps && \
    pip install --no-cache-dir -r requirements.txt && \
    # Clean up pip cache
    rm -rf /root/.cache/pip && \
    # Don't download models during build - they'll be downloaded at runtime
    rm -rf /root/.cache/huggingface || true

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/knowledge_base/chroma_db data/processed data/raw

# Build knowledge base at runtime (not in image)
# This will be done via a startup script or Railway's build command

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]

