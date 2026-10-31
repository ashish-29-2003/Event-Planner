# Multi-stage production Dockerfile for Samaroh (समारोह) on Google Cloud Run
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final minimal production image
FROM python:3.13-slim AS runner

WORKDIR /app

COPY --from=builder /install /usr/local

# Run as non-root user for security hardening
RUN groupadd -g 1001 samaroh && \
    useradd -u 1001 -g samaroh -m -s /bin/bash samaroh

# Copy source code and frontend public assets
COPY --chown=samaroh:samaroh src/ /app/src/
COPY --chown=samaroh:samaroh public/ /app/public/
COPY --chown=samaroh:samaroh run.py /app/
COPY --chown=samaroh:samaroh pyproject.toml /app/

# Persistent local cache directory
RUN mkdir -p /app/data && chown -R samaroh:samaroh /app/data

USER samaroh

ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV ALLOW_STORAGE_FALLBACK=true

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '8080'); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health')" || exit 1

CMD ["sh", "-c", "exec python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
