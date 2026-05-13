# Quick Reference - PipelinePilot

**Use this file to quickly find URLs, commands, and key information.**

---

## 🔗 Live URLs

### Production Services
- **Agent Backend:** https://pipelinepilot-agent-956500419273.us-central1.run.app
- **Frontend UI:** https://pipelinepilot-web-956500419273.us-central1.run.app (deploying)
- **MCP Server:** https://pipelinepilot-mcp-956500419273.us-central1.run.app
- **GitHub Repo:** https://github.com/avineetbespin/pipeline-hackathon

### Health Checks
```bash
# Agent
curl -k https://pipelinepilot-agent-956500419273.us-central1.run.app/health

# MCP
curl -k https://pipelinepilot-mcp-956500419273.us-central1.run.app/health

# Frontend (once deployed)
curl -k https://pipelinepilot-web-956500419273.us-central1.run.app
```

---

## 🚀 Deployment Commands

### Agent Backend
```bash
export CLOUDSDK_PYTHON="C:/Python313/python.exe"
gcloud builds submit --config=infra/cloudbuild-agent.yaml --project=bgus-genai-poc2
```

### React Frontend
```bash
export CLOUDSDK_PYTHON="C:/Python313/python.exe"
gcloud builds submit --config=infra/cloudbuild-web.yaml --project=bgus-genai-poc2
```

### MCP Server
```bash
export CLOUDSDK_PYTHON="C:/Python313/python.exe"
gcloud builds submit --config=infra/cloudbuild-mcp.yaml --project=bgus-genai-poc2
```

---

## 🧪 Testing Commands

### Result Passing Test
```bash
python test_result_passing.py
```

### Agent API Test
```bash
python scripts/test_deployed_agent.py
```

### Local Development
```bash
# Agent backend
cd agent && python -m uvicorn main:app --reload --port 8080

# Frontend
cd web && npm install && npm run dev
```

---

## 📁 Key Files

### Agent Code
- `agent/main.py` - FastAPI application
- `agent/planner_v2.py` - Gemini-based planner
- `agent/executor.py` - Execution engine (result passing logic)
- `agent/models.py` - Pydantic data models
- `agent/tools/fivetran.py` - 7 Fivetran operations
- `agent/tools/bigquery.py` - 4 BigQuery operations

### Frontend Code
- `web/src/App.jsx` - Main application
- `web/src/components/GoalInput.jsx` - Natural language input
- `web/src/components/PlanDisplay.jsx` - Execution plan display
- `web/src/components/ApprovalGate.jsx` - Approval UI
- `web/src/components/ExecutionStatus.jsx` - Progress tracker
- `web/src/api/agent.js` - API client

### Infrastructure
- `infra/Dockerfile.agent` - Agent container
- `infra/Dockerfile.mcp` - MCP container
- `infra/Dockerfile.web` - Frontend container
- `infra/cloudbuild-agent.yaml` - Agent build config
- `infra/cloudbuild-mcp.yaml` - MCP build config
- `infra/cloudbuild-web.yaml` - Frontend build config
- `infra/nginx.conf` - Frontend nginx config

### Documentation
- `IMPLEMENTATION_PLAN.md` - Full project plan
- `CLAUDE.md` - Conventions for Claude Code
- `PHASE4_PROGRESS.md` - Phase 4 progress report
- `TESTING_PLAN.md` - Test scenarios
- `SESSION_SUMMARY_PHASE4.md` - Session summary

---

## 🔑 Environment Variables

### Local Development
```bash
export GOOGLE_CLOUD_PROJECT=bgus-genai-poc2
export GOOGLE_CLOUD_LOCATION=global
export GOOGLE_GENAI_USE_VERTEXAI=True
export BIGQUERY_DATASET=pipelinepilot
export FIVETRAN_MCP_URL=https://pipelinepilot-mcp-956500419273.us-central1.run.app
```

### Frontend
```bash
# .env.local
VITE_API_URL=https://pipelinepilot-agent-956500419273.us-central1.run.app
```

---

## 🎯 Phase 4 TODO

- [x] Fix result passing
- [x] Build React UI
- [x] Deploy agent backend
- [ ] Deploy React frontend (in progress)
- [ ] Test end-to-end
- [ ] Build scheduler.py
- [ ] Add reasoning toggle
- [ ] Full multi-source demo

---

## 📊 Project Stats

- **GCP Project:** bgus-genai-poc2
- **Region:** us-central1
- **Service Account:** pipelinepilot-agent@bgus-genai-poc2.iam.gserviceaccount.com
- **BigQuery Dataset:** pipelinepilot
- **Artifact Registry:** us-central1-docker.pkg.dev/bgus-genai-poc2/pipelinepilot

---

## 🐛 Common Issues

### gcloud Python Error
```bash
# Fix: Set Python path
export CLOUDSDK_PYTHON="C:/Python313/python.exe"
```

### SSL Certificate Error (curl)
```bash
# Fix: Use -k flag to skip verification
curl -k https://...
```

### npm ci Fails
```bash
# Fix: Already fixed - we use npm install now
```

### Image Not Found in Cloud Run
```bash
# Fix: Already fixed - explicit docker push step added
```

---

## 📞 Support Resources

- **Hackathon:** https://rapid-agent.devpost.com/
- **Fivetran Track:** https://rapid-agent.devpost.com/details/fivetran-resources
- **Fivetran MCP:** https://github.com/fivetran/fivetran-mcp
- **Gemini Docs:** https://cloud.google.com/vertex-ai/generative-ai/docs/start/get-started-with-gemini-3
- **Cloud Run Docs:** https://cloud.google.com/run/docs

---

**Last Updated:** 2026-05-13 15:00 PST
