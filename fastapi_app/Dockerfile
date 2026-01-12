# Simple production-ready FastAPI image
FROM python:3.11-slim

# Install runtime deps for faiss-cpu wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
          libgomp1 \
          && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and assets
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Default command (override with CMD if needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
