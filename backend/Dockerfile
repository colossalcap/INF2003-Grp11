# ═══════════════════════════════════════════════════════════
# Stage 1: Build dependencies (gcc, libpq-dev stay here)
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ═══════════════════════════════════════════════════════════
# Stage 2: Runtime (slim — no build tools)
# ═══════════════════════════════════════════════════════════
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code (overridden by volume mount at runtime)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
