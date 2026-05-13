# PipelinePilot Web UI

React frontend for PipelinePilot autonomous data integration agent.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Configuration

Set the backend API URL via environment variable:

```bash
# .env.local
VITE_API_URL=https://pipelinepilot-agent-956500419273.us-central1.run.app
```

Or use the proxy in development (defaults to http://localhost:8080).

## Features

- Natural language goal input
- Real-time plan execution display
- Approval gates for write operations
- Live progress tracking
- Step-by-step result visualization

## Components

- `GoalInput` - Text area for entering pipeline goals
- `PlanDisplay` - Shows the execution plan with step details
- `ApprovalGate` - Approve/reject UI for write operations
- `ExecutionStatus` - Live progress and status indicators
