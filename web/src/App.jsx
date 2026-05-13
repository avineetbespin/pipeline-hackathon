import { useState, useEffect } from 'react'
import GoalInput from './components/GoalInput'
import PlanDisplay from './components/PlanDisplay'
import ExecutionStatus from './components/ExecutionStatus'
import { AgentAPI } from './api/agent'

function App() {
  const [execution, setExecution] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pollInterval, setPollInterval] = useState(null)

  // Poll for status updates while execution is running
  useEffect(() => {
    if (execution && execution.status === 'running') {
      const interval = setInterval(async () => {
        try {
          const updated = await AgentAPI.getRunStatus(execution.execution_id)
          setExecution(updated)

          // Stop polling if completed or failed
          if (updated.status !== 'running') {
            clearInterval(interval)
            setPollInterval(null)
          }
        } catch (err) {
          console.error('Polling error:', err)
        }
      }, 2000) // Poll every 2 seconds

      setPollInterval(interval)

      return () => clearInterval(interval)
    }
  }, [execution?.execution_id, execution?.status])

  const handleSubmitGoal = async (goal) => {
    setLoading(true)
    setError(null)

    try {
      // Create and start execution
      const result = await AgentAPI.createRun(goal)

      // Fetch full execution details
      const fullExecution = await AgentAPI.getRunStatus(result.execution_id)
      setExecution(fullExecution)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (approvalId) => {
    try {
      await AgentAPI.approveStep(approvalId)

      // Refresh execution state
      if (execution) {
        const updated = await AgentAPI.getRunStatus(execution.execution_id)
        setExecution(updated)
      }
    } catch (err) {
      setError(`Approval failed: ${err.message}`)
    }
  }

  const handleReject = async (approvalId, reason) => {
    try {
      await AgentAPI.rejectStep(approvalId, reason)

      // Refresh execution state
      if (execution) {
        const updated = await AgentAPI.getRunStatus(execution.execution_id)
        setExecution(updated)
      }
    } catch (err) {
      setError(`Rejection failed: ${err.message}`)
    }
  }

  const handleReset = () => {
    setExecution(null)
    setError(null)
    if (pollInterval) {
      clearInterval(pollInterval)
      setPollInterval(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                PipelinePilot
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Autonomous data integration powered by Gemini 3.1 Pro
              </p>
            </div>
            {execution && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                New Pipeline
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {!execution ? (
          <div className="max-w-3xl mx-auto">
            <GoalInput onSubmit={handleSubmitGoal} loading={loading} />

            {/* Example prompts */}
            <div className="mt-8 p-6 bg-white rounded-lg border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                Example Goals:
              </h3>
              <div className="space-y-2">
                {[
                  'Show me what Fivetran connectors I currently have set up',
                  'List all tables in my BigQuery pipelinepilot dataset',
                  'What destinations are configured in my Fivetran account?',
                ].map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSubmitGoal(example)}
                    disabled={loading}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 bg-gray-50 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Plan */}
            <div>
              <PlanDisplay
                plan={execution.plan}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            </div>

            {/* Right: Execution Status */}
            <div>
              <ExecutionStatus execution={execution} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Built for the Google Cloud Rapid Agent Hackathon (Fivetran Track) •{' '}
            <a
              href="https://github.com/avineetbespin/pipeline-hackathon"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700"
            >
              View Source
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
