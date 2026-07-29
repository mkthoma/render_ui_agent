# render_ui_agent

Deployment monorepo for the Session 14 generative-UI stack. Two services, one
Render blueprint.

| | |
|---|---|
| `glc_v3/` | the gateway — models, routing, quotas. **The only place a provider credential exists.** |
| `ui-agents/` | the runtime — agent graph, memory, component catalog, validator, and the UI it serves |
| `render.yaml` | one blueprint that deploys both and wires them together |

## What runs where

```
browser ──▶ ui-agents  ──HTTP──▶  glc_v3  ──▶ Gemini
            /decide               (holds every key)
            /gallery
            /app
```

The runtime never receives a provider key. It calls the gateway over HTTP, and
the gateway holds the credentials — the same separation the project keeps
locally, preserved in deployment rather than abandoned at it.

## Deploy

1. Push this repo to GitHub.
2. Render → **New → Blueprint** → connect it. Both services are created from
   `render.yaml`.
3. On **glc-gateway**, set `GEMINI_API_KEY_1` … `GEMINI_API_KEY_5` in the
   dashboard. Nothing else needs setting: `GLC_BASE_URL` on the runtime resolves
   from the gateway service automatically.
4. Open `https://<s14-runtime>.onrender.com/decide`.

### Routes

| path | |
|---|---|
| `/decide` | **the application** — ask a question, tap to continue |
| `/gallery` | every component in the catalog, drawn by the real client |
| `/app` | the session's original example viewer |
| `/v1/catalog` | the trusted catalog as JSON |
| `/healthz` | liveness, used by the platform healthcheck |

## Two constraints that are not preferences

**One instance.** A turn is two HTTP requests — `POST /v1/agent/runs`, then
`GET /v1/runs/{id}/composed` — and the run lives in `app.state.s13_runtime`.
Route them to different instances and the second returns 404. `numInstances: 1`
is load-bearing; do not enable autoscaling.

**A disk at `/data`.** The graph journal and memory are SQLite. Without the
mounted volume every redeploy silently starts with an empty history — it looks
fine until you notice old runs are gone.

Both are why this is a container and not a serverless function; a turn also takes
10–60 s, which most function timeouts will cut off.

## Local development

Two terminals, from the *source* repos or from here:

```bash
cd glc_v3 && uv sync && uv run glc serve
```

```bash
cd ui-agents && uv sync && GLC_BASE_URL=http://127.0.0.1:8111 uv run s14code serve
```

Then `http://127.0.0.1:8113/decide`. Locally the runtime binds `127.0.0.1` so a
dev machine is not exposed to its network; the container sets `S13_HOST=0.0.0.0`.

Create `glc_v3/.env` from `glc_v3/.env.example` and put your keys there. It is
gitignored and excluded from the Docker build context.

## Model note

Free-tier Gemini quota is **per key and per model**. `gemini-2.5-flash` is
retired for new keys and returns 404; the blueprint pins
`gemini-3.1-flash-lite`, which was reachable on all five keys. If turns start
failing with 429, check quota per model before assuming the code broke.

## Source of truth

The assignment work lives in [`mkthoma/ui-agents`](https://github.com/mkthoma/ui-agents).
This repo is a deployment copy — changes made to `ui-agents/` here need to reach
that repo too, or the two will drift.
