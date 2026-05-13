import ApprovalGate from './ApprovalGate'

const STATUS_STYLES = {
  pending: 'bg-gray-100 text-gray-700 border-gray-300',
  in_progress: 'bg-blue-100 text-blue-700 border-blue-300 animate-pulse',
  completed: 'bg-green-100 text-green-700 border-green-300',
  failed: 'bg-red-100 text-red-700 border-red-300',
  waiting_approval: 'bg-yellow-100 text-yellow-700 border-yellow-300',
}

const STATUS_ICONS = {
  pending: '⏳',
  in_progress: '⚙️',
  completed: '✓',
  failed: '✗',
  waiting_approval: '⏸',
}

export default function PlanDisplay({ plan, onApprove, onReject }) {
  if (!plan) return null

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Execution Plan</h2>
        <p className="text-sm text-gray-600">{plan.goal}</p>
        {plan.estimated_duration_minutes && (
          <p className="text-xs text-gray-500 mt-1">
            Estimated duration: {plan.estimated_duration_minutes} minutes
          </p>
        )}
      </div>

      <div className="space-y-4">
        {plan.steps && plan.steps.map((step, idx) => (
          <div
            key={step.step_id || idx}
            className={`border rounded-lg p-4 transition-all ${STATUS_STYLES[step.status] || STATUS_STYLES.pending}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-start space-x-3 flex-1">
                <span className="text-2xl">{STATUS_ICONS[step.status] || '○'}</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    Step {idx + 1}: {step.description}
                  </h3>
                  <div className="mt-1 text-xs space-y-1">
                    <p className="text-gray-600">
                      Tool: <code className="bg-gray-100 px-1 py-0.5 rounded">{step.tool_name}</code>
                    </p>
                    {step.arguments && Object.keys(step.arguments).length > 0 && (
                      <p className="text-gray-600">
                        Args: <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">
                          {JSON.stringify(step.arguments)}
                        </code>
                      </p>
                    )}
                  </div>
                </div>
              </div>
              {step.requires_approval && (
                <span className="ml-2 px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                  Approval Required
                </span>
              )}
            </div>

            {/* Show approval gate if waiting */}
            {step.status === 'waiting_approval' && step.requires_approval && (
              <ApprovalGate
                step={step}
                onApprove={onApprove}
                onReject={onReject}
              />
            )}

            {/* Show result if completed */}
            {step.status === 'completed' && step.result && (
              <div className="mt-3 p-3 bg-white bg-opacity-50 rounded text-xs">
                <p className="font-medium text-gray-700 mb-1">Result:</p>
                <pre className="text-gray-600 overflow-x-auto">
                  {JSON.stringify(step.result, null, 2).slice(0, 300)}
                  {JSON.stringify(step.result).length > 300 && '...'}
                </pre>
              </div>
            )}

            {/* Show error if failed */}
            {step.status === 'failed' && step.error && (
              <div className="mt-3 p-3 bg-red-50 rounded text-xs">
                <p className="font-medium text-red-700 mb-1">Error:</p>
                <p className="text-red-600">{step.error}</p>
              </div>
            )}

            {/* Show timing if available */}
            {(step.started_at || step.completed_at) && (
              <div className="mt-2 text-xs text-gray-500">
                {step.started_at && (
                  <span>Started: {new Date(step.started_at).toLocaleTimeString()}</span>
                )}
                {step.completed_at && (
                  <span className="ml-3">
                    Completed: {new Date(step.completed_at).toLocaleTimeString()}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
