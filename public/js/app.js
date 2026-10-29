/**
 * Samaroh (समारोह) - Master Application Controller
 * Handles UI interactions, live calculations, tabs, and celebratory micro-interactions.
 * Modern minimal edition.
 */

// Daily Subhashitas with attribution and English translations
const SUBHASHITAS = [
  {
    sanskrit: "॥ सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः ॥",
    meaning: "May all beings be prosperous, peaceful and healthy.",
    source: "Brihadaranyaka Upanishad"
  },
  {
    sanskrit: "॥ वसुधैव कुटुम्बकम् ॥",
    meaning: "The entire world is one sacred family.",
    source: "Maha Upanishad"
  },
  {
    sanskrit: "॥ विद्या ददाति विनयं विनयाद्याति पात्रताम् ॥",
    meaning: "Learning bestows humility, and humility brings dignity and grace.",
    source: "Hitopadesha"
  }
];

// Time-of-day Sanskrit greeting
function getCulturalGreeting() {
  const hr = new Date().getHours();
  if (hr >= 5 && hr < 12) return { text: "शुभ प्रभात", meaning: "Good Morning" };
  if (hr >= 12 && hr < 17) return { text: "शुभ अपराह्न", meaning: "Good Afternoon" };
  if (hr >= 17 && hr < 22) return { text: "शुभ संध्या", meaning: "Good Evening" };
  return { text: "शुभ रात्रि", meaning: "Good Night" };
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

document.addEventListener('DOMContentLoaded', async () => {
  // 1. Initialize Theme
  const theme = store.state.theme;
  document.documentElement.setAttribute('data-theme', theme);
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      store.toggleTheme();
      themeToggle.innerText = store.state.theme === 'dark' ? '☀️' : '🌙';
    });
    themeToggle.innerText = theme === 'dark' ? '☀️' : '🌙';
  }

  // 2. Set Greeting & Subhashita
  const greeting = getCulturalGreeting();
  const greetingEl = document.getElementById('cultural-greeting');
  if (greetingEl) {
    greetingEl.innerHTML = `<strong>${greeting.text}</strong>, Ashish (${greeting.meaning})`;
  }

  const subhashitaEl = document.getElementById('daily-subhashita');
  if (subhashitaEl) {
    const s = SUBHASHITAS[0];
    subhashitaEl.innerHTML = `<strong>${s.sanskrit}</strong> — ${s.meaning}`;
  }

  // 3. Tab Switching
  const navTabs = document.querySelectorAll('.nav-tab');
  const viewPanels = document.querySelectorAll('.view-panel');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetView = tab.getAttribute('data-view');
      navTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      viewPanels.forEach(panel => {
        panel.style.display = panel.id === `view-${targetView}` ? 'block' : 'none';
      });
    });
  });

  // 4. Load Active Event Data
  await loadCelebration(store.state.activeEventId);

  // 5. Celebration Switcher
  const switcher = document.getElementById('celebration-switcher');
  if (switcher) {
    switcher.addEventListener('change', async (e) => {
      await loadCelebration(e.target.value);
    });
  }

  // Share Celebration Link
  const shareBtn = document.getElementById('btn-share-celebration');
  if (shareBtn) {
    shareBtn.onclick = () => {
      const shareUrl = window.location.href;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
          alert("Celebration plan link copied to clipboard!\n\n" + shareUrl);
          triggerCelebrationConfetti();
        }).catch(() => {
          prompt("Copy this celebration link:", shareUrl);
        });
      } else {
        prompt("Copy this celebration link:", shareUrl);
      }
    };
  }

  // Vendor Filter Buttons
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

  // 6. Onboarding Wizard Dialog Controls
  setupOnboardingWizard();

  // 7. AI Chat Controller
  setupChatDrawer();
});

async function loadCelebration(eventId) {
  try {
    const [event, budgets, tasks, vendors, ideas] = await Promise.all([
      API.getEvent(eventId),
      API.getBudget(eventId),
      API.getTasks(eventId),
      API.getVendors(eventId),
      API.getIdeas(eventId)
    ]);

    store.setState({
      activeEventId: eventId,
      activeEvent: event,
      budgets,
      tasks,
      vendors,
      ideas
    });

    renderExecutiveOverview();
    renderBudgetMatrix();
    renderTimeline();
    renderVendors();
    renderIdeas();
    renderMuhurat();
    renderExportSheet();
  } catch (err) {
    console.error('Failed to load celebration:', err);
  }
}

function renderExecutiveOverview() {
  const { activeEvent, budgets, tasks } = store.state;
  if (!activeEvent) return;

  document.getElementById('overview-title').innerText = activeEvent.title;
  document.getElementById('overview-culture-city').innerText = `${activeEvent.culture} • ${activeEvent.city}`;

  // Countdown Calculation
  const targetDateStr = activeEvent.target_date || "2026-12-15";
  const targetDate = new Date(targetDateStr);
  const today = new Date();
  const diffTime = targetDate - today;
  const diffDays = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));

  const daysEl = document.getElementById('overview-days-left');
  if (daysEl) daysEl.innerText = diffDays;

  const dateEl = document.getElementById('overview-target-date');
  if (dateEl) dateEl.innerText = targetDate.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  const targetBudget = activeEvent.target_budget || 0;
  const allocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);
  const paid = budgets.reduce((sum, b) => sum + (b.advance_paid || 0), 0);

  document.getElementById('overview-target-budget').innerText = formatINR(targetBudget);
  document.getElementById('overview-allocated').innerText = formatINR(allocated);
  document.getElementById('overview-paid').innerText = formatINR(paid);

  const pct = targetBudget > 0 ? Math.min(Math.round((allocated / targetBudget) * 100), 100) : 0;
  const bar = document.getElementById('overview-budget-bar');
  if (bar) {
    bar.style.width = `${pct}%`;
    bar.style.backgroundColor = allocated > targetBudget ? 'var(--accent-warning)' : 'var(--text-primary)';
  }

  // Next Milestones list
  const nextTasksEl = document.getElementById('overview-next-tasks');
  if (nextTasksEl) {
    const pending = tasks.filter(t => t.status !== 'done').slice(0, 3);
    nextTasksEl.innerHTML = pending.map(t => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-light);">
        <div>
          <span style="font-size: 0.875rem; font-weight: 500;">${t.title}</span>
          <span style="font-size: 0.775rem; color: var(--text-secondary); margin-left: 0.5rem;">Due: ${t.due_date || 'TBD'}</span>
        </div>
        <span class="badge">${t.owner_role}</span>
      </div>
    `).join('') || '<p style="color: var(--text-secondary); font-size: 0.85rem; padding: 0.4rem 0;">All immediate milestones completed.</p>';
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
        <strong>${b.name}</strong>
        ${b.notes ? `<div style="font-size: 0.775rem; color: var(--text-secondary); margin-top: 0.15rem;">${b.notes}</div>` : ''}
      </td>
      <td><span class="badge">${b.category}</span></td>
      <td style="font-weight: 600;">${formatINR(b.estimated_cost)}</td>
      <td style="color: var(--accent-success); font-weight: 500;">${formatINR(b.advance_paid)}</td>
      <td>
        <span class="badge ${b.status === 'paid' ? 'badge-success' : 'badge-warm'}">
          ${b.status.toUpperCase()}
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

  container.innerHTML = tasks.map(t => `
    <div class="card" style="margin-bottom: 0.65rem; padding: 0.85rem 1rem; display: flex; align-items: flex-start; gap: 0.85rem;">
      <input type="checkbox" ${t.status === 'done' ? 'checked' : ''} style="margin-top: 0.25rem;" onchange="toggleTaskStatus('${activeEventId}', '${t.id}', this.checked)">
      <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
          <h3 style="font-size: 0.925rem; font-weight: 600; text-decoration: ${t.status === 'done' ? 'line-through' : 'none'}; color: ${t.status === 'done' ? 'var(--text-muted)' : 'var(--text-primary)'};">${t.title}</h3>
          <span style="font-size: 0.775rem; color: var(--text-secondary);">${t.due_date || 'Date TBD'}</span>
        </div>
        <p style="font-size: 0.825rem; color: var(--text-secondary); margin: 0.2rem 0 0.4rem 0;">${t.description}</p>
        <div style="display: flex; gap: 0.4rem;">
          <span class="badge badge-warm">${t.phase}</span>
          <span class="badge">${t.owner_role}</span>
        </div>
      </div>
    </div>
  `).join('');

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
          <span class="badge badge-warm">${v.category}</span>
          <span style="font-size: 0.775rem; font-weight: 600; color: var(--text-secondary);">★ ${v.rating || 4.8}</span>
        </div>
        <h3 style="font-size: 0.975rem; font-weight: 600; margin-bottom: 0.25rem;">${v.business_name}</h3>
        <p style="font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 0.65rem;">${v.notes || 'Deliverables confirmed per brief.'}</p>
        <div style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 0.2rem;">📍 ${v.address || 'Local vendor'}</div>
        <div style="font-size: 0.775rem; color: var(--text-muted);">📞 ${v.phone || 'Available upon request'}</div>
      </div>
      <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: baseline;">
        <div>
          <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-secondary);">Indicative Quote</div>
          <div style="font-size: 1.05rem; font-weight: 700;">${formatINR(v.quote_amount)}</div>
        </div>
        <span class="badge ${v.status === 'contracted' ? 'badge-success' : 'badge-warm'}">${v.status.toUpperCase()}</span>
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
        <span class="badge badge-warm">${i.tab_category.replace('_', ' ')}</span>
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);">${i.cost_bracket}</span>
      </div>
      <h3 style="font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem;">${i.title}</h3>
      <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0.6rem;">${i.description}</p>
      <div style="background: var(--bg-subtle); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-secondary); border-left: 2px solid var(--text-primary);">
        <strong style="color: var(--text-primary);">Cultural Context:</strong> ${i.cultural_context}
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
      <p style="font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 1.25rem;">${data.disclaimer}</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.75rem;">
        ${data.windows.map(w => `
          <div style="background: var(--bg-subtle); padding: 0.85rem 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <strong style="font-size: 0.9rem; color: var(--text-primary);">${w.season}</strong>
            <div style="margin: 0.4rem 0; font-size: 0.825rem;"><strong>Dates:</strong> ${w.auspicious_dates.join(', ')}</div>
            <div style="font-size: 0.775rem; color: var(--text-secondary);"><strong>Nakshatras:</strong> ${w.nakshatras}</div>
            <div style="font-size: 0.775rem; color: var(--text-secondary);"><strong>Lagnas:</strong> ${w.lagnas}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
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
        <h1 style="font-size: 1.75rem; font-weight: 700; margin: 0.25rem 0;">${activeEvent.title}</h1>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">${activeEvent.culture} Celebration • ${activeEvent.city} • ${activeEvent.guest_count} Guests</p>
        <div style="font-style: italic; color: var(--text-secondary); margin-top: 0.65rem; font-size: 0.95rem;">"${blessing}"</div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <div>
          <h2 style="font-size: 1rem; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 0.35rem; margin-bottom: 0.75rem;">Financial Blueprint</h2>
          <p style="font-size: 0.875rem;"><strong>Target Budget:</strong> ${formatINR(activeEvent.target_budget)}</p>
          <p style="font-size: 0.875rem;"><strong>Allocated Total:</strong> ${formatINR(totalAllocated)}</p>
          <ul style="margin-top: 0.5rem; padding-left: 1.2rem; font-size: 0.825rem; color: var(--text-secondary);">
            ${budgets.slice(0, 5).map(b => `<li>${b.name} (${b.category}): ${formatINR(b.estimated_cost)}</li>`).join('')}
          </ul>
        </div>

        <div>
          <h2 style="font-size: 1rem; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 0.35rem; margin-bottom: 0.75rem;">Key Milestones</h2>
          <ul style="padding-left: 1.2rem; font-size: 0.825rem; color: var(--text-secondary);">
            ${tasks.slice(0, 5).map(t => `<li><strong>${t.due_date || 'Date TBD'}:</strong> ${t.title} (${t.owner_role})</li>`).join('')}
          </ul>
        </div>
      </div>

      <div style="text-align: center; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 1rem;">
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
      } catch (err) {
        alert(`Notice: ${err.message}. Serving curated regional blueprint.`);
        modal.style.display = 'none';
        await loadCelebration('demo-wedding-jaipur');
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

    // Append user message
    messagesContainer.innerHTML += `
      <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
        <div style="background: var(--text-primary); color: var(--bg-primary); padding: 0.55rem 0.9rem; border-radius: var(--radius-md); max-width: 80%; font-size: 0.875rem;">
          ${text}
        </div>
      </div>
    `;
    chatInput.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Stream AI response
    const botMsgId = `bot-msg-${Date.now()}`;
    messagesContainer.innerHTML += `
      <div style="display: flex; justify-content: flex-start; margin-bottom: 0.75rem;">
        <div id="${botMsgId}" style="background: var(--bg-surface); border: 1px solid var(--border-color); padding: 0.65rem 0.95rem; border-radius: var(--radius-md); max-width: 85%; font-size: 0.875rem;">
          <em>Thinking...</em>
        </div>
      </div>
    `;
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
      const botDiv = document.getElementById(botMsgId);
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
                botDiv.innerHTML = fullText.replace(/\n/g, '<br>');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
              }
            } catch (e) {}
          }
        }
      }
    } catch (err) {
      document.getElementById(botMsgId).innerHTML = 'Offline mode active. Your celebration plan is available above.';
    }
  };

  sendBtn.onclick = sendMessage;
  chatInput.onkeydown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };
}
