# UI/UX Specification & Design System - Samaroh (समारोह)

**Document Version:** 1.0.0-PROD  
**Author:** Senior UX/UI Designer  
**Date:** 2026-10-23  

---

## 1. Design Direction & Cultural Philosophy

Samaroh blends high-craft digital product aesthetics (inspired by Apple, Linear, and Stripe) with the timeless warmth, sacred geometry, and celebratory richness of Indian heritage. The interface avoids caricature, kitsch, or clichéd royal tropes. Instead, it feels dignified, modern, intuitive, and deeply personal.

### 1.1 Cultural Motifs & Visual Elements
1. **Mandala Line-Art:** Low-opacity, fine-stroke vector mandalas used as subtle atmospheric watermarks on hero banners and modal backdrops (`opacity: 0.04` in light mode, `0.08` in dark mode).
2. **The Diya Flame:** Sacred diya flame icon representing illuminating wisdom. Pulses softly with golden radial halo during AI thought/generation cycles.
3. **Torana & Marigold Garlands:** Subtle ornamental horizontal divider lines inspired by mango leaves and marigold strings (*genda phool*).
4. **Kalash & Lotus Emblems:** Minimalist, geometric vector accents used to anchor success states and milestone badges.

### 1.2 Classical Sanskrit Expressions (Meaningful & Contextual)
Every Sanskrit touch is short, meaningful, grammatically verified, and always presented with an accompanying English translation:
- **Onboarding Header:** *शुभ आरम्भ* (*Shubh Aarambh* — "An auspicious beginning")
- **Product Title:** *उत्सव* (*Samaroh* — "Celebration, festival, joyous gathering")
- **Success State:** *मङ्गलम्* (*Mangalam* — "May auspiciousness prevail")
- **Welcome Greeting:** *स्वागतम्* (*Swagatam* — "A warm welcome")
- **Completion / Export:** *धन्यवादः* (*Dhanyavadah* — "With gratitude")
- **Daily Subhashita (Classical Upanishadic Verse):**
  > *"सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः। सर्वे भद्राणि पश्यन्तु मा कश्चिद्दुःखभाग्भवेत्॥"*  
  > *"May all sentient beings be prosperous and happy, free from illness; may all perceive goodness, and may none suffer."* — Brihadaranyaka Upanishad

---

## 2. Design Tokens & Palette

### 2.1 Color Tokens
```css
:root {
  /* Base Light Theme */
  --bg-primary: #FAF7F2;      /* Warm Sacred Ivory */
  --bg-surface: #FFFFFF;      /* Clean White Card */
  --bg-subtle: #F3ECE2;       /* Sandalwood Tint */
  --border-subtle: #E8DDD0;   /* Warm Border */
  --text-primary: #1C1917;    /* Deep Charcoal */
  --text-secondary: #78716C;  /* Muted Warm Stone */

  /* Cultural Celebratory Accents */
  --accent-saffron: #EA580C;  /* Kesari Saffron (Action primary) */
  --accent-marigold: #F59E0B; /* Genda Amber (Attention & joy) */
  --accent-vermilion: #E11D48;/* Sindoor Red (Weddings & sacred milestones) */
  --accent-gold: #D97706;     /* Royal Temple Gold (Premium borders) */
  --accent-peacock: #0284C7;  /* Mayura Blue (Community & stability) */
  --accent-emerald: #059669;  /* Tulsi Green (Success & in-budget) */

  /* Radii & Shadows */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  --shadow-card: 0 4px 20px -2px rgba(28, 25, 23, 0.05);
  --shadow-glow: 0 0 24px -4px rgba(245, 158, 11, 0.35);
}

[data-theme="dark"] {
  /* Base Dark Theme (Twilight Indigo) */
  --bg-primary: #0B0F19;      /* Midnight Twilight */
  --bg-surface: #131B2E;      /* Deep Indigo Card */
  --bg-subtle: #1C2742;       /* Subtle Night Tint */
  --border-subtle: #253356;   /* Cool Indigo Border */
  --text-primary: #F8FAFC;    /* Pristine Crisp White */
  --text-secondary: #94A3B8;  /* Soft Slate */

  /* Adjusted Dark Accents */
  --accent-saffron: #FB923C;
  --accent-marigold: #FBBF24;
  --accent-vermilion: #FB7185;
  --accent-gold: #F59E0B;
  --accent-peacock: #38BDF8;
  --accent-emerald: #34D399;
  --shadow-card: 0 4px 24px -2px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 30px -2px rgba(251, 191, 36, 0.25);
}
```

### 2.2 Typography Tokens
- **Display & Section Headings:** `'Noto Serif Devanagari', 'Playfair Display', Georgia, serif`
  - Devanagari line-height enforced at `1.6` to guarantee matras (vowel signs) never clip.
- **Body & Controls:** `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
  - Font weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold).

---

## 3. Screen-by-Screen UX & Wireframes

### 3.1 Screen 1: Landing Page & Cultural Hero
```
+-----------------------------------------------------------------------------------+
|  [Logo: SAMAROH समारोह]            [शुभ संध्या, Ashish]   [☀️/🌙] [Demo Mode] [Sign In]|
+-----------------------------------------------------------------------------------+
|                                                                                   |
|         ॥ शुभ आरम्भ: every celebration begins well ॥                              |
|                                                                                   |
|    Create culturally immaculate, financially realistic plans for weddings,        |
|      birthdays, and community festivals with the power of Google Gemini.          |
|                                                                                   |
|           [ ✨ Plan My Celebration ]     [ 🏛️ Explore Jaipur Royal Wedding ]       |
|                                                                                   |
|-----------------------------------------------------------------------------------|
|  [ Rotating Subhashita of the Day: सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः... ]     |
|-----------------------------------------------------------------------------------|
|                                                                                   |
|   +-------------------+   +--------------------+   +---------------------------+  |
|   | 💒 Weddings       |   | 🎂 Birthdays       |   | 🏮 Community Melas        |  |
|   | Multi-day rituals,|   | Themed games, eco  |   | RWA permits, food stalls, |  |
|   | Mehendi, Sangeet  |   | gifts, run of show |   | stage sound & security    |  |
|   +-------------------+   +--------------------+   +---------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 3.2 Screen 2: 4-Step Celebration Onboarding Wizard
- **Step 1 (Celebration Type):** Cards with visual icons (Wedding, Birthday, Community Event, Festival/Puja, Other).
- **Step 2 (Cultural Anchor):** Title (e.g., "Riya & Kabir's Vivaha"), Regional Heritage (Marwari, Punjabi, South Indian Tamil, Bengali, Secular), Host City.
- **Step 3 (Parameters):** Date (or "Find Auspicious Muhurat"), Target Budget (₹ Lakh/Crore selector), Guest Count (slider + numeric input).
- **Step 4 (GenAI Synthesis Trigger):** Diya Flame animation with progress indicators ("Formulating auspicious schedule...", "Balancing vendor allocations...", "Curating regional delicacies...").

### 3.3 Screen 3: Executive Celebration Workspace
```
+-----------------------------------------------------------------------------------+
| [Switch Event: Riya's Vivaha v]  [Budget: ₹35L]  [Guests: 350]   [Export PDF]     |
+-----------------------------------------------------------------------------------+
| [Overview] [AI Assistant] [Budget Matrix] [Timeline] [Vendors] [Ideas] [Muhurat]  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +-----------------------------+  +--------------------------------------------+  |
|  |       COUNTDOWN RING        |  |            LIVE FINANCIAL HEALTH           |  |
|  |             52              |  |  Target Budget: ₹35,00,000                 |  |
|  |          DAYS TO GO         |  |  Allocated:     ₹33,80,000 [█████████░] 96% |  |
|  |     Phase: Core Bookings    |  |  Advance Paid:  ₹12,40,000                 |  |
|  |  [ Export Google Calendar ] |  |  [ ⚡ AI Re-Balance Budget ]               |  |
|  +-----------------------------+  +--------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | ACTIVE MILESTONES (Next 7 Days)                                             |  |
|  | [x] Finalize Palace Venue contract (Jaipur)              Owner: Host        |  |
|  | [ ] Sample Royal Rajasthani catering menu                Owner: Caterer     |  |
|  | [ ] Confirm Bridal Mehendi artist deposit                Owner: Sister      |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 4. Personal Touch & Dynamic Tailoring

1. **Time-of-Day Cultural Greeting:**
   - Morning (05:00–12:00): *शुभ प्रभात* (*Shubh Prabhat*, Good Morning)
   - Afternoon (12:00–17:00): *शुभ अपराह्न* (*Shubh Aprahna*, Good Afternoon)
   - Evening (17:00–22:00): *शुभ संध्या* (*Shubh Sandhya*, Good Evening)
   - Night (22:00–05:00): *शुभ रात्रि* (*Shubh Ratri*, Good Night)
2. **Event-Themed Visual Anchors:**
   - Wedding: Vermilion (`#E11D48`) and Royal Gold accents; marigold garland divider.
   - Birthday: Marigold (`#F59E0B`) and Confetti bursts; playful badge styling.
   - Community Mela: Peacock Indigo (`#0284C7`) and warm Diya glow.
3. **Personal Blessing Note:**
   - Users can write a custom blessing or family dedication note (e.g., *"With love and blessings from Nanaji & Nanima for a joyful start"*).
   - This blessing appears prominently at the top of all printed and exported celebration sheets.

---

## 5. Animation & Motion Specifications

- **Easing Curves:** CSS `cubic-bezier(0.16, 1, 0.3, 1)` (mimics Apple iOS spring physics).
- **Diya Pulse Loader:** Golden atmospheric glow pulsing between `0.4` and `0.9` opacity over 1.8 seconds.
- **Budget Ticker:** Number values animate smoothly over 600ms when modified or re-balanced.
- **Task Completion Sparkle:** Checking off a milestone triggers a 40-particle golden confetti burst (`canvas-confetti`).
- **Reduced Motion Compliance:**
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```

---

## 6. Component States & Empty/Error Designs

| Component | Normal State | Hover State | Active / Focused | Disabled State |
|---|---|---|---|---|
| **Primary Button** | Saffron gradient fill, white text, 8px radius | Scale 1.02, subtle golden glow | Scale 0.98, visible focus ring | Opacity 0.45, cursor not-allowed |
| **Budget Input** | White/Dark surface, light border | Border amber-400 | Border saffron-500, ring 2px | Opacity 0.5 |
| **Task Checkbox** | Subtle border, rounded square | Border gold-400 | Ink-fill gold with white check | Grayed out |

- **Empty State Design:** Displays a soft mandala illustration with warm text: *"No expenses recorded yet. Click 'Add Expense' or let our AI Planner suggest standard allocations for your guest count."*
- **Error State Design:** Displays a soft kalash emblem with clear recovery steps: *"Network temporarily unreachable. Your offline edits are securely saved locally. [ Retry Sync ]"*
