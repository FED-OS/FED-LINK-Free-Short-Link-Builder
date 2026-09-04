# FED-LINk — root container image for the short link builder.
#
# This is the convenience copy at the repository root (docker build .)
# It is identical in behavior to scripts/docker/Dockerfile, which the
# scripts/docker/docker-compose.yml stack builds via context ../..
# Use whichever is closer to your working directory.
#
# Usage:
#   docker build -t fedlink .
#   docker run --rm -v "$PWD":/data fedlink                  # links.zip -> ./
#   docker run --rm fedlink build configs/links.json          # plain build
#   docker run --rm fedlink validate configs/links.json       # validation only
#
# The image only needs the generator: src/, configs/, templates/ and
# requirements.txt. Everything else in the repo stays out of the image
# to keep it small and the build cache effective.

FROM python:3.11-slim

LABEL org.opencontainers.image.title="FED-LINk" \
      org.opencontainers.image.description="InfinityFree short link bundle builder" \
      org.opencontainers.image.version="1.1.0" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/fedpromptly/infinityfree-shortener-builder"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY configs/ ./configs/
COPY templates/ ./templates/

# Non-root user for the build step; write access to /app for the ZIP
RUN useradd --create-home --uid 1000 fedlink \
    && mkdir -p /app/output /data \
    && chown -R fedlink:fedlink /app /data
USER fedlink

VOLUME ["/app/output"]

ENTRYPOINT ["python", "-m", "src.main"]
CMD ["build", "configs/links.json", "--output", "output", "--zip", "links.zip"]
