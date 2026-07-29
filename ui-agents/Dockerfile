# The Session 14 runtime: agent graph, memory, catalog, validator and the UI.
# One long-running process with a disk — NOT a serverless function. A turn is two
# HTTP requests (POST /v1/agent/runs, then GET /v1/runs/{id}/composed) and the run
# lives in app.state.s13_runtime, so both must reach the same process. Anything
# that can route them to different instances returns "run not found".
FROM python:3.12-slim AS base

# faiss and grpcio ship manylinux wheels, so no compiler is needed; curl is here
# only so the platform healthcheck below has something to call.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first: they change far less often than the source, so edits to
# s13code/ do not re-resolve the whole tree on every build.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY s13code/ ./s13code/
COPY proofs/ ./proofs/
RUN uv sync --frozen --no-dev

# The graph journal and memory are SQLite on disk. Mount a volume here or every
# redeploy silently starts with an empty history.
ENV S13_DATA_DIR=/data \
    S13_HOST=0.0.0.0 \
    S13_PORT=8113 \
    S13_SANDBOX_ROOT=/data/sandbox \
    PATH="/app/.venv/bin:$PATH"
RUN mkdir -p /data/sandbox

# No credentials here. GLC_BASE_URL points at the gateway, which owns every key —
# the same separation the runtime keeps locally.
EXPOSE 8113

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT:-8113}/healthz" || exit 1

# Shell form so $PORT (injected by most hosts) is expanded at start.
CMD s14code serve --host "$S13_HOST" --port "${PORT:-$S13_PORT}"
