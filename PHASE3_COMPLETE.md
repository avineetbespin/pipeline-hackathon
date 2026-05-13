# Phase 3 Complete - Core Agent Loop

**Date:** 2026-05-13  
**Status:** ✅ Fully Functional  

## What Was Built

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User Request (HTTP API)                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Agent Backend (Cloud Run)                                   │
│  https://pipelinepilot-agent-*.us-central1.run.app          │
│                                                              │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐   │
│  │  Planner    │──▶│  Executor    │──▶│ State Manager  │   │
│  │ (Gemini 3.1)│   │ (Async Loop) │   │ (In-Memory)    │   │
│  └─────────────┘   └──────┬───────┘   └────────────────┘   │
└────────────────────────────┼────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
    ┌─────────────────────┐   ┌──────────────────┐
    │  MCP Server         │   │  BigQuery        │
    │  (Cloud Run)        │   │  (Direct API)    │
    │  Fivetran Tools     │   │  SQL/Views       │
    └──────────┬──────────┘   └──────────────────┘
               │
               ▼
    ┌─────────────────────┐
    │  Fivetran API       │
    │  (SaaS)             │
    └─────────────────────┘
```

## Deployed Services

### 1. MCP Server (Fivetran Tools)
- **URL:** https://pipelinepilot-mcp-956500419273.us-central1.run.app
- **Purpose:** HTTP wrapper for Fivetran operations
- **Endpoints:**
  - `GET /health` - Health check
  - `GET /api/v1/groups` - List Fivetran groups
  - `GET /api/v1/groups/{id}/connectors` - List connectors
  - `GET /api/v1/connectors/{id}` - Get connector details
  - `POST /api/v1/connectors` - Create connector (requires approval)
  - `POST /api/v1/connectors/{id}/sync` - Trigger sync (requires approval)

### 2. Agent Backend (Main Service)
- **URL:** https://pipelinepilot-agent-956500419273.us-central1.run.app
- **Purpose:** Autonomous planning and execution engine
- **Endpoints:**
  - `GET /health` - Health check
  - `POST /api/v1/run` - Create and execute a plan
  - `GET /api/v1/run/{id}` - Get execution status
  - `GET /api/v1/plans` - List recent plans
  - `POST /api/v1/approvals/{id}` - Approve/reject a step

## Code Structure

```
pipeline-hackathon/
├── agent/                          # Agent backend
│   ├── main.py                     # FastAPI application
│   ├── planner_v2.py              # Gemini-based planner
│   ├── executor.py                # Execution engine
│   ├── models.py                  # Pydantic data models
│   ├── state_memory.py            # In-memory state management
│   └── tools/
│       ├── fivetran.py            # Fivetran tool wrappers
│       └── bigquery.py            # BigQuery tool wrappers
│
├── mcp/                           # MCP server
│   ├── http_wrapper.py            # HTTP API wrapper
│   ├── server.py                  # Original Fivetran MCP server
│   └── open-api-definitions/      # API schemas
│
├── infra/                         # Deployment configs
│   ├── Dockerfile.agent           # Agent backend container
│   ├── Dockerfile.mcp             # MCP server container
│   ├── cloudbuild-agent.yaml      # Agent build config
│   └── cloudbuild-mcp.yaml        # MCP build config
│
└── scripts/                       # Verification scripts
    ├── test_deployed_agent.py     # Test deployed agent
    ├── test_mcp_cloudrun.py       # Test deployed MCP
    └── ...
```

## Key Features Implemented

### 1. Structured Planning
- Gemini 3.1 Pro creates JSON execution plans
- Steps include tool name, arguments, and approval requirements
- Automatic detection of write operations requiring approval

### 2. Tool Execution
- **Fivetran Tools:**
  - `list_groups()` - List workspaces
  - `list_connectors(group_id)` - List connectors
  - `get_connector(connector_id)` - Get details
  - `list_destinations()` - List destinations
  - `create_connector(config)` - Create connector [REQUIRES APPROVAL]
  - `sync_connector(connector_id)` - Trigger sync [REQUIRES APPROVAL]
  
- **BigQuery Tools:**
  - `run_query(sql)` - Execute SELECT queries
  - `create_view(name, sql)` - Create/update views [REQUIRES APPROVAL]
  - `list_tables(dataset)` - List tables
  - `get_table_schema(table)` - Get schema

### 3. Approval Gates
- All write operations flagged with `requires_approval: true`
- Executor pauses at approval steps
- State saved in memory (Firestore integration ready)
- Approval flow: create request → wait → approve/reject → continue

### 4. State Management
- Plans stored with all step details
- Execution state tracked (running, completed, failed)
- Approval requests tracked with timestamps
- In-memory for Phase 3 (Firestore ready for Phase 4)

## Example API Usage

### Create and Execute a Plan

```bash
# Create a plan
curl -X POST https://pipelinepilot-agent-956500419273.us-central1.run.app/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "List my Fivetran connectors"}'

# Response
{
  "plan_id": "9396f7ec-16f3-4187-9eb3-17193666bac0",
  "execution_id": "9396f7ec-16f3-4187-9eb3-17193666bac0",
  "status": "running",
  "message": "Created plan with 2 steps"
}

# Check status
curl https://pipelinepilot-agent-956500419273.us-central1.run.app/api/v1/run/9396f7ec-16f3-4187-9eb3-17193666bac0

# Response includes full plan with results
{
  "execution_id": "...",
  "status": "completed",
  "plan": {
    "steps": [
      {
        "description": "List all Fivetran groups",
        "tool_name": "list_groups",
        "status": "completed",
        "result": {"data": {"items": [...]}}
      }
    ]
  }
}
```

## Testing Commands

```bash
# Test deployed agent
python scripts/test_deployed_agent.py

# Test deployed MCP server
python scripts/test_mcp_cloudrun.py

# Test Gemini access
python scripts/02_verify_gemini.py

# Test Fivetran credentials
python scripts/03_verify_fivetran.py --from-secret-manager
```

## Configuration

### Environment Variables (Agent Backend)
- `GOOGLE_CLOUD_PROJECT` = bgus-genai-poc2
- `GOOGLE_CLOUD_LOCATION` = global (required for Gemini 3.x)
- `GOOGLE_GENAI_USE_VERTEXAI` = True
- `BIGQUERY_DATASET` = pipelinepilot
- `FIVETRAN_MCP_URL` = https://pipelinepilot-mcp-*.us-central1.run.app

### Secrets (Secret Manager)
- `fivetran-api-key` - Fivetran API key
- `fivetran-api-secret` - Fivetran API secret

## Known Limitations (To Address in Phase 4)

1. **No result passing between steps** - Planner creates placeholders like `<group_id_from_step_1>` but executor doesn't extract and pass results between steps yet
2. **In-memory state** - Lost on restart; need Firestore Native mode
3. **No UI** - All interaction via API
4. **Single-group assumption** - Assumes first Fivetran group
5. **No cost estimation** - Approval gate shows placeholder cost messages

## Performance

- **Plan creation:** ~2-3 seconds (Gemini API latency)
- **Single step execution:** ~1-3 seconds (network + API)
- **Total for simple query:** ~5-10 seconds end-to-end

## Next Steps (Phase 4)

1. **Result passing** - Extract values from step results and inject into subsequent steps
2. **React UI** - Visual plan builder and approval interface
3. **Multi-source demo** - Full Stripe + HubSpot + Google Ads pipeline
4. **Slack alerts** - Cloud Scheduler integration
5. **Firestore migration** - Production state management
6. **Cost estimation** - Real Fivetran pricing integration

## Success Metrics

✅ Agent deployed and accessible via HTTPS  
✅ Gemini 3.1 Pro creating valid execution plans  
✅ Executor running plans against live Fivetran account  
✅ Approval gates detecting write operations  
✅ All read operations working (groups, connectors, destinations)  
✅ BigQuery tools integrated and ready  
✅ MCP server handling all Fivetran API calls  

## Files Added/Modified in Phase 3

**New Files:**
- `agent/main.py` - FastAPI backend
- `agent/planner_v2.py` - Structured planner
- `agent/executor.py` - Execution engine
- `agent/models.py` - Data models
- `agent/state_memory.py` - State management
- `agent/tools/bigquery.py` - BigQuery tools
- `infra/Dockerfile.agent` - Agent container
- `infra/cloudbuild-agent.yaml` - Build config
- `scripts/test_deployed_agent.py` - Deployment test

**Modified Files:**
- `agent/tools/fivetran.py` - Added all tool functions
- `requirements.txt` - Added dependencies

---

**Phase 3 Complete:** 2026-05-13 at 12:25 PM PST
