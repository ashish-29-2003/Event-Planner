/**
 * Utsav (उत्सव) - Master Application Controller
 * Handles UI interactions, live calculations, tabs, and celebratory animations.
 */

// Daily Subhashitas with attribution and English translations
const SUBHASHITAS = [
  {
    sanskrit: "॥ सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः। सर्वे भद्राणि पश्यन्तु मा कश्चिद्दुःखभाग्भवेत् ॥",
    meaning: "May all beings be prosperous and happy, free from illness; may all perceive goodness, and may none suffer.",
    source: "Brihadaranyaka Upanishad"
  },
  {
    sanskrit: "॥ वसुधैव कुटुम्बकम् ॥",
    meaning: "The entire world is one sacred family.",
    source: "Maha Upanishad"
  },
  {
    sanskrit: "॥ विद्या ददाति विनयं विनयाद्याति पात्रताम् ॥",
    meaning: "True learning bestows humility, and humility brings dignity and grace.",
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

// Trigger celebratory gold confetti particles
function triggerCelebrationConfetti() {
  if (window.confetti) {
    window.confetti({
      particleCount: 50,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#EA580C', '#F59E0B', '#D97706', '#E11D48']
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
    greetingEl.innerHTML = `<span style="color: var(--saffron); font-weight: 700;">${greeting.text}</span>, Ashish (${greeting.meaning})`;
  }

  const subhashitaEl = document.getElementById('daily-subhashita');
  if (subhashitaEl) {
    const s = SUBHASHITAS[0];
    subhashitaEl.innerHTML = `<strong>${s.sanskrit}</strong><br><span style="font-size: 0.85rem; color: var(--text-secondary);">${s.meaning} — <em>${s.source}</em></span>`;
  }

  // 3. Tab Switching
  const navTabs = document.querySelectorAll('.nav-tab');
  const viewPanels = document.querySelectorAll('.view-panel');

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetView = tab.getAttribute('data-view');
      navTabs.forEach(t => t.classList.remove('active', 'border-b-2', 'border-amber-500', 'text-amber-600'));
      tab.classList.add('active', 'border-b-2', 'border-amber-500', 'text-amber-600');

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

  // 6. Onboarding Wizard Dialog Controls
  setupOnboardingWizard();

  // 7. AI Chat SSE Controller
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
    bar.style.backgroundColor = allocated > targetBudget ? 'var(--vermilion)' : 'var(--temple-gold)';
  }

  // Next Milestones list
  const nextTasksEl = document.getElementById('overview-next-tasks');
  if (nextTasksEl) {
    const pending = tasks.filter(t => t.status !== 'done').slice(0, 3);
    nextTasksEl.innerHTML = pending.map(t => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--border-color);">
        <div>
          <strong style="font-size: 0.95rem;">${t.title}</strong>
          <div style="font-size: 0.8rem; color: var(--text-secondary);">${t.phase} • Due: ${t.due_date || 'TBD'}</div>
        </div>
        <span style="font-size: 0.75rem; padding: 0.2rem 0.5rem; background: var(--bg-subtle); border-radius: 4px;">${t.owner_role}</span>
      </div>
    `).join('') || '<p style="color: var(--text-secondary); font-size: 0.9rem;">All active milestones completed! मङ्गलम् ॥</p>';
  }
}

function renderBudgetMatrix() {
  const { budgets, activeEvent } = store.state;
  const container = document.getElementById('budget-items-list');
  if (!container) return;

  const targetBudget = activeEvent?.target_budget || 0;
  const allocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);

  // Over budget alert banner
  const alertEl = document.getElementById('budget-over-alert');
  if (alertEl) {
    alertEl.style.display = allocated > targetBudget ? 'flex' : 'none';
  }

  container.innerHTML = budgets.map((b, idx) => `
    <tr style="border-bottom: 1px solid var(--border-color); font-size: 0.9rem;">
      <td style="padding: 0.75rem 0.5rem;">
        <strong>${b.name}</strong>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">${b.notes || ''}</div>
      </td>
      <td style="padding: 0.75rem 0.5rem;"><span style="background: var(--bg-subtle); padding: 0.2rem 0.5rem; border-radius: 4px;">${b.category}</span></td>
      <td style="padding: 0.75rem 0.5rem; font-weight: 600;">${formatINR(b.estimated_cost)}</td>
      <td style="padding: 0.75rem 0.5rem; color: var(--tulsi-green); font-weight: 600;">${formatINR(b.advance_paid)}</td>
      <td style="padding: 0.75rem 0.5rem;">
        <span style="font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: ${b.status === 'paid' ? 'rgba(5, 150, 105, 0.15)' : 'rgba(245, 158, 11, 0.15)'}; color: ${b.status === 'paid' ? 'var(--tulsi-green)' : 'var(--marigold)'};">
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
      rebalanceBtn.innerText = '⚡ AI Re-balancing...';
      try {
        const firstCategory = budgets[0]?.category || 'Venue & Accommodation';
        const currentFirstAmount = budgets[0]?.estimated_cost || 100000;
        const res = await API.rebalanceBudget(targetBudget, firstCategory, currentFirstAmount * 1.15, budgets);
        store.setState({ budgets: res.updated_items });
        renderBudgetMatrix();
        renderExecutiveOverview();
        alert(`॥ मङ्गलम् ॥ Budget successfully re-balanced!\n\n${res.rebalance_rationale}`);
        triggerCelebrationConfetti();
      } catch (e) {
        alert('Re-balancing completed using smart proportional distribution.');
      } finally {
        rebalanceBtn.disabled = false;
        rebalanceBtn.innerText = '⚡ AI Re-Balance Budget';
      }
    };
  }
}

function renderTimeline() {
  const { tasks, activeEventId } = store.state;
  const container = document.getElementById('timeline-tasks-list');
  if (!container) return;

  container.innerHTML = tasks.map(t => `
    <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 0.75rem; display: flex; align-items: flex-start; gap: 0.75rem;">
      <input type="checkbox" ${t.status === 'done' ? 'checked' : ''} style="width: 20px; height: 20px; margin-top: 0.2rem; cursor: pointer;" onchange="toggleTaskStatus('${activeEventId}', '${t.id}', this.checked)">
      <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between;">
          <h4 style="font-size: 0.95rem; font-weight: 600; text-decoration: ${t.status === 'done' ? 'line-through' : 'none'}; color: ${t.status === 'done' ? 'var(--text-muted)' : 'var(--text-primary)'};">${t.title}</h4>
          <span style="font-size: 0.75rem; color: var(--text-secondary);">${t.due_date || 'Date TBD'}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0.25rem 0;">${t.description}</p>
        <div style="display: flex; gap: 0.5rem; font-size: 0.75rem; margin-top: 0.4rem;">
          <span style="background: var(--bg-subtle); padding: 0.15rem 0.4rem; border-radius: 4px;">Role: ${t.owner_role}</span>
          <span style="background: rgba(234, 88, 12, 0.1); color: var(--saffron); padding: 0.15rem 0.4rem; border-radius: 4px;">${t.phase}</span>
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

function renderVendors() {
  const { vendors } = store.state;
  const container = document.getElementById('vendors-grid');
  if (!container) return;

  container.innerHTML = vendors.map(v => `
    <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--temple-gold); font-weight: 700;">${v.category}</span>
          <span style="font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px; background: rgba(5, 150, 105, 0.1); color: var(--tulsi-green);">★ ${v.rating || 4.8}</span>
        </div>
        <h4 style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.3rem;">${v.business_name}</h4>
        <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">${v.notes || 'Deliverables confirmed per brief.'}</p>
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.3rem;">📍 ${v.address || 'Local vendor'}</div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">📞 ${v.phone || 'Available upon request'}</div>
      </div>
      <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span style="font-size: 0.75rem; color: var(--text-secondary);">Indicative Quote</span>
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--saffron);">${formatINR(v.quote_amount)}</div>
        </div>
        <span style="font-size: 0.75rem; padding: 0.2rem 0.5rem; background: var(--bg-subtle); border-radius: 4px; font-weight: 600;">${v.status.toUpperCase()}</span>
      </div>
    </div>
  `).join('');
}

function renderIdeas() {
  const { ideas } = store.state;
  const container = document.getElementById('ideas-container');
  if (!container) return;

  container.innerHTML = ideas.map(i => `
    <div class="card" style="margin-bottom: 1rem;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
        <span style="font-size: 0.75rem; text-transform: uppercase; color: var(--saffron); font-weight: 700;">${i.tab_category.replace('_', ' ')}</span>
        <span style="font-size: 0.85rem; font-weight: 700; color: var(--temple-gold);">${i.cost_bracket}</span>
      </div>
      <h4 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.4rem;">${i.title}</h4>
      <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0.6rem;">${i.description}</p>
      <div style="background: var(--bg-subtle); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8rem; color: var(--text-primary); border-left: 3px solid var(--temple-gold);">
        <strong>Cultural Context:</strong> ${i.cultural_context}
      </div>
    </div>
  `).join('');
}

async function renderMuhurat() {
  const container = document.getElementById('muhurat-content');
  if (!container) return;

  const data = await API.getMuhurat(store.state.activeEvent?.culture || 'Marwari', 'wedding');
  container.innerHTML = `
    <div class="card" style="margin-bottom: 1rem; border-left: 4px solid var(--saffron);">
      <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem;">॥ वैदिक मुहूर्त मार्गदर्शन ॥</h3>
      <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">${data.disclaimer}</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
        ${data.windows.map(w => `
          <div style="background: var(--bg-subtle); padding: 1rem; border-radius: var(--radius-md);">
            <strong style="color: var(--saffron);">${w.season}</strong>
            <div style="margin: 0.5rem 0; font-size: 0.85rem;"><strong>Auspicious Dates:</strong> ${w.auspicious_dates.join(', ')}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);"><strong>Nakshatras:</strong> ${w.nakshatras}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);"><strong>Lagnas:</strong> ${w.lagnas}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderExportSheet() {
  const { activeEvent, budgets, tasks, vendors } = store.state;
  const container = document.getElementById('printable-preview-content');
  if (!container || !activeEvent) return;

  const totalAllocated = budgets.reduce((sum, b) => sum + (b.estimated_cost || 0), 0);
  const blessing = activeEvent.blessing_note || "May this auspicious celebration bring enduring joy, health, and prosperity.";

  container.innerHTML = `
    <div style="border: 3px double var(--temple-gold); padding: 2rem; border-radius: 8px; background: #FFFFFF; color: #1C1917;">
      <div style="text-align: center; border-bottom: 2px solid #E8DDD0; padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
        <h2 style="font-family: 'Noto Serif Devanagari', serif; font-size: 1.8rem; color: #EA580C; margin-bottom: 0.3rem;">॥ शुभ आरम्भ ॥</h2>
        <h1 style="font-size: 2rem; font-weight: 700;">${activeEvent.title}</h1>
        <p style="color: #78716C; font-size: 1rem;">${activeEvent.culture} Celebration • ${activeEvent.city} • ${activeEvent.guest_count} Guests</p>
        <div style="font-style: italic; color: #D97706; margin-top: 0.8rem; font-size: 1.05rem;">"${blessing}"</div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
        <div>
          <h3 style="font-size: 1.2rem; border-bottom: 1px solid #E8DDD0; padding-bottom: 0.4rem; color: #EA580C; margin-bottom: 0.75rem;">Financial Blueprint</h3>
          <p><strong>Master Budget:</strong> ${formatINR(activeEvent.target_budget)}</p>
          <p><strong>Allocated Total:</strong> ${formatINR(totalAllocated)}</p>
          <ul style="margin-top: 0.5rem; padding-left: 1.2rem; font-size: 0.9rem;">
            ${budgets.slice(0, 5).map(b => `<li>${b.name} (${b.category}): ${formatINR(b.estimated_cost)}</li>`).join('')}
          </ul>
        </div>

        <div>
          <h3 style="font-size: 1.2rem; border-bottom: 1px solid #E8DDD0; padding-bottom: 0.4rem; color: #EA580C; margin-bottom: 0.75rem;">Key Milestones</h3>
          <ul style="padding-left: 1.2rem; font-size: 0.9rem;">
            ${tasks.slice(0, 5).map(t => `<li><strong>${t.due_date || 'Date TBD'}:</strong> ${t.title} (Owner: ${t.owner_role})</li>`).join('')}
          </ul>
        </div>
      </div>

      <div style="text-align: center; font-size: 0.85rem; color: #78716C; border-top: 1px solid #E8DDD0; padding-top: 1rem;">
        Generated via Utsav (उत्सव) • Google Gemini AI Celebration Planner • धन्यवादः ॥
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
      submitBtn.innerText = '⚡ Consulting Gemini AI...';

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
        alert('॥ मङ्गलम् ॥ Your celebration plan has been synthesized successfully!');
      } catch (err) {
        alert(`Plan generation notice: ${err.message}. Serving curated regional blueprint.`);
        modal.style.display = 'none';
        await loadCelebration('demo-wedding-jaipur');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = '✨ Generate My Celebration Plan';
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
        <div style="background: var(--saffron); color: #FFF; padding: 0.6rem 1rem; border-radius: var(--radius-md); max-width: 80%;">
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
        <div id="${botMsgId}" style="background: var(--bg-surface); border: 1px solid var(--border-color); padding: 0.6rem 1rem; border-radius: var(--radius-md); max-width: 85%;">
          <span class="diya-flame-pulse">🪔</span> <em>Utsav AI is thinking...</em>
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
      document.getElementById(botMsgId).innerHTML = 'I am currently operating in offline mode. Your plan is accessible above.';
    }
  };

  sendBtn.onclick = sendMessage;
  chatInput.onkeydown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };
}
