# Claude Code conventions for `pipeline-hackathon`

This file is read by Claude Code at the start of every session. Keep it tight.

## What this project is

**PipelinePilot** — an autonomous data integration agent for the
Google Cloud Rapid Agent Hackathon (Fivetran track). User describes a
business question; agent autonomously builds the data pipeline.

**Read [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) for the full plan**, architecture, and task list.
Tasks are numbered (T1.1, T2.3, etc.) — when the human says "do T2.3,"
look there.

## Critical gotchas — internalize before writing code

1. **Gemini 3.1 Pro runs ONLY on the global endpoint.** Always set
   `GOOGLE_CLOUD_LOCATION=global`. A regional endpoint will 404.
2. **Model identifier is `gemini-3.1-pro-preview`** (not `gemini-3-pro-preview` — that was discontinued March 2026). Fallback: `gemini-3-flash-preview`.
3. **State-changing Fivetran calls (`create_connector`, `sync_connection`, etc.)
   MUST pass through the approval gate.** Never bypass.
4. **Secrets live in Secret Manager**, never in env files committed to git.
   The `.env.example` is a template only.
5. **Fivetran trial expires in 14 days from activation.** If you see auth
   errors near the end of the build, that's why.

## Repo conventions

- **Python**: 3.11+, `uv` or `pip` with `requirements.txt`, ruff for lint,
  black for format, pytest for tests.
- **Imports**: stdlib first, third-party second, local last, alphabetized
  within each group.
- **Type hints**: required on all public functions, optional on private.
- **Docstrings**: required on all public functions (one-line summary + args + returns).
- **Logging**: use `structlog` if added, otherwise stdlib `logging` with
  JSON formatter. Never `print()` in production code.
- **Frontend**: React + Vite + Tailwind. Component files use `.tsx`.
  Functional components only, no class components.
- **Commits**: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
  One logical change per commit.
- **Branches**: feature branches off `main`; PRs (even solo) get a short
  description that says which task IDs they close.

## Where things live

- Setup scripts: `scripts/`
- Agent backend (Python, FastAPI): `agent/`
- Fivetran MCP fork: `mcp/`
- Frontend: `web/`
- Dockerfiles, Cloud Build configs: `infra/`
- Tests: `tests/`
- Architecture, demo script, API docs: `docs/`

## Common commands

```bash
# Set up local Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run verification (after Phase 1 setup is done)
python scripts/02_verify_gemini.py
python scripts/03_verify_fivetran.py --from-secret-manager

# Run agent locally
uvicorn agent.main:app --reload --port 8080

# Run tests
pytest -xvs

# Deploy agent to Cloud Run
gcloud run deploy pipelinepilot-agent \
  --source . \
  --region us-central1 \
  --service-account pipelinepilot-agent@bgus-genai-poc2.iam.gserviceaccount.com
```

## When in doubt

- Prefer reading existing code over assuming patterns.
- Ask the human before adding new dependencies.
- Update `IMPLEMENTATION_PLAN.md` (especially section 12 changelog) when you
  complete a task or make a decision.
- If a task seems wrong or unclear, flag it back to the human rather than
  guessing — this is a hackathon, scope creep kills.
