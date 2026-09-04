# FED-LINk — container image for running the short link builder.
# Usage:
#   docker build -t fedlink -f scripts/docker/Dockerfile .
#   docker run --rm -v "$PWD/output:/app/output" fedlink build configs/links.json

FROM python:3.11-slim

LABEL org.opencontainers.image.title="FED-LINk" \
      org.opencontainers.image.description="InfinityFree short link bundle builder" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY configs/ ./configs/
COPY templates/ ./templates/

# Non-root user for the build step
RUN useradd --create-home --uid 1000 fedlink \
    && mkdir -p /app/output \
    && chown -R fedlink:fedlink /app
USER fedlink

VOLUME ["/app/output"]

ENTRYPOINT ["python", "-m", "src.main"]
CMD ["build", "configs/links.json", "--output", "output", "--zip", "links.zip"]
