/**
 * Utsav (उत्सव) - Reactive Client Store
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
      theme: localStorage.getItem('utsav-theme') || 'light',
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
    localStorage.setItem('utsav-theme', theme);
    this.notify();
  }

  toggleTheme() {
    this.setTheme(this.state.theme === 'dark' ? 'light' : 'dark');
  }
}

window.store = new EventStore();
