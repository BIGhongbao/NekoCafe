FROM python:3.12-alpine AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS deps
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM deps AS test
COPY src ./src
COPY tests ./tests
ENV PATH="/venv/bin:$PATH" PYTHONPATH=/app
RUN pytest -q

FROM base AS runtime
RUN addgroup -S app && adduser -S app -G app
COPY --from=deps /venv /venv
COPY src ./src
ENV PATH="/venv/bin:$PATH" \
    PYTHONPATH=/app \
    SERVICE_NAME=member-service \
    SERVICE_VERSION=0.1.0 \
    PORT=8080
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
