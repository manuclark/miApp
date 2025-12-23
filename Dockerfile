# Multi-stage build: Build frontend first
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY angular.json tsconfig.json tsconfig.app.json tsconfig.spec.json ./
COPY ionic.config.json capacitor.config.ts ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src ./src

# Build the application
RUN npm run build -- --configuration production

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pyodbc
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/www ./www

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
