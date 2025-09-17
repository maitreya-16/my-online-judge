# # Base image
# FROM python:3.12-slim

# # Set environment variables
# ENV DEBIAN_FRONTEND=noninteractive
# ENV DOCKERVERSION=24.0.5

# # Install system dependencies, compilers, Java, and Docker CLI
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         curl \
#         tar \
#         openjdk-21-jdk \
#         gcc \
#         g++ \
#         build-essential \
#         python3-dev \
#         git \
#         unzip \
#     && curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
#     && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 -C /usr/local/bin docker/docker \
#     && rm docker-${DOCKERVERSION}.tgz \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy requirements and install Python packages
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . .

# # Default command (you can override in docker-compose)
# CMD ["celery", "-A", "workers.tasks", "worker", "--loglevel=info"]

# Base image
FROM python:3.12-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKERVERSION=24.0.5

# Install system dependencies, compilers, Java, and Docker CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        tar \
        build-essential \
        unzip \
    && curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
    && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker-${DOCKERVERSION}.tgz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default command (you can override in docker-compose)
CMD ["celery", "-A", "workers.tasks", "worker", "--loglevel=info"]
