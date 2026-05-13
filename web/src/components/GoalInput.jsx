import { useState } from 'react'

export default function GoalInput({ onSubmit, loading }) {
  const [goal, setGoal] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (goal.trim() && !loading) {
      onSubmit(goal.trim())
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          What do you want to build?
        </h2>
        <p className="text-gray-600">
          Describe your data integration goal in plain English. PipelinePilot will plan and execute the pipeline for you.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Example: Show me all connectors in my Fivetran account, or create a view that joins Stripe revenue with Google Ads spend..."
            rows={4}
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none disabled:bg-gray-50 disabled:text-gray-500"
          />

          <button
            type="submit"
            disabled={!goal.trim() || loading}
            className="w-full px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating plan...
              </span>
            ) : (
              'Create Pipeline'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
