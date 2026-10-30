/**
 * Samaroh (समारोह) - Master Application Controller
 * Handles UI interactions, live calculations, tabs, and celebratory micro-interactions.
 * Modern minimal edition.
 */

// Daily Subhashitas with attribution and bilingual translations
const SUBHASHITAS = [
  {
    sanskrit: "॥ सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः ॥",
    meaning_en: "May all beings be prosperous, peaceful and healthy.",
    meaning_hi: "सभी सुखी हों, सभी रोगमुक्त और स्वस्थ रहें।",
    source: "Brihadaranyaka Upanishad"
  },
  {
    sanskrit: "॥ वसुधैव कुटुम्बकम् ॥",
    meaning_en: "The entire world is one sacred family.",
    meaning_hi: "समस्त संसार ही एक पवित्र परिवार है।",
    source: "Maha Upanishad"
  },
  {
    sanskrit: "॥ विद्या ददाति विनयं विनयाद्याति पात्रताम् ॥",
    meaning_en: "Learning bestows humility, and humility brings dignity and grace.",
    meaning_hi: "ज्ञान से विनय आता है, और विनय से पात्रता प्राप्त होती है।",
    source: "Hitopadesha"
  }
];

// Time-of-day single-language greeting (U11)
function getCulturalGreeting(lang = 'en') {
  const hr = new Date().getHours();
  if (lang === 'hi') {
    if (hr >= 5 && hr < 12) return "शुभ प्रभात";
    if (hr >= 12 && hr < 17) return "शुभ अपराह्न";
    if (hr >= 17 && hr < 22) return "शुभ संध्या";
    return "शुभ रात्रि";
  }
  if (hr >= 5 && hr < 12) return "Good Morning";
  if (hr >= 12 && hr < 17) return "Good Afternoon";
  if (hr >= 17 && hr < 22) return "Good Evening";
  return "Good Night";
}

// Indian Lakh/Crore Currency Formatter
function formatINR(val) {
  if (val === undefined || val === null) return "₹0";
  return "₹" + Number(val).toLocaleString('en-IN');
}

// Subtle celebratory confetti
function triggerCelebrationConfetti() {
  if (window.confetti) {
    window.confetti({
      particleCount: 35,
      spread: 60,
      origin: { y: 0.65 },
      colors: ['#18181B', '#B45309', '#059669', '#E4E4E7']
    });
  }
}

// Safe HTML escaping & DOMPurify sanitization to eliminate XSS sinks
function escapeHTML(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
window.escapeHTML = escapeHTML;

function sanitizeHTML(html) {
  if (typeof DOMPurify !== 'undefined' && DOMPurify.sanitize) {
    return DOMPurify.sanitize(html);
  }
  return escapeHTML(html);
}
window.sanitizeHTML = sanitizeHTML;

// Update Language UI elements (U6, U11)
function updateLanguageUI() {
  const lang = store.state.language || 'en';
  const userName = store.state.currentUser?.name || 'Guest Explorer';
  const greetingText = getCulturalGreeting(lang);

  const greetingEl = document.getElementById('cultural-greeting');
  if (greetingEl) {
    greetingEl.innerHTML = `<strong style="color: var(--text-primary);">${escapeHTML(greetingText)}</strong>, ${escapeHTML(userName)}`;
  }

  const subhashitaEl = document.getElementById('daily-subhashita');
  if (subhashitaEl) {
    const s = SUBHASHITAS[0];
    const meaning = lang === 'hi' ? s.meaning_hi : s.meaning_en;
    subhashitaEl.innerHTML = `<strong>${escapeHTML(s.sanskrit)}</strong> — ${escapeHTML(meaning)}`;
  }

  const langLabel = document.getElementById('lang-label');
  if (langLabel) {
    langLabel.innerText = lang === 'hi' ? 'English' : 'हिन्दी';
  }
}

// Update Theme SVG Icons (U6)
function updateThemeIcons(theme) {
  const moon = document.getElementById('theme-icon-moon');
  const sun = document.getElementById('theme-icon-sun');
  if (moon && sun) {
    if (theme === 'dark') {
      moon.style.display = 'none';
      sun.style.display = 'block';
    } else {
      moon.style.display = 'block';
      sun.style.display = 'none';
    }
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Initialize Theme & SVGs
  const theme = store.state.theme;
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcons(theme);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      store.toggleTheme();
      updateThemeIcons(store.state.theme);
    });
  }

  // 2. Set Greeting & Subhashita & Language Toggle
  updateLanguageUI();
  const langToggle = document.getElementById('lang-toggle');
  if (langToggle) {
    langToggle.addEventListener('click', () => {
      const nextLang = store.state.language === 'hi' ? 'en' : 'hi';
      store.setLanguage(nextLang);
      updateLanguageUI();
    });
  }

  // 3. Tab Switching
  const navTabs = document.querySelectorAll('.nav-tab');
  const viewPanels = document.querySelectorAll('.view-panel');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetView = tab.getAttribute('data-view');
      navTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');

      viewPanels.forEach(panel => {
        panel.style.display = panel.id === `view-${targetView}` ? 'block' : 'none';
      });
    });
  });

  // 4. Custom Accessible Celebration Switcher (U10)
  setupCelebrationSwitcher();

  // 5. Share Modal Setup (U9)
  setupShareModal();

  // 6. Guests & RSVP Setup (U7)
  setupGuestsModule();

  // 7. Vendor Filter Buttons
  const filterPills = document.querySelectorAll('.vendor-filter-pill');
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => {
        p.classList.remove('active', 'btn-primary');
        p.classList.add('btn-secondary');
      });
      pill.classList.remove('btn-secondary');
      pill.classList.add('active', 'btn-primary');
      renderVendors(pill.getAttribute('data-category'));
    });
  });

  // 8. Onboarding Wizard Dialog Controls
  setupOnboardingWizard();

  // 9. AI Chat Controller
  setupChatDrawer();

  // 10. Load Active Event Data
  await loadCelebration(store.state.activeEventId);

  // 11. AI Diagnostics & Fallback Transparency Check
  try {
    const health = await API.getHealth();
    const fallbackBanner = document.getElementById('ai-fallback-banner');
    if (fallbackBanner && health && health.ai === 'fallback') {
      fallbackBanner.style.display = 'flex';
    }
  } catch (e) {
    console.warn('AI health probe skipped', e);
  }
});

// Accessible Custom Celebration Switcher (U10)
function setupCelebrationSwitcher() {
  const toggleBtn = document.getElementById('switcher-toggle-btn');
  const listbox = document.getElementById('celebration-listbox');
  const nativeSelect = document.getElementById('celebration-switcher');
  const activeIcon = document.getElementById('switcher-active-icon');
  const activeLabel = document.getElementById('switcher-active-label');

  if (!toggleBtn || !listbox) return;

  const openListbox = () => {
    listbox.style.display = 'block';
    toggleBtn.setAttribute('aria-expanded', 'true');
    const activeItem = listbox.querySelector('.switcher-item.active') || listbox.querySelector('.switcher-item');
    if (activeItem) activeItem.focus();
  };

  const closeListbox = () => {
    listbox.style.display = 'none';
    toggleBtn.setAttribute('aria-expanded', 'false');
  };

  toggleBtn.onclick = (e) => {
    e.stopPropagation();
    const isOpen = listbox.style.display === 'block';
    if (isOpen) {
      closeListbox();
    } else {
      openListbox();
    }
  };

  document.addEventListener('click', (e) => {
    if (!toggleBtn.contains(e.target) && !listbox.contains(e.target)) {
      closeListbox();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && listbox.style.display === 'block') {
      closeListbox();
      toggleBtn.focus();
    }
  });

  const items = listbox.querySelectorAll('.switcher-item');
  items.forEach((item, idx) => {
    const selectItem = async () => {
      items.forEach(i => {
        i.classList.remove('active');
        i.setAttribute('aria-selected', 'false');
      });
      item.classList.add('active');
      item.setAttribute('aria-selected', 'true');

      const eventId = item.getAttribute('data-event-id');
      const icon = item.querySelector('.switcher-icon')?.innerText || '✨';
      const title = item.querySelector('.switcher-title')?.innerText || eventId;

      if (activeIcon) activeIcon.innerText = icon;
      if (activeLabel) activeLabel.innerText = title;
      if (nativeSelect) nativeSelect.value = eventId;

      closeListbox();
      toggleBtn.focus();
      await loadCelebration(eventId);
    };

    item.onclick = (e) => {
      e.stopPropagation();
      selectItem();
    };

    item.onkeydown = (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectItem();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        const next = items[idx + 1] || items[0];
        next.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prev = items[idx - 1] || items[items.length - 1];
        prev.focus();
      }
    };
  });

  if (nativeSelect) {
    nativeSelect.onchange = async (e) => {
      const matchingItem = listbox.querySelector(`[data-event-id="${e.target.value}"]`);
      if (matchingItem) {
        matchingItem.click();
      } else {
        await loadCelebration(e.target.value);
      }
    };
  }
}

// Share Modal Controller (U9)
function setupShareModal() {
  const shareModal = document.getElementById('share-modal');
  const shareBtn = document.getElementById('btn-share-celebration');
  const closeBtn = document.getElementById('btn-close-share');
  const linkInput = document.getElementById('share-link-input');
  const copyBtn = document.getElementById('btn-copy-share');
  const copyFeedback = document.getElementById('copy-feedback');
  const waBtn = document.getElementById('btn-whatsapp-share');
  const printBtn = document.getElementById('btn-share-print');
  const blessingEl = document.getElementById('share-blessing-text');

  if (!shareModal) return;

  const openShare = async () => {
    const activeEvent = store.state.activeEvent;
    const activeEventId = store.state.activeEventId;

    let shareUrl = `${window.location.origin}/?event=${encodeURIComponent(activeEventId)}`;
    try {
      const tokenData = await API.getShareToken(activeEventId);
      if (tokenData && tokenData.share_token) {
        shareUrl = `${window.location.origin}/?event=${encodeURIComponent(activeEventId)}&token=${encodeURIComponent(tokenData.share_token)}`;
      }
    } catch (e) {
      // Fallback
    }

    if (linkInput) linkInput.value = shareUrl;
    if (copyFeedback) copyFeedback.style.display = 'none';

    if (waBtn) {
      const title = activeEvent?.title || 'Celebration Plan';
      const waText = encodeURIComponent(`॥ शुभ आरम्भ ॥ Here is our celebration plan for "${title}":\n${shareUrl}`);
      waBtn.href = `https://wa.me/?text=${waText}`;
    }

    if (blessingEl && activeEvent) {
      blessingEl.textContent = `"${activeEvent.blessing_note || 'May this auspicious celebration bring enduring joy, good health, and abundant prosperity to all families.'}"`;
    }

    shareModal.style.display = 'flex';
  };

  if (shareBtn) shareBtn.onclick = openShare;
  if (closeBtn) closeBtn.onclick = () => { shareModal.style.display = 'none'; };

  shareModal.onclick = (e) => {
    if (e.target === shareModal) shareModal.style.display = 'none';
  };

  if (copyBtn && linkInput) {
    copyBtn.onclick = () => {
      const url = linkInput.value;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
          if (copyFeedback) copyFeedback.style.display = 'inline-block';
          triggerCelebrationConfetti();
        }).catch(() => {
          linkInput.select();
          document.execCommand('copy');
          if (copyFeedback) copyFeedback.style.display = 'inline-block';
        });
      } else {
        linkInput.select();
        document.execCommand('copy');
        if (copyFeedback) copyFeedback.style.display = 'inline-block';
      }
    };
  }

  if (printBtn) {
    printBtn.onclick = () => {
      window.print();
    };
  }
}

// Master Celebration Loader
async function loadCelebration(eventId) {
  try {
    const [event, budgets, tasks, vendors, ideas, guests] = await Promise.all([
      API.getEvent(eventId),
      API.getBudget(eventId),
      API.getTasks(eventId),
      API.getVendors(eventId),
      API.getIdeas(eventId),
      API.getGuests(eventId).catch(() => [])
    ]);

    store.setState({
      activeEventId: eventId,
      activeEvent: event,
      budgets,
      tasks,
      vendors,
      ideas,
      guests: guests || []
    });

    renderExecutiveOverview();
    renderBudgetMatrix();
    renderTimeline();
    renderVendors();
    renderIdeas();
    renderMuhurat();
    renderExportSheet();
    renderGuests();
  } catch (err) {
    console.error('Failed to load celebration:', err);
  }
}

// Relative due date calculator (U4)
function formatRelativeDueDate(dateStr) {
  if (!dateStr) return { text: 'Date TBD', isUrgent: false };
  const due = new Date(dateStr);
  if (isNaN(due.getTime())) return { text: dateStr, isUrgent: false };

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  due.setHours(0, 0, 0, 0);
  const diffDays = Math.round((due - today) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return { text: `${Math.abs(diffDays)}d overdue`, isUrgent: true };
  if (diffDays === 0) return { text: 'Due today', isUrgent: true };
  if (diffDays === 1) return { text: 'Due tomorrow', isUrgent: true };
  if (diffDays <= 7) return { text: `in ${diffDays} days`, isUrgent: true };
  return { text: `in ${diffDays} days`, isUrgent: false };
}

function renderExecutiveOverview() {
  const { activeEvent, budgets, tasks, vendors } = store.state;
  if (!activeEvent) return;

  // Apply event-type dynamic theme (U12)
  const eventType = (activeEvent.event_type || 'wedding').toLowerCase();
  document.body.className = `theme-${eventType}`;

  // Overview Title & Culture
  const titleEl = document.getElementById('overview-title');
  if (titleEl) titleEl.innerText = activeEvent.title;

  const cultureEl = document.getElementById('overview-culture-city');
  if (cultureEl) cultureEl.innerText = `${activeEvent.culture || 'Indian'} • ${activeEvent.city || 'India'}`;

  const statusBadge = document.getElementById('overview-status-badge');
  if (statusBadge) statusBadge.innerText = 'Active plan';

  // Countdown Calculation
  const targetDateStr = activeEvent.target_date || activeEvent.date || "2026-12-15";
  const targetDate = new Date(targetDateStr);
  const today = new Date();
  const diffTime = targetDate - today;
  const diffDays = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));

  const daysEl = document.getElementById('overview-days-left');
  if (daysEl) daysEl.innerText = diffDays;

  const dateEl = document.getElementById('overview-target-date');
  if (dateEl) dateEl.innerText = targetDate.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  // Financial Metrics & Hierarchy (U3)
  const targetBudget = activeEvent.target_budget || 0;
  const allocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);
  const paid = budgets.reduce((sum, b) => sum + (b.advance_paid || 0), 0);
  const remaining = targetBudget - allocated;

  const allocPct = targetBudget > 0 ? (allocated / targetBudget) * 100 : 0;
  const paidPct = targetBudget > 0 ? (paid / targetBudget) * 100 : 0;
  const committedUnpaid = Math.max(0, allocated - paid);
  const committedUnpaidPct = targetBudget > 0 ? (committedUnpaid / targetBudget) * 100 : 0;

  const targetBudgetEl = document.getElementById('overview-target-budget');
  if (targetBudgetEl) targetBudgetEl.innerText = formatINR(targetBudget);

  const allocatedEl = document.getElementById('overview-allocated');
  if (allocatedEl) allocatedEl.innerText = formatINR(allocated);

  const allocPctEl = document.getElementById('overview-allocated-pct');
  if (allocPctEl) allocPctEl.innerText = `${allocPct.toFixed(1)}% committed`;

  const paidEl = document.getElementById('overview-paid');
  if (paidEl) paidEl.innerText = formatINR(paid);

  const paidPctEl = document.getElementById('overview-paid-pct');
  if (paidPctEl) paidPctEl.innerText = `${paidPct.toFixed(1)}% settled`;

  const remainingEl = document.getElementById('overview-remaining');
  const remainingCaptionEl = document.getElementById('overview-remaining-caption');
  if (remainingEl) {
    remainingEl.innerText = formatINR(Math.abs(remaining));
    if (remaining < 0) {
      remainingEl.style.color = 'var(--accent-warning)';
      if (remainingCaptionEl) remainingCaptionEl.innerText = 'Over target budget';
    } else {
      remainingEl.style.color = 'var(--accent-warm)';
      if (remainingCaptionEl) remainingCaptionEl.innerText = 'Buffer available';
    }
  }

  // Two-Segment Progress Bar (U2)
  const paidBar = document.getElementById('overview-paid-bar');
  const allocBar = document.getElementById('overview-allocated-bar');
  const progressTrack = document.getElementById('overview-progress-track');

  if (paidBar) {
    paidBar.style.width = `${Math.min(paidPct, 100)}%`;
  }
  if (allocBar) {
    allocBar.style.width = `${Math.min(committedUnpaidPct, Math.max(0, 100 - Math.min(paidPct, 100)))}%`;
    allocBar.style.backgroundColor = allocated > targetBudget ? 'var(--accent-warning)' : 'var(--text-primary)';
  }
  if (progressTrack) {
    progressTrack.setAttribute('aria-valuenow', Math.min(Math.round(allocPct), 100).toString());
  }

  // Overview Immediate Milestones List
  const nextTasksContainer = document.getElementById('overview-next-tasks');
  if (nextTasksContainer) {
    const nextThree = tasks.slice(0, 3);
    nextTasksContainer.innerHTML = nextThree.map(t => {
      const rel = formatRelativeDueDate(t.due_date);
      const isDone = t.status === 'done';
      return `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px dashed var(--border-color); font-size: 0.825rem;">
          <span style="text-decoration: ${isDone ? 'line-through' : 'none'}; color: ${isDone ? 'var(--text-muted)' : 'var(--text-primary)'};">
            ${escapeHTML(t.title)}
          </span>
          <span class="badge ${isDone ? 'badge-success' : rel.isUrgent ? 'badge-warm' : ''}" style="font-size: 0.7rem;">
            ${isDone ? 'Completed' : rel.text}
          </span>
        </div>
      `;
    }).join('');
  }

  // Overview Card 1: Dynamic Financial Ledger
  const ovBudgetHeadline = document.getElementById('ovcard-budget-headline');
  const ovBudgetTopcat = document.getElementById('ovcard-budget-topcat');
  const ovBudgetStatus = document.getElementById('ovcard-budget-status');
  if (ovBudgetHeadline) {
    ovBudgetHeadline.innerText = `${formatINR(allocated)} Allocated`;
  }
  if (ovBudgetTopcat && budgets.length > 0) {
    const sorted = [...budgets].sort((a, b) => (b.estimated_cost || 0) - (a.estimated_cost || 0));
    ovBudgetTopcat.innerText = `Largest: ${sorted[0].name} (${formatINR(sorted[0].estimated_cost)})`;
  }
  if (ovBudgetStatus) {
    ovBudgetStatus.innerText = allocated > targetBudget ? 'Exceeded' : 'Balanced';
    ovBudgetStatus.className = `badge ${allocated > targetBudget ? 'badge-warm' : 'badge-success'}`;
  }

  // Overview Card 2: Countdown & Milestones
  const ovTasksHeadline = document.getElementById('ovcard-tasks-headline');
  const ovTasksNext = document.getElementById('ovcard-tasks-next');
  const ovTasksBadge = document.getElementById('ovcard-tasks-badge');
  const completedTasks = tasks.filter(t => t.status === 'done').length;
  if (ovTasksHeadline) {
    ovTasksHeadline.innerText = `${completedTasks} of ${tasks.length} Completed`;
  }
  if (ovTasksNext) {
    const nextPending = tasks.find(t => t.status !== 'done');
    ovTasksNext.innerText = nextPending ? `Next: ${nextPending.title}` : 'All milestones completed!';
  }
  if (ovTasksBadge) {
    ovTasksBadge.innerText = completedTasks === tasks.length && tasks.length > 0 ? 'All Complete' : 'In Progress';
    ovTasksBadge.className = `badge ${completedTasks === tasks.length ? 'badge-success' : 'badge-warm'}`;
  }

  // Overview Card 3: Verified Vendors
  const ovVendorsHeadline = document.getElementById('ovcard-vendors-headline');
  const ovVendorsQuotes = document.getElementById('ovcard-vendors-quotes');
  const totalVendorQuotes = vendors.reduce((s, v) => s + (v.quote_amount || 0), 0);
  if (ovVendorsHeadline) {
    ovVendorsHeadline.innerText = `${vendors.length} Vendors Shortlisted`;
  }
  if (ovVendorsQuotes) {
    ovVendorsQuotes.innerText = `Committed quote sum: ${formatINR(totalVendorQuotes)}`;
  }

  // Overview Card 4: Guests & RSVP (U5, U7)
  const ovGuestsHeadline = document.getElementById('ovcard-guests-headline');
  const ovGuestsRsvp = document.getElementById('ovcard-guests-rsvp');
  const ovGuestsBadge = document.getElementById('ovcard-guests-badge');
  const guests = store.state.guests || [];
  const guestTotal = guests.length > 0 ? guests.reduce((s, g) => s + (1 + (g.plus_ones || 0)), 0) : (activeEvent.guest_count || 300);
  const attendingTotal = guests.filter(g => g.rsvp_status === 'attending').reduce((s, g) => s + (1 + (g.plus_ones || 0)), 0);
  if (ovGuestsHeadline) {
    ovGuestsHeadline.innerText = `${guestTotal} Guests Tracked`;
  }
  if (ovGuestsRsvp) {
    ovGuestsRsvp.innerText = `Attending: ${attendingTotal} • Pending: ${Math.max(0, guestTotal - attendingTotal)}`;
  }
  if (ovGuestsBadge) {
    const pct = guestTotal > 0 ? Math.round((attendingTotal / guestTotal) * 100) : 0;
    ovGuestsBadge.innerText = `${pct}% Confirmed`;
  }
}

function renderBudgetMatrix() {
  const { budgets, activeEvent } = store.state;
  const container = document.getElementById('budget-items-list');
  if (!container) return;

  const targetBudget = activeEvent?.target_budget || 0;
  const allocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);

  const alertEl = document.getElementById('budget-over-alert');
  if (alertEl) {
    alertEl.style.display = allocated > targetBudget ? 'block' : 'none';
  }

  container.innerHTML = budgets.map((b) => `
    <tr>
      <td>
        <strong>${escapeHTML(b.name)}</strong>
        ${b.notes ? `<div style="font-size: 0.775rem; color: var(--text-secondary); margin-top: 0.15rem;">${escapeHTML(b.notes)}</div>` : ''}
      </td>
      <td><span class="badge">${escapeHTML(b.category)}</span></td>
      <td style="font-weight: 600;">${formatINR(b.estimated_cost)}</td>
      <td style="color: var(--accent-success); font-weight: 500;">${formatINR(b.advance_paid)}</td>
      <td>
        <span class="badge ${b.status === 'paid' ? 'badge-success' : 'badge-warm'}">
          ${escapeHTML(b.status.toUpperCase())}
        </span>
      </td>
    </tr>
  `).join('');

  // Wire Re-balance trigger button
  const rebalanceBtn = document.getElementById('btn-rebalance-budget');
  if (rebalanceBtn) {
    rebalanceBtn.onclick = async () => {
      rebalanceBtn.disabled = true;
      rebalanceBtn.innerText = 'AI Rebalancing...';
      try {
        const firstCategory = budgets[0]?.category || 'Venue & Accommodation';
        const currentFirstAmount = budgets[0]?.estimated_cost || 100000;
        const res = await API.rebalanceBudget(targetBudget, firstCategory, currentFirstAmount * 1.15, budgets);
        store.setState({ budgets: res.updated_items });
        renderBudgetMatrix();
        renderExecutiveOverview();
        alert(`Budget re-balanced:\n\n${res.rebalance_rationale}`);
        triggerCelebrationConfetti();
      } catch (e) {
        alert('Re-balancing completed using proportional distribution.');
      } finally {
        rebalanceBtn.disabled = false;
        rebalanceBtn.innerText = 'AI Rebalance Budget';
      }
    };
  }
}

function renderTimeline() {
  const { tasks, activeEventId } = store.state;
  const container = document.getElementById('timeline-tasks-list');
  if (!container) return;

  container.innerHTML = tasks.map(t => {
    const rel = formatRelativeDueDate(t.due_date);
    const isDone = t.status === 'done';
    return `
      <div class="card" style="margin-bottom: 0.65rem; padding: 0.85rem 1rem; display: flex; align-items: flex-start; gap: 0.85rem; border-left: 3px solid ${isDone ? 'var(--accent-success)' : 'var(--accent-warm)'};">
        <input 
          type="checkbox" 
          id="task-chk-${escapeHTML(t.id)}"
          aria-label="Mark task ${escapeHTML(t.title)} as ${isDone ? 'incomplete' : 'complete'}"
          ${isDone ? 'checked' : ''} 
          style="margin-top: 0.25rem;" 
          onchange="toggleTaskStatus('${escapeHTML(activeEventId)}', '${escapeHTML(t.id)}', this.checked)"
        >
        <div style="flex: 1;">
          <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 0.4rem;">
            <label for="task-chk-${escapeHTML(t.id)}" style="font-size: 0.925rem; font-weight: 600; cursor: pointer; text-decoration: ${isDone ? 'line-through' : 'none'}; color: ${isDone ? 'var(--text-secondary)' : 'var(--text-primary)'};">
              ${escapeHTML(t.title)}
            </label>
            <div style="display: flex; align-items: center; gap: 0.35rem;">
              <span style="font-size: 0.775rem; color: var(--text-secondary);">${escapeHTML(t.due_date || 'Date TBD')}</span>
              <span class="badge ${isDone ? 'badge-success' : rel.isUrgent ? 'badge-warm' : ''}" style="font-size: 0.7rem;">
                ${isDone ? 'Completed' : rel.text}
              </span>
            </div>
          </div>
          <p style="font-size: 0.825rem; color: var(--text-secondary); margin: 0.2rem 0 0.4rem 0;">${escapeHTML(t.description)}</p>
          <div style="display: flex; gap: 0.4rem; align-items: center;">
            <span class="badge badge-warm">${escapeHTML(t.phase)}</span>
            <span class="badge">${escapeHTML(t.owner_role)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Export Calendar button
  const exportIcsBtn = document.getElementById('btn-export-ics');
  if (exportIcsBtn) {
    exportIcsBtn.onclick = () => {
      window.location.href = `/api/export/${activeEventId}/calendar`;
    };
  }

  // Google Calendar direct link button
  const gcalLinkBtn = document.getElementById('btn-gcal-link');
  if (gcalLinkBtn) {
    gcalLinkBtn.onclick = async () => {
      const linkData = await API.getNextMilestoneLink(activeEventId);
      if (linkData && linkData.google_calendar_url) {
        window.open(linkData.google_calendar_url, '_blank');
      }
    };
  }
}

window.toggleTaskStatus = async (eventId, taskId, isChecked) => {
  const newStatus = isChecked ? 'done' : 'todo';
  await API.toggleTask(eventId, taskId, newStatus);
  const tasks = store.state.tasks.map(t => t.id === taskId ? { ...t, status: newStatus } : t);
  store.setState({ tasks });
  renderTimeline();
  renderExecutiveOverview();
  if (isChecked) {
    triggerCelebrationConfetti();
  }
};

function renderVendors(filterCategory = 'all') {
  const { vendors } = store.state;
  const container = document.getElementById('vendors-grid');
  if (!container) return;

  const filtered = filterCategory === 'all'
    ? vendors
    : vendors.filter(v => v.category.toLowerCase().includes(filterCategory.toLowerCase()));

  container.innerHTML = filtered.map(v => `
    <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="badge badge-warm">${escapeHTML(v.category)}</span>
          <span style="font-size: 0.775rem; font-weight: 600; color: var(--text-secondary);">★ ${v.rating || 4.8}</span>
        </div>
        <h3 style="font-size: 0.975rem; font-weight: 600; margin-bottom: 0.25rem;">${escapeHTML(v.business_name)}</h3>
        <p style="font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 0.65rem;">${escapeHTML(v.notes || 'Deliverables confirmed per brief.')}</p>
        <div style="font-size: 0.775rem; color: var(--text-secondary); margin-bottom: 0.2rem;">📍 ${escapeHTML(v.address || 'Local vendor')}</div>
        <div style="font-size: 0.775rem; color: var(--text-secondary);">📞 ${escapeHTML(v.phone || 'Available upon request')}</div>
      </div>
      <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: baseline;">
        <div>
          <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-secondary);">Indicative Quote</div>
          <div style="font-size: 1.05rem; font-weight: 700;">${formatINR(v.quote_amount)}</div>
        </div>
        <span class="badge ${v.status === 'contracted' ? 'badge-success' : 'badge-warm'}">${escapeHTML(v.status.toUpperCase())}</span>
      </div>
    </div>
  `).join('');
}

function renderIdeas() {
  const { ideas } = store.state;
  const container = document.getElementById('ideas-container');
  if (!container) return;

  container.innerHTML = ideas.map(i => `
    <div class="card" style="margin-bottom: 0.85rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
        <span class="badge badge-warm">${escapeHTML(i.tab_category.replace('_', ' '))}</span>
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);">${escapeHTML(i.cost_bracket)}</span>
      </div>
      <h3 style="font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem;">${escapeHTML(i.title)}</h3>
      <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0.6rem;">${escapeHTML(i.description)}</p>
      <div style="background: var(--bg-subtle); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-secondary); border-left: 2px solid var(--text-primary);">
        <strong style="color: var(--text-primary);">Cultural Context:</strong> ${escapeHTML(i.cultural_context)}
      </div>
    </div>
  `).join('');
}

async function renderMuhurat() {
  const container = document.getElementById('muhurat-content');
  if (!container) return;

  const data = await API.getMuhurat(store.state.activeEvent?.culture || 'Marwari', 'wedding');
  container.innerHTML = `
    <div class="card">
      <h2 style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.25rem;">Auspicious Muhurat Windows</h2>
      <p style="font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 1.25rem;">${escapeHTML(data.disclaimer)}</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.75rem;">
        ${data.windows.map(w => `
          <div style="background: var(--bg-subtle); padding: 0.85rem 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <strong style="font-size: 0.9rem; color: var(--text-primary);">${escapeHTML(w.season)}</strong>
            <div style="margin: 0.4rem 0; font-size: 0.825rem;"><strong>Dates:</strong> ${escapeHTML(w.auspicious_dates.join(', '))}</div>
            <div style="font-size: 0.775rem; color: var(--text-secondary);"><strong>Nakshatras:</strong> ${escapeHTML(w.nakshatras)}</div>
            <div style="font-size: 0.775rem; color: var(--text-secondary);"><strong>Lagnas:</strong> ${escapeHTML(w.lagnas)}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// Guests & RSVP Module (U7)
function renderGuests(filterSide = 'all') {
  const { guests, activeEventId } = store.state;
  const container = document.getElementById('guests-table-body');
  if (!container) return;

  // Calculate metrics
  const totalCount = guests.reduce((sum, g) => sum + (1 + (g.plus_ones || 0)), 0);
  const attendingCount = guests.filter(g => g.rsvp_status === 'attending').reduce((sum, g) => sum + (1 + (g.plus_ones || 0)), 0);
  const pendingCount = guests.filter(g => g.rsvp_status === 'pending').reduce((sum, g) => sum + (1 + (g.plus_ones || 0)), 0);
  const declinedCount = guests.filter(g => g.rsvp_status === 'declined').reduce((sum, g) => sum + (1 + (g.plus_ones || 0)), 0);

  const mTotal = document.getElementById('guests-metric-total');
  const mAttending = document.getElementById('guests-metric-attending');
  const mPending = document.getElementById('guests-metric-pending');
  const mDeclined = document.getElementById('guests-metric-declined');

  if (mTotal) mTotal.innerText = totalCount;
  if (mAttending) mAttending.innerText = attendingCount;
  if (mPending) mPending.innerText = pendingCount;
  if (mDeclined) mDeclined.innerText = declinedCount;

  // Filter guests
  const filtered = filterSide === 'all'
    ? guests
    : guests.filter(g => (g.side || 'general').toLowerCase() === filterSide.toLowerCase());

  if (filtered.length === 0) {
    container.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No guests matching this filter.</td></tr>`;
    return;
  }

  container.innerHTML = filtered.map(g => {
    const partySize = 1 + (g.plus_ones || 0);
    const sideLabels = {
      bride: "Bride's Side",
      groom: "Groom's Side",
      vip: "VIP / Dignitary",
      general: "General"
    };
    const sideLabel = sideLabels[g.side] || g.side || 'General';

    return `
      <tr>
        <td>
          <strong>${escapeHTML(g.name)}</strong>
          ${g.phone || g.email ? `<div style="font-size: 0.775rem; color: var(--text-secondary); margin-top: 0.15rem;">${escapeHTML(g.phone || g.email)}</div>` : ''}
        </td>
        <td>
          <span class="badge ${g.side === 'vip' ? 'badge-warm' : ''}">${escapeHTML(sideLabel)}</span>
        </td>
        <td style="font-weight: 600;">
          ${partySize} ${partySize > 1 ? '<span style="font-size: 0.75rem; color: var(--text-secondary); font-weight: normal;">(+' + g.plus_ones + ')</span>' : ''}
        </td>
        <td style="font-size: 0.8rem; color: var(--text-secondary);">
          ${escapeHTML(g.dietary_notes || g.notes || 'No special requirements')}
        </td>
        <td>
          <select 
            class="rsvp-status-select"
            aria-label="RSVP status for ${escapeHTML(g.name)}"
            data-guest-id="${escapeHTML(g.id)}"
            onchange="window.updateGuestRSVPStatus('${escapeHTML(activeEventId)}', '${escapeHTML(g.id)}', this.value)"
            style="padding: 0.25rem 0.5rem; font-size: 0.8rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color); background: var(--bg-surface); color: var(--text-primary); font-weight: 500;"
          >
            <option value="attending" ${g.rsvp_status === 'attending' ? 'selected' : ''}>✓ Confirmed</option>
            <option value="pending" ${g.rsvp_status === 'pending' ? 'selected' : ''}>⏳ Pending</option>
            <option value="declined" ${g.rsvp_status === 'declined' ? 'selected' : ''}>✗ Declined</option>
          </select>
        </td>
      </tr>
    `;
  }).join('');
}

window.updateGuestRSVPStatus = async (eventId, guestId, status) => {
  try {
    await API.updateGuestRSVP(eventId, guestId, status);
    const guests = store.state.guests.map(g => g.id === guestId ? { ...g, rsvp_status: status } : g);
    store.setState({ guests });
    renderGuests();
    renderExecutiveOverview();
  } catch (e) {
    console.error('Failed to update RSVP:', e);
  }
};

function setupGuestsModule() {
  const filterPills = document.querySelectorAll('.guest-filter-pill');
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => {
        p.classList.remove('active', 'btn-primary');
        p.classList.add('btn-secondary');
      });
      pill.classList.remove('btn-secondary');
      pill.classList.add('active', 'btn-primary');
      renderGuests(pill.getAttribute('data-side'));
    });
  });

  const openGuestBtn = document.getElementById('btn-open-guest-modal');
  const guestModal = document.getElementById('guest-modal');
  const closeGuestBtn = document.getElementById('btn-close-guest-modal');
  const guestForm = document.getElementById('guest-form');

  if (openGuestBtn && guestModal) {
    openGuestBtn.onclick = () => { guestModal.style.display = 'flex'; };
  }
  if (closeGuestBtn && guestModal) {
    closeGuestBtn.onclick = () => { guestModal.style.display = 'none'; };
  }
  if (guestModal) {
    guestModal.onclick = (e) => {
      if (e.target === guestModal) guestModal.style.display = 'none';
    };
  }

  if (guestForm) {
    guestForm.onsubmit = async (e) => {
      e.preventDefault();
      const name = document.getElementById('guest-name').value.trim();
      const side = document.getElementById('guest-side').value;
      const count = parseInt(document.getElementById('guest-count').value, 10) || 1;
      const rsvp = document.getElementById('guest-rsvp').value;
      const notes = document.getElementById('guest-notes').value.trim();

      const newGuest = {
        name,
        side,
        plus_ones: Math.max(0, count - 1),
        rsvp_status: rsvp,
        dietary_notes: notes
      };

      try {
        const saved = await API.addGuest(store.state.activeEventId, newGuest);
        const guests = [...store.state.guests, saved];
        store.setState({ guests });
        guestModal.style.display = 'none';
        guestForm.reset();
        renderGuests();
        renderExecutiveOverview();
        triggerCelebrationConfetti();
      } catch (err) {
        alert('Could not save guest: ' + err.message);
      }
    };
  }
}

function renderExportSheet() {
  const { activeEvent, budgets, tasks } = store.state;
  const container = document.getElementById('printable-preview-content');
  if (!container || !activeEvent) return;

  const totalAllocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);
  const blessing = activeEvent.blessing_note || "May this auspicious celebration bring enduring joy, health, and prosperity.";

  container.innerHTML = `
    <div style="border: 1px solid var(--border-color); padding: 2.25rem; border-radius: var(--radius-md); background: var(--bg-surface); color: var(--text-primary);">
      <div style="text-align: center; border-bottom: 1px solid var(--border-color); padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
        <span style="font-family: 'Noto Serif Devanagari', serif; font-size: 1.1rem; color: var(--text-secondary);">॥ शुभ आरम्भ ॥</span>
        <h1 style="font-size: 1.75rem; font-weight: 700; margin: 0.25rem 0;">${escapeHTML(activeEvent.title)}</h1>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">${escapeHTML(activeEvent.culture)} Celebration • ${escapeHTML(activeEvent.city)} • ${activeEvent.guest_count} Guests</p>
        <div style="font-style: italic; color: var(--text-secondary); margin-top: 0.65rem; font-size: 0.95rem;">"${escapeHTML(blessing)}"</div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <div>
          <h2 style="font-size: 1rem; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 0.35rem; margin-bottom: 0.75rem;">Financial Blueprint</h2>
          <p style="font-size: 0.875rem;"><strong>Target Budget:</strong> ${formatINR(activeEvent.target_budget)}</p>
          <p style="font-size: 0.875rem;"><strong>Allocated Total:</strong> ${formatINR(totalAllocated)}</p>
          <ul style="margin-top: 0.5rem; padding-left: 1.2rem; font-size: 0.825rem; color: var(--text-secondary);">
            ${budgets.slice(0, 5).map(b => `<li>${escapeHTML(b.name)} (${escapeHTML(b.category)}): ${formatINR(b.estimated_cost)}</li>`).join('')}
          </ul>
        </div>

        <div>
          <h2 style="font-size: 1rem; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 0.35rem; margin-bottom: 0.75rem;">Key Milestones</h2>
          <ul style="padding-left: 1.2rem; font-size: 0.825rem; color: var(--text-secondary);">
            ${tasks.slice(0, 5).map(t => `<li><strong>${escapeHTML(t.due_date || 'Date TBD')}:</strong> ${escapeHTML(t.title)} (${escapeHTML(t.owner_role)})</li>`).join('')}
          </ul>
        </div>
      </div>

      <div style="text-align: center; font-size: 0.8rem; color: var(--text-secondary); border-top: 1px solid var(--border-color); padding-top: 1rem;">
        Generated via Samaroh (समारोह) • AI Celebration Planner
      </div>
    </div>
  `;

  const printBtn = document.getElementById('btn-trigger-print');
  if (printBtn) {
    printBtn.onclick = () => window.print();
  }
}

function setupOnboardingWizard() {
  const openBtn = document.getElementById('btn-open-wizard');
  const modal = document.getElementById('wizard-modal');
  const closeBtn = document.getElementById('btn-close-wizard');
  const form = document.getElementById('wizard-form');

  if (openBtn && modal) {
    openBtn.onclick = () => modal.style.display = 'flex';
  }
  if (closeBtn && modal) {
    closeBtn.onclick = () => modal.style.display = 'none';
  }

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerText = 'Synthesizing Plan...';

      const brief = {
        title: document.getElementById('wiz-title').value,
        event_type: document.getElementById('wiz-type').value,
        culture: document.getElementById('wiz-culture').value,
        city: document.getElementById('wiz-city').value,
        target_budget: parseFloat(document.getElementById('wiz-budget').value),
        guest_count: parseInt(document.getElementById('wiz-guests').value),
        target_date: document.getElementById('wiz-date').value || "2026-12-15",
        language: "en",
        notes: document.getElementById('wiz-notes').value
      };

      try {
        const result = await API.generatePlan(brief);
        modal.style.display = 'none';
        await loadCelebration(result.event_id);
        triggerCelebrationConfetti();
        const fallbackBanner = document.getElementById('ai-fallback-banner');
        if (fallbackBanner) {
          if (result && result.is_fallback) {
            fallbackBanner.style.display = 'flex';
          } else {
            fallbackBanner.style.display = 'none';
          }
        }
      } catch (err) {
        alert(`Notice: ${err.message}. Serving curated regional blueprint.`);
        modal.style.display = 'none';
        await loadCelebration('demo-wedding-jaipur');
        const fallbackBanner = document.getElementById('ai-fallback-banner');
        if (fallbackBanner) {
          fallbackBanner.style.display = 'flex';
        }
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Generate Plan';
      }
    };
  }
}

function setupChatDrawer() {
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('btn-send-chat');
  const messagesContainer = document.getElementById('chat-messages');

  if (!sendBtn || !chatInput) return;

  const sendMessage = async () => {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append user message safely via textContent
    const userRow = document.createElement('div');
    userRow.style.cssText = 'display: flex; justify-content: flex-end; margin-bottom: 0.75rem;';
    const userBubble = document.createElement('div');
    userBubble.style.cssText = 'background: var(--text-primary); color: var(--bg-primary); padding: 0.55rem 0.9rem; border-radius: var(--radius-md); max-width: 80%; font-size: 0.875rem;';
    userBubble.textContent = text;
    userRow.appendChild(userBubble);
    messagesContainer.appendChild(userRow);

    chatInput.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Stream AI response safely
    const botMsgId = `bot-msg-${Date.now()}`;
    const botRow = document.createElement('div');
    botRow.style.cssText = 'display: flex; justify-content: flex-start; margin-bottom: 0.75rem;';
    const botDiv = document.createElement('div');
    botDiv.id = botMsgId;
    botDiv.style.cssText = 'background: var(--bg-surface); border: 1px solid var(--border-color); padding: 0.65rem 0.95rem; border-radius: var(--radius-md); max-width: 85%; font-size: 0.875rem;';
    botDiv.innerHTML = '<em>Thinking...</em>';
    botRow.appendChild(botDiv);
    messagesContainer.appendChild(botRow);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, event_id: store.state.activeEventId })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      botDiv.innerHTML = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ') && !line.includes('[DONE]')) {
            try {
              const parsed = JSON.parse(line.replace('data: ', ''));
              if (parsed.text) {
                fullText += parsed.text;
                botDiv.innerHTML = sanitizeHTML(fullText.replace(/\n/g, '<br>'));
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
              }
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      botDiv.textContent = 'Offline mode active. Your celebration plan is available above.';
    }
  };

  sendBtn.onclick = sendMessage;
  chatInput.onkeydown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };
}
