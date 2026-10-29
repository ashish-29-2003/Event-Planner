/**
 * Samaroh (समारोह) - API Client
 * Connects UI with Python FastAPI backend endpoints, Firebase Auth tokens,
 * and Google Maps Places discovery proxy.
 */
const API = {
  baseUrl: window.location.origin,
  authToken: null,
  appCheckToken: null,

  setAuthToken(token) {
    this.authToken = token;
  },

  setAppCheckToken(token) {
    this.appCheckToken = token;
  },

  getHeaders(custom = {}) {
    const headers = { 'Content-Type': 'application/json', ...custom };
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    if (this.appCheckToken) {
      headers['X-Firebase-AppCheck'] = this.appCheckToken;
    }
    return headers;
  },

  async getHealth() {
    const res = await fetch(`${this.baseUrl}/api/health`);
    return await res.json();
  },

  async listEvents() {
    const res = await fetch(`${this.baseUrl}/api/events`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async getEvent(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async getBudget(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/budget`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async updateBudget(id, items) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/budget`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(items)
    });
    return await res.json();
  },

  async rebalanceBudget(targetBudget, changedCategory, newAmount, currentItems) {
    const res = await fetch(`${this.baseUrl}/api/ai/rebalance-budget`, {
      method: 'POST',
      headers: this.getHeaders(),
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
    const res = await fetch(`${this.baseUrl}/api/events/${id}/tasks`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async toggleTask(eventId, taskId, newStatus) {
    const res = await fetch(`${this.baseUrl}/api/events/${eventId}/tasks/${taskId}/toggle`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ status: newStatus })
    });
    return await res.json();
  },

  async getVendors(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/vendors`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async getIdeas(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/ideas`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async getGuests(id) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/guests`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async addGuest(id, guest) {
    const res = await fetch(`${this.baseUrl}/api/events/${id}/guests`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(guest)
    });
    return await res.json();
  },

  async updateGuestRSVP(eventId, guestId, status) {
    const res = await fetch(`${this.baseUrl}/api/events/${eventId}/guests/${guestId}/rsvp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ status })
    });
    return await res.json();
  },

  async searchPlaces(query, city = 'Jaipur', category = 'venue') {
    const params = new URLSearchParams({ query, city, category });
    const res = await fetch(`${this.baseUrl}/api/places/search?${params.toString()}`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async generatePlan(brief) {
    const res = await fetch(`${this.baseUrl}/api/ai/plan`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(brief)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Plan generation failed');
    }
    return await res.json();
  },

  async getMuhurat(culture, eventType) {
    const res = await fetch(`${this.baseUrl}/api/ai/muhurat?culture=${encodeURIComponent(culture)}&event_type=${encodeURIComponent(eventType)}`, {
      headers: this.getHeaders()
    });
    return await res.json();
  },

  async getNextMilestoneLink(id) {
    const res = await fetch(`${this.baseUrl}/api/export/${id}/next-milestone-link`, {
      headers: this.getHeaders()
    });
    return await res.json();
  }
};

window.API = API;
