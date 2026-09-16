# ---------- Build stage ----------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependencies into a virtualenv we can copy to the runtime stage
COPY backend/requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# ---------- Runtime stage ----------
FROM python:3.11-slim

# Security: don't run as root
RUN groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

# Copy the virtualenv from the build stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the backend app and the frontend into the image
COPY backend/app ./app
COPY frontend /frontend

# SQLite will live in /app/data; create it and make sure appuser owns it
RUN mkdir -p /app/data && chown -R app:app /app
ENV DATABASE_URL="sqlite:////app/data/tasks.db"

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]