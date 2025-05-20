# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:${PATH}"

COPY --from=builder /root/.local /home/appuser/.local

# Copy aplikasi
COPY . .

# Setup non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["hypercorn", "app:asgi_app", "--bind", "0.0.0.0:5000", "--workers", "4"]