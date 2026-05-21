# ── Stage 1: runtime base ────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# System libraries required by opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
      libglib2.0-0 \
      libgl1 \
      libsm6 \
      libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── Stage 2: install Python dependencies ─────────────────────────────────────
FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 3: final image ──────────────────────────────────────────────────────
FROM deps AS final

COPY . .

# Snapshots directory (can be overridden by bind-mount in production)
RUN mkdir -p snapshots

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
