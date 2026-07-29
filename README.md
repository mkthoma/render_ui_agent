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

## Running on the free tier — what you are trading away

The blueprint uses `plan: free` for both services. Two consequences, both real:

**Services sleep after ~15 minutes idle.** Waking takes roughly 50 s, and *then*
your turn takes another 30–60 s. The first request after a lull looks like a
hang. Before demoing or recording, wake both:

```bash
curl -s https://<glc-gateway>.onrender.com/healthz
curl -s https://<s14-runtime>.onrender.com/healthz
```

**No persistent disk.** Render's free instance type does not offer one, so
`S13_DATA_DIR` writes to the container filesystem. Runs work normally while the
container is alive; the graph journal and memory are **lost on every restart,
redeploy and wake-from-sleep**. Fine for a demo, wrong for anything you want to
keep. To fix it, move to a paid plan and restore the `disk:` block:

```yaml
disk:
  name: s14-data
  mountPath: /data
  sizeGB: 1
```

## One constraint that is not a preference

**One instance.** A turn is two HTTP requests — `POST /v1/agent/runs`, then
`GET /v1/runs/{id}/composed` — and the run lives in `app.state.s13_runtime`.
Route them to different instances and the second returns 404. `numInstances: 1`
is load-bearing; do not enable autoscaling on any plan.

That, plus a 10–60 s turn, is why this is a container rather than a serverless
function — most function timeouts would cut a turn off mid-compose.

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
