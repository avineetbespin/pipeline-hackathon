import { useState, useEffect } from 'react'

export default function ExecutionStatus({ execution }) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

  if (!execution) return null

  const { status, plan, started_at, completed_at } = execution

  // Calculate progress
  const totalSteps = plan?.steps?.length || 0
  const completedSteps = plan?.steps?.filter(s => s.status === 'completed').length || 0
  const failedSteps = plan?.steps?.filter(s => s.status === 'failed').length || 0
  const inProgressSteps = plan?.steps?.filter(s => s.status === 'in_progress').length || 0
  const waitingApprovalSteps = plan?.steps?.filter(s => s.status === 'waiting_approval').length || 0

  const progressPercentage = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0

  // Track elapsed time for running executions
  useEffect(() => {
    if (status === 'running' && started_at) {
      const interval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - new Date(started_at).getTime()) / 1000)
        setElapsedSeconds(elapsed)
      }, 1000)

      return () => clearInterval(interval)
    }
  }, [status, started_at])

  // Status color
  const statusColors = {
    running: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6 sticky top-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Execution Status</h2>

      {/* Overall Status */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Status:</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[status] || 'text-gray-600 bg-gray-100'}`}>
            {status.toUpperCase()}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mb-2">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                status === 'completed' ? 'bg-green-500' :
                status === 'failed' ? 'bg-red-500' :
                'bg-blue-500'
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <p className="text-xs text-gray-600 mt-1 text-right">
            {completedSteps} / {totalSteps} steps completed ({progressPercentage}%)
          </p>
        </div>
      </div>

      {/* Step Breakdown */}
      <div className="mb-6 space-y-2">
        {completedSteps > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">✓ Completed</span>
            <span className="font-semibold text-green-600">{completedSteps}</span>
          </div>
        )}
        {inProgressSteps > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">⚙️ In Progress</span>
            <span className="font-semibold text-blue-600">{inProgressSteps}</span>
          </div>
        )}
        {waitingApprovalSteps > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">⏸ Waiting Approval</span>
            <span className="font-semibold text-yellow-600">{waitingApprovalSteps}</span>
          </div>
        )}
        {failedSteps > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">✗ Failed</span>
            <span className="font-semibold text-red-600">{failedSteps}</span>
          </div>
        )}
      </div>

      {/* Timing */}
      <div className="border-t border-gray-200 pt-4 space-y-2 text-sm">
        {started_at && (
          <div className="flex justify-between">
            <span className="text-gray-600">Started:</span>
            <span className="font-medium text-gray-900">
              {new Date(started_at).toLocaleTimeString()}
            </span>
          </div>
        )}
        {status === 'running' && started_at && (
          <div className="flex justify-between">
            <span className="text-gray-600">Elapsed:</span>
            <span className="font-medium text-blue-600">
              {elapsedSeconds}s
            </span>
          </div>
        )}
        {completed_at && (
          <div className="flex justify-between">
            <span className="text-gray-600">Completed:</span>
            <span className="font-medium text-gray-900">
              {new Date(completed_at).toLocaleTimeString()}
            </span>
          </div>
        )}
        {started_at && completed_at && (
          <div className="flex justify-between">
            <span className="text-gray-600">Duration:</span>
            <span className="font-medium text-gray-900">
              {Math.round((new Date(completed_at) - new Date(started_at)) / 1000)}s
            </span>
          </div>
        )}
      </div>

      {/* Long-running notice */}
      {status === 'running' && elapsedSeconds > 60 && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-xs text-yellow-800">
            <strong>Still working...</strong> Some operations (like Fivetran API calls) can take 2-5 minutes on first request.
          </p>
        </div>
      )}

      {/* Execution ID */}
      <div className="mt-4 p-3 bg-gray-50 rounded text-xs">
        <p className="text-gray-600 mb-1">Execution ID:</p>
        <code className="text-gray-800 break-all">{execution.execution_id}</code>
      </div>
    </div>
  )
}
