# PipelinePilot — Implementation Plan

> **Audience:** Claude Code (and any human collaborator). This is the source
> of truth for what we're building and the order to build it in. Update this
> file as decisions are made and tasks are completed.

---

## 1. What we're building

**PipelinePilot** is an autonomous data integration agent. A user describes a
business question they need to answer (in English), and the agent autonomously:

1. Plans the data pipeline needed to answer it.
2. Discovers existing Fivetran connectors and BigQuery destinations.
3. Proposes new connectors with cost estimates, gated by user approval.
4. Creates the connectors, triggers initial syncs, and verifies tables arrive.
5. Generates and deploys a BigQuery SQL view that computes the answer.
6. Sets up scheduled monitoring + alerting (Cloud Scheduler + Slack/email).
7. Reports back with where everything lives and the current answer.

**Anchor demo scenario** (this is the demo we are designing the whole product backward from):

> A founder says: *"I need to know if our paid acquisition is profitable.
> Pull Stripe revenue, HubSpot conversion data, and Google Ads spend into
> BigQuery, refresh daily, and alert me on Slack if blended CAC payback
> exceeds 6 months."*
>
> PipelinePilot then sets the whole thing up while the founder makes coffee.

---

## 2. Hackathon context

| Item | Value |
|---|---|
| Hackathon | Google Cloud Rapid Agent Hackathon |
| Track | **Fivetran** (one of 5 partner buckets) |
| Deadline | **Jun 11, 2026 @ 2:00 PM PDT** |
| Prizes (Fivetran bucket) | 1st $5,000 • 2nd $3,000 • 3rd $2,000 |
| GCP project | `bgus-genai-poc2` |
| Repo | `github.com/avineetbespin/pipeline-hackathon` |

### Required submission deliverables

- [ ] Hosted project URL (publicly accessible — likely Cloud Run)
- [ ] Public open-source repo with **MIT or other OSI license at the root**
- [ ] **~3 minute demo video** (YouTube/Vimeo public link)
- [ ] Completed Devpost submission form, with **Fivetran** track selected

### Judging criteria (build with these in mind)

1. **Technological Implementation** — quality of Google Cloud + Fivetran integration
2. **Design** — UX and project polish
3. **Potential Impact** — real-world value
4. **Quality of the Idea** — creativity / uniqueness

---

## 3. Why Fivetran (rationale, do not relitigate)

- Fivetran's own December 2025 blog post pitches *exactly* this vision
  ("Integrate data faster using natural language, Fivetran, and MCP").
  Judges will see their company's strategic direction reflected in the demo.
- The Fivetran MCP server is real, official, and exposes 50+ tools.
- The bucket is structurally less crowded than MongoDB / Elastic / GitLab.
- Multi-step autonomy is *natural* — discovery, planning, creation,
  validation, monitoring — not bolted on.

---

## 4. Architecture

```
                       ┌──────────────────────────────────────────┐
                       │  User (web browser)                       │
                       │  - Types natural-language pipeline goal   │
                       │  - Sees plan, approves, watches progress  │
                       └──────────────────┬───────────────────────┘
                                          │ HTTPS
                                          ▼
                       ┌──────────────────────────────────────────┐
                       │  PipelinePilot Frontend (Cloud Run)      │
                       │  - Static site + small JSON API           │
                       │  - Session state in Firestore             │
                       └──────────────────┬───────────────────────┘
                                          │ HTTPS (internal)
                                          ▼
                       ┌──────────────────────────────────────────┐
                       │  Agent Backend (Cloud Run)               │
                       │  - Gemini 3.1 Pro (global endpoint)       │
                       │  - Planner / executor / verifier loop     │
                       │  - Tool dispatcher                         │
                       └────┬──────────────┬─────────────┬────────┘
                            │              │             │
                            ▼              ▼             ▼
              ┌──────────────────┐ ┌────────────┐ ┌──────────────┐
              │ Fivetran MCP     │ │ BigQuery   │ │ Cloud        │
              │ Server (Cloud    │ │ tools      │ │ Scheduler +  │
              │ Run, our fork)   │ │ (custom)   │ │ Slack tools  │
              │ - 50+ tools      │ │ - run SQL  │ │ (custom)     │
              │ - read/write to  │ │ - create   │ │ - schedule   │
              │   Fivetran API   │ │   views    │ │   queries    │
              └────────┬─────────┘ └──────┬─────┘ └──────┬───────┘
                       │                  │              │
                       ▼                  ▼              ▼
                  Fivetran API        BigQuery       Cloud Scheduler
                                                     + Slack webhook
```

**Cross-cutting:**
- **Secret Manager** — Fivetran API key/secret, Slack webhook URL.
- **Firestore** — agent plans, approval state, run history.
- **Artifact Registry** — container images for both Cloud Run services.

---

## 5. Tech stack (locked decisions)

| Concern | Choice | Why |
|---|---|---|
| Reasoning model | `gemini-3.1-pro-preview` (Vertex AI, **global endpoint**) | Strongest agentic reasoning available in May 2026; fallback to `gemini-3-flash-preview` if quota is blocked |
| Agent framework | Google Gen AI SDK for Python (`google-genai >= 1.51.0`) | Native function calling, supports thinking_level, official path |
| MCP server | Fork of `github.com/fivetran/fivetran-mcp` | Officially blessed by the hackathon's Fivetran resources page |
| Hosting | Cloud Run (both frontend and backend) | Org-friendly, scales to zero, simpler than Agent Runtime for our shape |
| Data warehouse | BigQuery (dataset: `pipelinepilot`) | Native GCP, judges will appreciate it, Fivetran has a first-class connector |
| State | Firestore (Native mode) | Simple, serverless, fits document-shaped agent state |
| Secrets | Secret Manager | Required by hackathon's Phase 4 |
| Frontend | React (Vite) + Tailwind | Fast to build, clean for a demo |
| Demo source data | Stripe (test mode), HubSpot dev account, Google Ads test account | All have free sandboxes |

**NOT using** (and the reason):
- Agent Builder low-code console — fine for prototypes, but we want a real repo we can submit and that Claude Code can iterate on.
- Agent Runtime — adds a Vertex-specific layer that complicates the open-source repo story.
- LangChain / LlamaIndex — extra dependency, no clear value over the native SDK for this scope.

---

## 6. Repo structure (target state)

```
pipeline-hackathon/
├── README.md                         # public-facing project description
├── IMPLEMENTATION_PLAN.md            # this file (source of truth)
├── CLAUDE.md                         # conventions for Claude Code
├── LICENSE                           # MIT, required by hackathon
├── .gitignore
├── .env.example                      # template, no real secrets
├── requirements.txt                  # pinned Python deps
├── pyproject.toml                    # (optional) for clean packaging
│
├── scripts/                          # one-off setup + verification
│   ├── 01_setup.sh                   # gcloud APIs, SA, BigQuery dataset
│   ├── 02_verify_gemini.py
│   ├── 03_verify_fivetran.py
│   └── 04_deploy_mcp_to_cloudrun.sh  # Day 4+
│
├── agent/                            # the agent backend
│   ├── __init__.py
│   ├── main.py                       # FastAPI entrypoint for Cloud Run
│   ├── planner.py                    # plan generation w/ Gemini
│   ├── executor.py                   # step execution + approval gates
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── fivetran.py               # MCP client wrapper
│   │   ├── bigquery.py
│   │   └── scheduler.py
│   ├── prompts/
│   │   ├── system.md                 # system prompt
│   │   └── planning_examples.md      # few-shot examples
│   └── state.py                      # Firestore wrapper
│
├── mcp/                              # our fork of fivetran-mcp
│   └── ...                           # (added as a git submodule or vendored)
│
├── web/                              # frontend
│   ├── index.html
│   ├── src/
│   └── package.json
│
├── infra/                            # IaC
│   ├── Dockerfile.agent
│   ├── Dockerfile.mcp
│   └── cloudbuild.yaml
│
├── tests/
│   └── test_planner.py
│
└── docs/
    ├── architecture.md
    ├── demo_script.md
    └── api.md
```

---

## 7. Critical gotchas (flag these to anyone touching the code)

### G1 — Gemini 3.1 Pro is on the **global** endpoint, not regional

```python
import os
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"   # NOT us-central1
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
```

Using a regional endpoint will return cryptic 404s on the model. This is
the single most common Day-1 failure mode.

### G2 — Gemini 3.1 Pro is a **preview** model

Default quota is low. If we start seeing 429s, either request a quota
increase (1–5 business days via the console) or fall back to
`gemini-3-flash-preview` (same family, same SDK, cheaper).

### G3 — Fivetran trial is **14 days**

Hackathon runs 30. Plan to either pay for a month at the tail end or
pre-record demo segments before expiry. Ask Fivetran hackathon support
on the Devpost Discord if they extend trials for participants.

### G4 — `bgus-genai-poc2` is a **shared org sandbox**

Quota collisions with other team members are possible. If demo recording
starts hitting throttles, consider requesting a dedicated subfolder/project
for the final week.

### G5 — Org IAM may block standard Cloud Run public exposure

If `--allow-unauthenticated` is denied by org policy, put the service
behind Identity-Aware Proxy and share a token with judges. Equivalent
hackathon-acceptable outcome.

### G6 — All state-changing Fivetran calls **must** go through the approval gate

This is a product principle, not a nice-to-have. The hackathon explicitly
rewards "under your oversight." Never let the planner call
`create_connector`, `delete_connector`, or `sync_connection` without an
explicit user approval recorded in Firestore.

---

## 8. Implementation phases & tasks

Each task has an ID (e.g. `T1.3`), an acceptance criterion ("Done when...")
that's verifiable, and an owner (defaults to Claude Code unless flagged
`[HUMAN]` because it requires console/web work).

### Phase 1 — Environment & verification (Day 1)

| ID | Task | Done when... |
|---|---|---|
| T1.1 [HUMAN] | Verify your user has `serviceUsageAdmin`, `iam.serviceAccountAdmin`, `resourcemanager.projectIamAdmin` on `bgus-genai-poc2` | You can run `gcloud services list --available` without error |
| T1.2 | Commit the initial repo skeleton (this file + LICENSE + .gitignore + README) | `git push` succeeds, license shows in GitHub About section |
| T1.3 | Run `scripts/01_setup.sh` | All 9 APIs enabled, SA created with 9 roles, BigQuery dataset `pipelinepilot` exists |
| T1.4 [HUMAN] | Store Fivetran key + secret in Secret Manager (commands at end of `01_setup.sh`) | `gcloud secrets list` shows `fivetran-api-key` and `fivetran-api-secret` |
| T1.5 [HUMAN] | Apply for $100 hackathon credit at https://forms.gle/xfv9vQzfRfNCCVbG7 | Confirmation email received |
| T1.6 | Run `scripts/02_verify_gemini.py` | Script prints a response from `gemini-3.1-pro-preview` (or Flash fallback) |
| T1.7 | Run `scripts/03_verify_fivetran.py --from-secret-manager` | Script lists your Fivetran group(s) and any existing connectors |
| T1.8 [HUMAN] | Join the hackathon Discord and Devpost forum; register the project | Registration confirmation visible on Devpost |

**Phase 1 done when all 8 boxes are checked.**

### Phase 2 — First end-to-end Gemini → MCP → Fivetran (Days 2–3)

| ID | Task | Done when... |
|---|---|---|
| T2.1 | Fork `github.com/fivetran/fivetran-mcp` into our org and vendor it into `mcp/` | Fork exists, vendored copy installable locally |
| T2.2 | Write a `Dockerfile.mcp` that runs the MCP server as an HTTP service | `docker build -f infra/Dockerfile.mcp .` succeeds, container responds to MCP requests locally |
| T2.3 | Deploy the MCP server to Cloud Run (`pipelinepilot-mcp` service), with Fivetran creds injected from Secret Manager | `curl https://pipelinepilot-mcp-*.run.app/health` returns 200 |
| T2.4 | Write `agent/tools/fivetran.py` — a thin Python client that calls the deployed MCP server | Unit test calls `list_connections` and returns parsed JSON |
| T2.5 | Write `agent/planner.py` — minimal: Gemini 3.1 Pro with one tool (`list_connections`), prompted to answer "what data sources do I have?" | Running it returns a real natural-language summary of your Fivetran connectors, citing real connector names |

**Phase 2 done when:** A Python script invokes Gemini 3.1 Pro with the Fivetran tool, and Gemini accurately describes the Fivetran account state. **This is the first moment the project is real.**

### Phase 3 — Core agent loop (Days 4–10)

| ID | Task | Done when... |
|---|---|---|
| T3.1 | Define the tool surface: `list_connections`, `list_destinations`, `get_connector_schemas`, `create_connector`, `sync_connection`, `get_sync_status` — wired through MCP | Each callable from `agent/tools/fivetran.py` with typed Python wrappers |
| T3.2 | Add BigQuery tools: `run_query`, `create_view`, `list_tables` | `agent/tools/bigquery.py` exists with each callable from the agent loop |
| T3.3 | Build the planner: takes a natural-language goal, produces a structured `Plan` (list of `Step`s with tool, args, rationale, requires_approval flag) | Planner produces a valid `Plan` JSON for the anchor demo scenario |
| T3.4 | Build the executor: walks the `Plan`, calls tools, records results in Firestore, pauses at `requires_approval` steps | Executor can run a 3-step plan end-to-end against the Fivetran sandbox |
| T3.5 | Implement the approval gate: state-changing steps write to a Firestore `approvals` collection; executor blocks until approved | Calling `create_connector` blocks; manually setting `approved: true` in Firestore unblocks it |
| T3.6 | Wrap it all in a FastAPI app (`agent/main.py`) deployed to Cloud Run | `POST /run` accepts a goal, returns a plan id; `GET /run/{id}` returns current state |

**Phase 3 done when:** From a curl command, an end-to-end run completes for a simplified version of the anchor demo (one source, one destination, one view), with the approval gate firing once.

### Phase 4 — UI + multi-source (Days 11–18)

| ID | Task | Done when... |
|---|---|---|
| T4.1 | Build the React frontend: text input for goal, plan display panel, approval buttons, live progress feed | UI renders all the right states on a recorded plan |
| T4.2 | Wire the frontend to the agent backend via Cloud Run | Submitting a goal in the UI starts an agent run and shows live progress |
| T4.3 | Add the third tool category: Cloud Scheduler + Slack webhook for daily alerts | Agent can set up a scheduled job that posts to Slack on threshold breach |
| T4.4 | Run the full anchor demo end-to-end (Stripe + HubSpot + Google Ads → BigQuery → Slack alert) | Demo completes in <10 min with no human intervention except the approval click |
| T4.5 | Add a "show reasoning" toggle that reveals the agent's chain-of-thought per step | UI checkbox renders the rationale field per step |

**Phase 4 done when:** A non-technical person can drive the demo through the UI and produce a working data product without coaching.

### Phase 5 — Hardening (Days 19–24)

| ID | Task | Done when... |
|---|---|---|
| T5.1 | Failure handling: connector setup fails, schema mismatch, auth expiry — each surfaces a clear UI error and a retry path | All three failure cases tested with realistic scenarios |
| T5.2 | Cost estimate: before `create_connector` runs, show estimated monthly cost based on Fivetran pricing tiers (approximation OK) | Approval gate UI shows a $ figure |
| T5.3 | README, architecture diagram, demo script, CONTRIBUTING.md | All present in `docs/` and root |
| T5.4 | One-command deploy script | `./deploy.sh` (or `make deploy`) rebuilds and pushes both Cloud Run services |
| T5.5 | Practice the demo run end-to-end 5+ times against a clean Fivetran account | Timed at <3 min for the speakable narrative portion |

### Phase 6 — Demo video + submit (Days 25–30)

| ID | Task | Done when... |
|---|---|---|
| T6.1 | Write the demo script (60 sec problem framing, 90 sec agent in action, 30 sec close) | `docs/demo_script.md` complete |
| T6.2 | Record demo (screen capture + voiceover), edit to ~3 min | MP4 file rendered, uploaded to YouTube as unlisted, link verified |
| T6.3 | Final repo polish: license at root, README badges, clean commit history | GitHub "About" sidebar shows MIT, README renders cleanly |
| T6.4 | Submit on Devpost with Fivetran track selected | Submission visible in "My projects" |
| T6.5 | Have one outside person clone the repo and follow the README — fix what they can't get working | Outside person successfully runs the demo |

---

## 9. Definition of done for the whole project

A judge can:

1. Click the hosted URL → load the PipelinePilot UI in their browser
2. Watch the 3-minute demo video from the Devpost page
3. Clone the public GitHub repo, see the MIT license, follow the README, and reproduce the setup
4. Read the architecture diagram and immediately understand the Fivetran integration
5. Try the live demo themselves with a fresh Fivetran trial

…and at every step, the Fivetran integration is *visibly load-bearing*, not decorative.

---

## 10. References

- Hackathon: https://rapid-agent.devpost.com/
- Fivetran track resources: https://rapid-agent.devpost.com/details/fivetran-resources
- Fivetran MCP server: https://github.com/fivetran/fivetran-mcp
- Fivetran MCP blog post (Dec 2025): https://www.fivetran.com/blog/integrate-data-faster-using-natural-language-fivetran-and-mcp
- Fivetran REST API auth: https://fivetran.com/docs/rest-api/getting-started#authentication
- Fivetran → BigQuery setup: https://fivetran.com/docs/destinations/bigquery/setup-guide
- Gemini 3 on Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/docs/start/get-started-with-gemini-3
- Gen AI SDK for Python: https://googleapis.github.io/python-genai/
- Agent Starter Pack (optional reference): https://github.com/GoogleCloudPlatform/agent-starter-pack
- Cloud Run quickstart: https://cloud.google.com/run/docs/quickstarts

---

## 11. Open questions (resolve as we go)

- **OQ1** — Does `bgus-genai-poc2` allow public Cloud Run? If not, we use IAP.
- **OQ2** — Does Fivetran's hackathon support extend trials? Ask on Discord.
- **OQ3** — Do we want Slack alerts or email alerts in the demo? Slack is more visual; email is more universal. Pick by Day 18.
- **OQ4** — Should we use the `gemini-3.1-pro-preview-customtools` variant for the executor (better at custom tool use, same price)? Test in Phase 3.

---

## 12. Changelog

- **2026-05-12** — Initial plan committed. Phase 1 scripts ready.
