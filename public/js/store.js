/**
 * Samaroh (समारोह) - Reactive Client Store & Normalizer
 * Manages celebration state, active user, guest list, language, and theme.
 */

function normalizeEvent(raw) {
  if (!raw || typeof raw !== 'object' || raw.detail || raw.error) {
    return {
      id: 'demo-wedding-jaipur',
      title: "Riya & Kabir's Royal Vivaha & Sangeet",
      event_type: 'wedding',
      culture: 'Marwari Hindu',
      city: 'Jaipur',
      target_budget: 4500000,
      guest_count: 350,
      target_date: '2026-12-15',
      blessing_note: 'May every celebration begin with auspicious blessings and joy.',
      auspicious_guidance: '',
      disclaimer: ''
    };
  }
  return {
    id: raw.id || 'celebration-plan',
    title: raw.title || raw.celebration_title || raw.name || 'Celebration Plan',
    event_type: (raw.event_type || 'wedding').toLowerCase(),
    culture: raw.culture || 'Indian Tradition',
    city: raw.city || 'India',
    target_budget: Number(raw.target_budget) || 0,
    guest_count: Number(raw.guest_count) || 0,
    target_date: raw.target_date || raw.date || '2026-12-15',
    blessing_note: raw.blessing_note || 'May every celebration begin with auspicious blessings and joy.',
    auspicious_guidance: raw.auspicious_guidance || '',
    disclaimer: raw.disclaimer || ''
  };
}

class EventStore {
  constructor() {
    this.state = {
      activeEventId: 'demo-wedding-jaipur',
      events: [],
      activeEvent: null,
      budgets: [],
      tasks: [],
      vendors: [],
      ideas: [],
      guests: [],
      currentUser: {
        uid: 'demo-user',
        name: 'Guest Explorer',
        email: 'guest@samaroh.app',
        is_demo: true
      },
      language: localStorage.getItem('samaroh-lang') || 'en',
      theme: localStorage.getItem('samaroh-theme') || 'light',
      isSynthesizing: false
    };
    this.listeners = [];
  }

  resetCelebration(eventId) {
    this.state.activeEventId = eventId;
    this.state.budgets = [];
    this.state.tasks = [];
    this.state.vendors = [];
    this.state.ideas = [];
    this.state.guests = [];
    this.notify();
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
  }

  setState(partialState) {
    if (partialState.activeEvent) {
      partialState.activeEvent = normalizeEvent(partialState.activeEvent);
    }
    if (partialState.guests !== undefined && !Array.isArray(partialState.guests)) {
      partialState.guests = [];
    }
    if (partialState.budgets !== undefined && !Array.isArray(partialState.budgets)) {
      partialState.budgets = [];
    }
    if (partialState.tasks !== undefined && !Array.isArray(partialState.tasks)) {
      partialState.tasks = [];
    }
    if (partialState.vendors !== undefined && !Array.isArray(partialState.vendors)) {
      partialState.vendors = [];
    }
    if (partialState.ideas !== undefined && !Array.isArray(partialState.ideas)) {
      partialState.ideas = [];
    }
    this.state = { ...this.state, ...partialState };
    this.notify();
  }

  setTheme(theme) {
    this.state.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('samaroh-theme', theme);
    this.notify();
  }

  toggleTheme() {
    this.setTheme(this.state.theme === 'dark' ? 'light' : 'dark');
  }

  setLanguage(lang) {
    this.state.language = lang;
    localStorage.setItem('samaroh-lang', lang);
    this.notify();
  }

  setCurrentUser(user) {
    this.state.currentUser = user;
    this.notify();
  }
}

window.normalizeEvent = normalizeEvent;
window.store = new EventStore();
