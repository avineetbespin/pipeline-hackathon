/**
 * API client for PipelinePilot agent backend
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export class AgentAPI {
  /**
   * Create and start executing a plan
   * @param {string} goal - Natural language goal
   * @returns {Promise<{plan_id: string, execution_id: string, status: string}>}
   */
  static async createRun(goal) {
    const response = await fetch(`${API_BASE}/api/v1/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get execution status and results
   * @param {string} executionId
   * @returns {Promise<Object>}
   */
  static async getRunStatus(executionId) {
    const response = await fetch(`${API_BASE}/api/v1/run/${executionId}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * List recent executions
   * @returns {Promise<Array>}
   */
  static async listRuns() {
    const response = await fetch(`${API_BASE}/api/v1/plans`);

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Approve a step
   * @param {string} approvalId
   * @returns {Promise<Object>}
   */
  static async approveStep(approvalId) {
    const response = await fetch(`${API_BASE}/api/v1/approvals/${approvalId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: true }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Reject a step
   * @param {string} approvalId
   * @param {string} reason
   * @returns {Promise<Object>}
   */
  static async rejectStep(approvalId, reason) {
    const response = await fetch(`${API_BASE}/api/v1/approvals/${approvalId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved: false, reason }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }
}
