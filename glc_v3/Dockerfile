# The gateway: models, keys, routing, quotas. It owns every provider credential
# so the runtime never sees one — keep that true in deployment by giving ONLY
# this service the GEMINI_API_KEY_* variables.
FROM python:3.12-slim AS base

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY glc/ ./glc/
COPY static/ ./static/
RUN uv sync --frozen --no-dev

# glc/cli.py already defaults to 0.0.0.0 and reads GLC_PORT.
ENV GLC_HOST=0.0.0.0 \
    GLC_PORT=8111 \
    PATH="/app/.venv/bin:$PATH"

# Keys come from the platform's secret store at run time, never from the image.
# Set GEMINI_API_KEY_1..N and GEMINI_MODEL there.
EXPOSE 8111

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-8111}/healthz" || exit 1

CMD glc serve --host "$GLC_HOST" --port "${PORT:-$GLC_PORT}"
