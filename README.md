# PipelinePilot

> Tell it the question you need answered. It builds the data pipeline.

PipelinePilot is an autonomous data integration agent built on **Gemini 3.1
Pro**, **Google Cloud Agent Builder**, and the **Fivetran MCP server**. You
describe a business question in plain English; the agent plans a data
pipeline, sets up the Fivetran connectors, lands the data in BigQuery,
writes the analytical model, and configures monitoring — all under your
explicit approval.

Built for the [Google Cloud Rapid Agent Hackathon](https://rapid-agent.devpost.com/), Fivetran track.

---

## Demo scenario

> **Founder:** *"I need to know if our paid acquisition is profitable.
> Pull Stripe revenue, HubSpot conversion data, and Google Ads spend into
> BigQuery, refresh daily, and alert me on Slack if blended CAC payback
> exceeds 6 months."*

PipelinePilot then:

1. **Plans** the work and shows you the steps.
2. **Discovers** what's already set up in your Fivetran account.
3. **Estimates cost** and asks you to approve before creating anything.
4. **Creates the missing connectors**, triggers initial syncs, validates data lands.
5. **Writes the BigQuery view** that computes blended CAC payback.
6. **Schedules a daily check** that posts to Slack on threshold breach.
7. **Reports back** with the current answer and where everything lives.

---

## Architecture

```
User ─▶ React UI (Cloud Run) ─▶ Agent Backend (Cloud Run, Gemini 3.1 Pro)
                                        │
                  ┌─────────────────────┼─────────────────────────┐
                  ▼                     ▼                         ▼
         Fivetran MCP Server     BigQuery tools         Cloud Scheduler tools
            (Cloud Run)            (custom)                  (custom)
                  │
                  ▼
            Fivetran API
```

- **Reasoning:** Gemini 3.1 Pro via Vertex AI (global endpoint)
- **Tool layer:** Forked [`fivetran/fivetran-mcp`](https://github.com/fivetran/fivetran-mcp) + custom BigQuery + Scheduler tools
- **State:** Firestore for plans and approval records
- **Secrets:** Secret Manager for Fivetran credentials
- **Hosting:** Cloud Run for all services

---

## Quick start

> **You'll need:** A Google Cloud project with billing, a [Fivetran trial](https://fivetran.com/signup), and the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

```bash
# Clone
git clone https://github.com/avineetbespin/pipeline-hackathon.git
cd pipeline-hackathon

# Configure (edit PROJECT_ID in the script if needed)
./scripts/01_setup.sh

# Add Fivetran creds to Secret Manager
printf "%s" "YOUR_FIVETRAN_API_KEY"    | gcloud secrets create fivetran-api-key    --data-file=- --replication-policy=automatic
printf "%s" "YOUR_FIVETRAN_API_SECRET" | gcloud secrets create fivetran-api-secret --data-file=- --replication-policy=automatic

# Verify everything is wired up
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/02_verify_gemini.py
python scripts/03_verify_fivetran.py --from-secret-manager
```

See [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) for the full setup, deployment, and dev workflow.

---

## Tech stack

| Layer | Technology |
|---|---|
| Reasoning | Gemini 3.1 Pro (Vertex AI, global endpoint) |
| Agent SDK | [Google Gen AI SDK for Python](https://googleapis.github.io/python-genai/) |
| Partner integration | [Fivetran MCP server](https://github.com/fivetran/fivetran-mcp) |
| Compute | Cloud Run |
| Data warehouse | BigQuery |
| State | Firestore |
| Secrets | Secret Manager |
| Scheduling | Cloud Scheduler |
| Frontend | React + Vite + Tailwind |

---

## Hackathon submission

- **Track:** Fivetran
- **Submission deadline:** Jun 11, 2026 @ 2:00 PM PDT
- **Demo video:** *coming soon*
- **Live demo:** *coming soon*

---

## License

MIT — see [LICENSE](./LICENSE).

---

## Authors

[@avineetbespin](https://github.com/avineetbespin)
