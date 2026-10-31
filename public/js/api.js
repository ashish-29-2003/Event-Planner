/**
 * Samaroh (समारोह) - API Client & Cold-Start Resilience Layer
 * Connects UI with Python FastAPI backend, handles Render idle cold-starts with
 * pre-warming and exponential backoff retry, and provides automatic graceful
 * degradation to static demo celebration data if the server is unreachable.
 */
const API = {
  baseUrl: (window.__API_BASE__ && window.__API_BASE__.trim()) || window.location.origin,
  authToken: null,
  appCheckToken: null,
  isDegraded: false,
  isServerWaking: false,
  hasPrewarmed: false,

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

  setServerWaking(waking) {
    this.isServerWaking = waking;
    const pill = document.getElementById('server-waking-pill');
    if (pill) {
      pill.style.display = waking ? 'flex' : 'none';
    }
  },

  setDegradedMode(degraded) {
    this.isDegraded = degraded;
    this.setServerWaking(false);
    const banner = document.getElementById('degraded-demo-banner');
    if (banner) {
      banner.style.display = degraded ? 'flex' : 'none';
    }
  },

  prewarm() {
    if (this.hasPrewarmed) return;
    this.hasPrewarmed = true;

    // Show waking indicator if server does not respond within 2.5s
    const wakingTimer = setTimeout(() => {
      this.setServerWaking(true);
    }, 2500);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 75000);

    fetch(`${this.baseUrl}/api/health`, { signal: controller.signal })
      .then(res => {
        clearTimeout(wakingTimer);
        clearTimeout(timeoutId);
        if (res.ok) {
          this.setServerWaking(false);
        } else {
          this.setServerWaking(true);
        }
      })
      .catch(() => {
        clearTimeout(wakingTimer);
        clearTimeout(timeoutId);
        // Server might be sleeping; keep waking state active
        this.setServerWaking(true);
      });
  },

  async fetchWithRetry(endpoint, options = {}, isIdempotent = true, fallbackPath = null, maxTimeoutMs = 85000) {
    if (this.isDegraded && fallbackPath) {
      try {
        const fbRes = await fetch(fallbackPath);
        if (fbRes.ok) return await fbRes.json();
      } catch (e) {
        console.warn('Degraded fetch failed:', e);
      }
    }

    const startTime = Date.now();
    let attempt = 0;
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;

    while (true) {
      attempt++;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 25000); // 25s per attempt
        const res = await fetch(url, {
          ...options,
          headers: this.getHeaders(options.headers || {}),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          this.setServerWaking(false);
          return await res.json();
        }

        const isColdStartStatus = [502, 503, 504].includes(res.status);
        const elapsed = Date.now() - startTime;

        if (!isIdempotent || !isColdStartStatus || elapsed >= maxTimeoutMs) {
          if (fallbackPath) {
            console.warn(`API returned ${res.status}. Falling back to static demo data: ${fallbackPath}`);
            this.setDegradedMode(true);
            const fbRes = await fetch(fallbackPath);
            return await fbRes.json();
          }
          const errData = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(errData.detail || `Server error (${res.status})`);
        }
      } catch (err) {
        const elapsed = Date.now() - startTime;
        if (!isIdempotent || elapsed >= maxTimeoutMs) {
          if (fallbackPath) {
            console.warn(`API connection failed (${err.message}). Falling back to static demo data: ${fallbackPath}`);
            this.setDegradedMode(true);
            const fbRes = await fetch(fallbackPath);
            return await fbRes.json();
          }
          throw err;
        }
      }

      // Idempotent retry loop (waking sleeping backend)
      this.setServerWaking(true);
      const delay = Math.min(6000, 1000 * Math.pow(1.4, attempt));
      await new Promise(r => setTimeout(r, delay));
    }
  },

  async getHealth() {
    return await this.fetchWithRetry('/api/health', {}, true, null, 15000);
  },

  async listEvents() {
    return await this.fetchWithRetry('/api/events', {}, true, '/demo-data/events.json');
  },

  async getEvent(id) {
    return await this.fetchWithRetry(`/api/events/${id}`, {}, true, `/demo-data/${id}.json`);
  },

  async getBudget(id) {
    return await this.fetchWithRetry(`/api/events/${id}/budget`, {}, true, `/demo-data/${id}_budget.json`);
  },

  async updateBudget(id, items) {
    return await this.fetchWithRetry(`/api/events/${id}/budget`, {
      method: 'PUT',
      body: JSON.stringify(items)
    }, false, null);
  },

  async rebalanceBudget(targetBudget, changedCategory, newAmount, currentItems) {
    return await this.fetchWithRetry('/api/ai/rebalance-budget', {
      method: 'POST',
      body: JSON.stringify({
        target_budget: targetBudget,
        changed_category: changedCategory,
        new_amount: newAmount,
        current_items: currentItems
      })
    }, false, null);
  },

  async getTasks(id) {
    return await this.fetchWithRetry(`/api/events/${id}/tasks`, {}, true, `/demo-data/${id}_tasks.json`);
  },

  async toggleTask(eventId, taskId, newStatus) {
    return await this.fetchWithRetry(`/api/events/${eventId}/tasks/${taskId}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ status: newStatus })
    }, false, null);
  },

  async getVendors(id) {
    return await this.fetchWithRetry(`/api/events/${id}/vendors`, {}, true, `/demo-data/${id}_vendors.json`);
  },

  async getIdeas(id) {
    return await this.fetchWithRetry(`/api/events/${id}/ideas`, {}, true, `/demo-data/${id}_ideas.json`);
  },

  async getGuests(id) {
    return await this.fetchWithRetry(`/api/events/${id}/guests`, {}, true, `/demo-data/${id}_guests.json`);
  },

  async addGuest(id, guest) {
    return await this.fetchWithRetry(`/api/events/${id}/guests`, {
      method: 'POST',
      body: JSON.stringify(guest)
    }, false, null);
  },

  async updateGuestRSVP(eventId, guestId, status) {
    return await this.fetchWithRetry(`/api/events/${eventId}/guests/${guestId}/rsvp`, {
      method: 'POST',
      body: JSON.stringify({ status })
    }, false, null);
  },

  async searchPlaces(query, city = 'Jaipur', category = 'venue') {
    const params = new URLSearchParams({ query, city, category });
    return await this.fetchWithRetry(`/api/places/search?${params.toString()}`, {}, true, null, 25000);
  },

  async generatePlan(brief) {
    return await this.fetchWithRetry('/api/ai/plan', {
      method: 'POST',
      body: JSON.stringify(brief)
    }, false, null);
  },

  async getMuhurat(culture, eventType) {
    const params = new URLSearchParams({ culture, event_type: eventType });
    return await this.fetchWithRetry(`/api/ai/muhurat?${params.toString()}`, {}, true, null, 25000);
  },

  async getNextMilestoneLink(id) {
    return await this.fetchWithRetry(`/api/export/${id}/next-milestone-link`, {}, true, null, 25000);
  },

  async getShareToken(id, ttlDays = 7) {
    return await this.fetchWithRetry(`/api/export/${id}/share-token?ttl_days=${ttlDays}`, {
      method: 'POST'
    }, false, null);
  }
};

// Initiate non-blocking pre-warm probe on page load
if (typeof window !== 'undefined') {
  window.API = API;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => API.prewarm());
  } else {
    API.prewarm();
  }
}
