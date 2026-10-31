/**
 * Samaroh (समारोह) - Firebase Authentication Web Client
 * Supports Google Sign-In with popup & redirect fallback, Firebase Auth Emulator,
 * reactive auth-state listeners, and automatic ID token refresh for API requests.
 */

const Auth = {
  authInstance: null,
  currentUser: null,
  idToken: null,

  // Public Firebase client configuration (safe for frontend exposure)
  config: window.FIREBASE_CONFIG || {
    apiKey: window.FIREBASE_API_KEY || "demo-firebase-web-api-key",
    authDomain: "samaroh-celebrations.firebaseapp.com",
    projectId: "samaroh-celebrations",
    storageBucket: "samaroh-celebrations.appspot.com",
    messagingSenderId: "1234567890",
    appId: "1:1234567890:web:samaroh-ui"
  },

  init() {
    // Stage R12 Session Purge: Invalidate stale mock tokens and upgrade storage version
    const STORAGE_VERSION_KEY = 'samaroh-storage-version';
    const CURRENT_STORAGE_VERSION = '2.0.0';
    const currentVersion = localStorage.getItem(STORAGE_VERSION_KEY);

    const savedToken = localStorage.getItem('samaroh-auth-token');
    const isMockToken = savedToken && (savedToken.startsWith('test-token-') || savedToken.startsWith('mock-token-'));

    if (currentVersion !== CURRENT_STORAGE_VERSION || isMockToken) {
      localStorage.removeItem('samaroh-auth-token');
      localStorage.removeItem('samaroh-auth-user');
      localStorage.setItem(STORAGE_VERSION_KEY, CURRENT_STORAGE_VERSION);
    }

    try {
      if (typeof firebase !== 'undefined' && firebase.apps) {
        if (!firebase.apps.length) {
          firebase.initializeApp(this.config);
        }
        this.authInstance = firebase.auth();

        // Connect to Firebase Auth Emulator if running locally on port 9099
        if (
          window.USE_AUTH_EMULATOR ||
          (window.location.hostname === '127.0.0.1' && window.location.port === '9099')
        ) {
          this.authInstance.useEmulator('http://127.0.0.1:9099');
        }

        // Listen for Firebase auth state changes
        this.authInstance.onAuthStateChanged(async (user) => {
          if (user) {
            const token = await user.getIdToken();
            this.handleUserSignedIn({
              uid: user.uid,
              name: user.displayName || user.email.split('@')[0],
              email: user.email,
              picture: user.photoURL,
              is_demo: false
            }, token);
          } else {
            this.handleUserSignedOut();
          }
        });
        return;
      }
    } catch (e) {
      console.warn("Firebase Web SDK initialization notice:", e);
    }

    // Check for persisted local session (for demo / emulator test environments)
    const saved = localStorage.getItem('samaroh-auth-user');
    const savedToken = localStorage.getItem('samaroh-auth-token');
    if (saved && savedToken) {
      try {
        const parsed = JSON.parse(saved);
        this.handleUserSignedIn(parsed, savedToken);
      } catch (err) {
        this.handleUserSignedOut();
      }
    } else {
      this.handleUserSignedOut();
    }
  },

  async signInWithGoogle() {
    if (this.authInstance && typeof firebase !== 'undefined') {
      try {
        const provider = new firebase.auth.GoogleAuthProvider();
        provider.addScope('email');
        provider.addScope('profile');
        const result = await this.authInstance.signInWithPopup(provider);
        const token = await result.user.getIdToken();
        this.handleUserSignedIn({
          uid: result.user.uid,
          name: result.user.displayName || result.user.email.split('@')[0],
          email: result.user.email,
          picture: result.user.photoURL,
          is_demo: false
        }, token);
        return;
      } catch (err) {
        // Fallback to redirect if popup was blocked by browser
        if (err.code === 'auth/popup-blocked') {
          const provider = new firebase.auth.GoogleAuthProvider();
          return this.authInstance.signInWithRedirect(provider);
        }
        console.warn("Firebase popup sign-in notice:", err);
      }
    }

    // If running in production or without emulator, notify the user honestly
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!isLocalhost) {
      if (window.showToast) {
        window.showToast("Sign-in is currently unconfigured in this demo deployment. You can browse all celebrations and create drafts.", "info");
      } else {
        alert("Sign-in is currently unconfigured in this demo deployment. You can browse all celebrations and create drafts.");
      }
      return;
    }

    // Localhost test fallback only
    const testUser = {
      uid: "google-user-local",
      name: "Local Tester",
      email: "tester@samaroh.local",
      picture: null,
      is_demo: false
    };
    const testToken = `test-token-${testUser.uid}`;
    this.handleUserSignedIn(testUser, testToken);
  },

  async signOutUser() {
    if (this.authInstance) {
      try {
        await this.authInstance.signOut();
      } catch (e) {
        console.warn("Sign-out warning:", e);
      }
    }
    this.handleUserSignedOut();
  },

  handleUserSignedIn(user, token) {
    this.currentUser = user;
    this.idToken = token;
    localStorage.setItem('samaroh-auth-user', JSON.stringify(user));
    localStorage.setItem('samaroh-auth-token', token);

    if (window.API) {
      window.API.setAuthToken(token);
    }
    if (window.store) {
      window.store.setCurrentUser(user);
    }
    this.renderUI(user);
  },

  handleUserSignedOut() {
    this.currentUser = null;
    this.idToken = null;
    localStorage.removeItem('samaroh-auth-user');
    localStorage.removeItem('samaroh-auth-token');

    const demoUser = {
      uid: "demo-user",
      name: "Guest Explorer",
      email: "guest@samaroh.app",
      is_demo: true
    };

    if (window.API) {
      window.API.setAuthToken(null);
    }
    if (window.store) {
      window.store.setCurrentUser(demoUser);
    }
    this.renderUI(demoUser);
  },

  async getIdToken() {
    if (this.authInstance && this.authInstance.currentUser) {
      this.idToken = await this.authInstance.currentUser.getIdToken(true);
      if (window.API) window.API.setAuthToken(this.idToken);
      return this.idToken;
    }
    return this.idToken;
  },

  renderUI(user) {
    const banner = document.getElementById('demo-mode-banner');
    const signinBtn = document.getElementById('btn-auth-signin');
    const profileMenu = document.getElementById('user-profile-menu');
    const userNameSpan = document.getElementById('user-display-name');
    const avatarImg = document.getElementById('user-avatar');
    const avatarFallback = document.getElementById('user-avatar-fallback');
    const greetingEl = document.getElementById('cultural-greeting');

    if (user && !user.is_demo) {
      // User is authenticated
      if (banner) banner.style.display = 'none';
      if (signinBtn) signinBtn.style.display = 'none';
      if (profileMenu) profileMenu.style.display = 'flex';
      if (userNameSpan) userNameSpan.textContent = user.name || "Celebration Host";

      if (user.picture && avatarImg) {
        avatarImg.src = user.picture;
        avatarImg.style.display = 'block';
        if (avatarFallback) avatarFallback.style.display = 'none';
      } else if (avatarFallback) {
        avatarFallback.textContent = (user.name || "U")[0].toUpperCase();
        avatarFallback.style.display = 'flex';
        if (avatarImg) avatarImg.style.display = 'none';
      }

      if (greetingEl) {
        const safeName = window.escapeHTML ? window.escapeHTML(user.name.split(' ')[0]) : user.name.split(' ')[0];
        greetingEl.innerHTML = `<strong style="color: var(--text-primary);">नमस्ते</strong>, ${safeName}`;
      }
    } else {
      // Guest / Demo mode
      if (banner) banner.style.display = 'flex';
      if (signinBtn) signinBtn.style.display = 'inline-flex';
      if (profileMenu) profileMenu.style.display = 'none';

      if (greetingEl) {
        greetingEl.innerHTML = `<strong style="color: var(--text-primary);">शुभ आरम्भ</strong>, Guest Explorer`;
      }
    }
  }
};

window.Auth = Auth;
document.addEventListener('DOMContentLoaded', () => {
  Auth.init();
});
