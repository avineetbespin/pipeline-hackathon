# PipelinePilot - Deployment URLs

## Production Services

### Agent Backend
- **URL:** https://pipelinepilot-agent-956500419273.us-central1.run.app
- **Health:** https://pipelinepilot-agent-956500419273.us-central1.run.app/health
- **API Docs:** https://pipelinepilot-agent-956500419273.us-central1.run.app/docs
- **Purpose:** Main agent API with Gemini planning and execution

### MCP Server (Fivetran Tools)
- **URL:** https://pipelinepilot-mcp-956500419273.us-central1.run.app
- **Health:** https://pipelinepilot-mcp-956500419273.us-central1.run.app/health
- **Purpose:** HTTP wrapper for Fivetran MCP tools

## GCP Resources

- **Project ID:** bgus-genai-poc2
- **Project Number:** 956500419273
- **Region:** us-central1
- **Dataset:** pipelinepilot (BigQuery)
- **Service Account:** pipelinepilot-agent@bgus-genai-poc2.iam.gserviceaccount.com
- **Container Registry:** us-central1-docker.pkg.dev/bgus-genai-poc2/pipelinepilot

## Container Images

- **Agent Backend:** us-central1-docker.pkg.dev/bgus-genai-poc2/pipelinepilot/agent-backend:latest
- **MCP Server:** us-central1-docker.pkg.dev/bgus-genai-poc2/pipelinepilot/mcp-server:latest

## External Services

- **Fivetran Account:** https://fivetran.com/dashboard
  - Group: "Warehouse" (ID: predicament_glisten)
  - Connectors: 0 (as of 2026-05-13)

## Quick Test Commands

```bash
# Test agent health
curl https://pipelinepilot-agent-956500419273.us-central1.run.app/health

# Create a plan
curl -X POST https://pipelinepilot-agent-956500419273.us-central1.run.app/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{"goal": "List my Fivetran groups"}'

# Test MCP server
curl https://pipelinepilot-mcp-956500419273.us-central1.run.app/health
curl https://pipelinepilot-mcp-956500419273.us-central1.run.app/api/v1/groups
```

---
Last Updated: 2026-05-13
