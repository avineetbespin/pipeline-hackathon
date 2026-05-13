# Phase 4 Ready - Quick Start Guide

This document helps you (or another Claude instance) pick up exactly where we left off.

## Current Status (2026-05-13)

✅ **Phase 1-3 Complete**
- All infrastructure deployed and tested
- Agent backend live on Cloud Run
- MCP server live on Cloud Run
- Gemini 3.1 Pro integration working
- Fivetran API connected
- 195 files committed to GitHub

## Production URLs

```
Agent API: https://pipelinepilot-agent-956500419273.us-central1.run.app
MCP Server: https://pipelinepilot-mcp-956500419273.us-central1.run.app
GitHub: https://github.com/avineetbespin/pipeline-hackathon
```

## Phase 4 Critical Path

### 1. Fix Result Passing (Priority 1)
**Problem:** Planner creates placeholders like `<group_id_from_step_1>` but executor doesn't extract values.

**Solution needed:**
- Modify `agent/executor.py` to extract values from `step.result`
- Add result context to subsequent steps
- Update `agent/planner_v2.py` to use `{{step_1.result.data.items[0].id}}` syntax

**Files to modify:**
- `agent/executor.py` - Add result extraction logic
- `agent/planner_v2.py` - Update prompt with result reference syntax

### 2. Build React UI (Priority 2)
**What to build:**
- Text input for natural language goals
- Plan display with step details
- Approve/reject buttons for write operations
- Real-time execution status
- Results display

**Structure:**
```
web/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── App.jsx
    ├── components/
    │   ├── GoalInput.jsx
    │   ├── PlanDisplay.jsx
    │   ├── ApprovalGate.jsx
    │   └── ExecutionStatus.jsx
    └── api/
        └── agent.js
```

**Tech stack:** React + Vite + Tailwind (already in plan)

### 3. Multi-Source Demo (Priority 3)
**Implement anchor scenario:**
- Stripe connector for revenue
- HubSpot connector for conversion data
- Google Ads connector for spend
- BigQuery view for blended CAC payback
- Slack alert on threshold breach

**Files to create:**
- `agent/tools/scheduler.py` - Cloud Scheduler integration
- Example plan JSON for full demo scenario

### 4. Slack Alerts (Priority 4)
**Add Cloud Scheduler:**
- Daily query execution
- Slack webhook posting
- Threshold detection

## Testing Commands

```bash
# Verify deployments
curl https://pipelinepilot-agent-956500419273.us-central1.run.app/health
python scripts/test_deployed_agent.py

# Run local agent (for development)
cd agent && python -m uvicorn main:app --host 0.0.0.0 --port 8080

# Test Fivetran connectivity
python scripts/03_verify_fivetran.py --from-secret-manager

# Test Gemini
python scripts/02_verify_gemini.py
```

## Environment Setup

```bash
# Activate venv
source .venv/Scripts/activate  # or .venv\Scripts\activate on Windows

# Set PYTHONPATH for local development
export PYTHONPATH="."

# GCP authentication
export CLOUDSDK_PYTHON="C:/Python313/python.exe"
gcloud config set project bgus-genai-poc2
```

## Key Files Reference

**Agent Backend:**
- `agent/main.py` - FastAPI app
- `agent/planner_v2.py` - Plan generation
- `agent/executor.py` - Plan execution ⚠️ NEEDS RESULT PASSING FIX
- `agent/models.py` - Data models

**Tools:**
- `agent/tools/fivetran.py` - 7 Fivetran operations
- `agent/tools/bigquery.py` - 4 BigQuery operations

**Infrastructure:**
- `infra/Dockerfile.agent` - Agent container
- `infra/cloudbuild-agent.yaml` - Build config

## Known Issues to Address

1. ⚠️ **Result passing** - Most critical, blocks complex multi-step plans
2. **In-memory state** - Migrate to Firestore Native
3. **No cost estimation** - Add real Fivetran pricing
4. **Limited error handling** - Improve error messages
5. **No UI** - Build React frontend

## Implementation Plan Timeline

- **Days 11-18:** Phase 4 (UI + demo) ← WE ARE HERE
- **Days 19-24:** Phase 5 (hardening)
- **Days 25-30:** Phase 6 (video + submission)
- **June 11, 2026:** Deadline

## Memory Files Created

The following memory files were saved for continuity:
1. `project_phase3_complete.md`
2. `project_architecture.md`
3. `project_deployment.md`
4. `project_phase4_next.md`
5. `reference_hackathon.md`

Read these first when resuming!

## Quick Win Tasks (Easy Wins for Momentum)

1. ✅ Fix result passing in executor (2-3 hours)
2. Create basic React UI shell (2 hours)
3. Add real-time plan updates via polling (1 hour)
4. Improve error messages (1 hour)
5. Add cost estimate to approval gate (1 hour)

## Resources

- **Fivetran API Docs:** https://fivetran.com/docs/rest-api
- **Gemini 3 Docs:** https://cloud.google.com/vertex-ai/generative-ai/docs/start/get-started-with-gemini-3
- **Implementation Plan:** See `IMPLEMENTATION_PLAN.md`
- **Phase 3 Details:** See `PHASE3_COMPLETE.md`

---

**Start with:** Fix result passing in `agent/executor.py`, then build React UI. The hardest technical work is done!

Last Updated: 2026-05-13
