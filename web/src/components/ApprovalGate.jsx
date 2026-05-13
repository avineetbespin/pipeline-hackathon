import { useState } from 'react'

export default function ApprovalGate({ step, onApprove, onReject }) {
  const [rejecting, setRejecting] = useState(false)
  const [rejectReason, setRejectReason] = useState('')
  const [loading, setLoading] = useState(false)

  // Extract approval_id from step (might be in step.approval_id or step.step_id)
  const approvalId = step.approval_id || step.step_id

  const handleApprove = async () => {
    setLoading(true)
    try {
      await onApprove(approvalId)
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async () => {
    setLoading(true)
    try {
      await onReject(approvalId, rejectReason || 'User rejected')
      setRejecting(false)
      setRejectReason('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
      <div className="mb-3">
        <h4 className="font-semibold text-yellow-900 mb-2">Approval Required</h4>
        <p className="text-sm text-yellow-800 mb-2">
          This operation will modify your Fivetran or BigQuery configuration.
        </p>

        {/* Cost estimate if available */}
        {step.cost_estimate && (
          <p className="text-sm text-yellow-800 mb-2">
            <span className="font-medium">Cost Impact:</span> {step.cost_estimate}
          </p>
        )}

        {/* Details */}
        <div className="text-xs text-yellow-700 space-y-1">
          <p>
            <span className="font-medium">Tool:</span> {step.tool_name}
          </p>
          {step.arguments && (
            <p>
              <span className="font-medium">Arguments:</span>
              <code className="ml-1 bg-yellow-100 px-1 py-0.5 rounded">
                {JSON.stringify(step.arguments, null, 2)}
              </code>
            </p>
          )}
        </div>
      </div>

      {!rejecting ? (
        <div className="flex space-x-3">
          <button
            onClick={handleApprove}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded hover:bg-green-700 disabled:bg-gray-300 transition-colors text-sm"
          >
            {loading ? 'Approving...' : 'Approve'}
          </button>
          <button
            onClick={() => setRejecting(true)}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-red-600 text-white font-medium rounded hover:bg-red-700 disabled:bg-gray-300 transition-colors text-sm"
          >
            Reject
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <input
            type="text"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Reason for rejection (optional)"
            className="w-full px-3 py-2 border border-yellow-300 rounded text-sm focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          />
          <div className="flex space-x-3">
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-red-600 text-white font-medium rounded hover:bg-red-700 disabled:bg-gray-300 transition-colors text-sm"
            >
              {loading ? 'Rejecting...' : 'Confirm Rejection'}
            </button>
            <button
              onClick={() => {
                setRejecting(false)
                setRejectReason('')
              }}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded hover:bg-gray-300 disabled:bg-gray-100 transition-colors text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
