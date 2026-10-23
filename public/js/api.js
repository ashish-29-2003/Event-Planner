/**
 * Utsav (उत्सव) - API Client
 * Connects UI with Python FastAPI backend endpoints.
 */
const API = {
  baseUrl: window.location.origin,

  async getHealth() {
    const res = await fetch(`${this.baseUrl}/api/health`);
    return await res.json();
  },

  async listEvents() {
    const res = await fetch(`${this.baseUrl}/api/events`);
    return await res.json();
  },

  async getEvent(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}`);
    return await res.json();
  },

  async getBudget(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/budget`);
    return await res.json();
  },

  async updateBudget(id, items) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/budget`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(items)
    });
    return await res.json();
  },

  async rebalanceBudget(targetBudget, changedCategory, newAmount, currentItems) {
    const res = await fetch(`${this.baseUrl}/api/ai/rebalance-budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_budget: targetBudget,
        changed_category: changedCategory,
        new_amount: newAmount,
        current_items: currentItems
      })
    });
    return await res.json();
  },

  async getTasks(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/tasks`);
    return await res.json();
  },

  async toggleTask(eventId, taskId, newStatus) {
    const res = await fetch(`${this.baseUrl}/api/events/${eventId}/tasks/${taskId}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    return await res.json();
  },

  async getVendors(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/vendors`);
    return await res.json();
  },

  async getIdeas(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/ideas`);
    return await res.json();
  },

  async generatePlan(brief) {
    const res = await fetch(`${this.baseUrl}/api/ai/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(brief)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Plan generation failed');
    }
    return await res.json();
  },

  async getMuhurat(culture, eventType) {
    const res = await fetch(`${this.baseUrl}/api/ai/muhurat?culture=${encodeURIComponent(culture)}&event_type=${encodeURIComponent(eventType)}`);
    return await res.json();
  },

  async getNextMilestoneLink(id) {
    const res = await fetch(`${this.baseUrl}/api/export/${id}/next-milestone-link`);
    return await res.json();
  }
};

window.API = API;
