FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml ./
COPY servers ./servers
COPY mocks ./mocks
COPY README.md LICENSE ./

RUN pip install --upgrade pip && \
    pip install ".[serve]"

# Run as non-root for compliance with HITL spec §16
RUN useradd -u 10001 -m daum && chown -R daum:daum /app
USER daum

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2).status==200 else 1)"

CMD ["python", "-m", "servers.http_app"]
