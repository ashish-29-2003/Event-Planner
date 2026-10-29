/**
 * Samaroh (समारोह) - Reactive Client Store
 * Manages celebration state, active user, guest list, language, and theme.
 */
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

window.store = new EventStore();
