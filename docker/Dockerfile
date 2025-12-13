# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# STAGE 1: Builder (Heavy lifting, compilation)
# -----------------------------------------------------------------------------
# We use the NVIDIA CUDA runtime to ensure any compiled extensions (like llama-cpp) 
# can link against CUDA libraries.
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install minimal system build deps (compilers for python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with BuildKit caching (Fast Re-builds)
COPY requirements/ /tmp/requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements/base.txt

# -----------------------------------------------------------------------------
# STAGE 2: Runtime (Slim, Secure, GPU-enabled)
# -----------------------------------------------------------------------------
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Keep Python unbuffered in Prod so logs stream instantly to Docker/Portainer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install only the runtime python (no compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash chimera

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory & Permissions
WORKDIR /app
RUN mkdir -p data/backups logs && \
    chown -R chimera:chimera /app

# Switch user early for security
USER chimera

# Copy code (ownership is handled by COPY --chown in newer docker versions, 
# but doing it here after USER switch requires care. 
# Better to copy as root then chown, OR copy as user.)
COPY --chown=chimera:chimera src/ ./src/
COPY --chown=chimera:chimera config.yaml ./config.yaml

# Native Python Healthcheck (No curl needed!)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; exit(0) if urllib.request.urlopen('http://localhost:3000/api/health').getcode() == 200 else exit(1)"

# Expose ports
EXPOSE 3000 3001

# Default command
CMD ["python3", "-m", "src.main", "server"]