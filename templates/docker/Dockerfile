# SaucyClaw Multi-Agent Project

# Use Python 3.11+ for optimal compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /workspace

# Install Python dependencies
RUN pip install --no-cache-dir -q \
    pyyaml \
    rich \
    click \
    && pip install --no-cache-dir -e /workspace/tools

# Create necessary directories
RUN mkdir -p \
    /workspace/system \
    /workspace/agents \
    /workspace/docs \
    /workspace/templates \
    /workspace/examples \
    /workspace/scripts \
    /workspace/tools \
    /workspace/demo \
    /workspace/focus \
    /workspace/plaza

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Default command
CMD ["bash"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
