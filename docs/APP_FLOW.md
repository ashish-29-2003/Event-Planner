# End-to-End User & System Application Flows - Utsav (उत्सव)

**Document Version:** 1.0.0-PROD  
**Author:** Senior UX Architect & System Engineer  
**Date:** 2026-10-23  

---

## 1. High-Level User Journey Overview

```mermaid
stateDiagram-v2
    [*] --> LandingPage: User visits utsav-ai.netlify.app or localhost:8000
    LandingPage --> AuthModal: Clicks "Begin Planning" or "Explore Demo"
    
    state AuthChoice {
        [*] --> Choice
        Choice --> GoogleAuth: Sign in with Google
        Choice --> GuestDemo: Instant Guest / Demo Mode
    }
    
    AuthModal --> AuthChoice
    GoogleAuth --> Dashboard: Authenticated Session
    GuestDemo --> Dashboard: Ephemeral Demo Session

    state Dashboard {
        [*] --> CelebrationList
        CelebrationList --> EventWorkspace: Select Existing Event
        CelebrationList --> NewEventWizard: Click "Create New Celebration"
    }

    NewEventWizard --> AISynthesis: Submit Celebration Brief
    AISynthesis --> EventWorkspace: Master Plan Generated (Python API)

    state EventWorkspace {
        [*] --> Overview
        Overview --> AIPlanner: Conversational Assistant (SSE)
        Overview --> BudgetPlanner: Financials & Re-balancing
        Overview --> TimelineChecklist: Countdown & .ics Export
        Overview --> VendorChecklist: Quotes & Shortlisting
        Overview --> PersonalizedIdeas: Cultural Hub
        Overview --> GuestRSVP: Guest Counts & Diet
        Overview --> MuhuratHelper: Auspicious Guidance
        Overview --> ExportShare: PDF / Print Summary
    }

    EventWorkspace --> [*]
```

---

## 2. Detailed Sub-System Flowcharts

### 2.1 First-Time User & Authentication Flow
```mermaid
flowchart TD
    Start([User arrives on Landing Page]) --> ReadHero[Reads cultural tagline & features]
    ReadHero --> CTA{User clicks CTA}
    
    CTA -->|Try Instant Demo| DemoMode[Initialize Demo Store with 3 Pre-seeded Celebrations]
    CTA -->|Sign In / Sign Up| AuthDialog[Open Auth Dialog]
    
    AuthDialog --> AuthProvider{Provider Selection}
    AuthProvider -->|Google OAuth| GooglePopup[Google Account Sign-In]
    AuthProvider -->|Guest Session| AnonAuth[Generate Guest Session Token]
    
    GooglePopup --> SyncUser[Sync User Profile to Backend DB]
    AnonAuth --> TempUser[Generate Ephemeral User Session]
    
    DemoMode --> WorkspaceJaipur[Open Jaipur Royal Wedding Demo]
    SyncUser --> CheckEvents{Has existing celebrations?}
    TempUser --> CheckEvents
    
    CheckEvents -->|Yes| DashboardView[Show My Celebrations Dashboard]
    CheckEvents -->|No| LaunchWizard[Launch Onboarding Wizard]
```

---

### 2.2 Event Creation & AI Master Plan Generation Flow
```mermaid
sequenceDiagram
    autonumber
    actor Host as Event Host
    participant UI as Onboarding Wizard
    participant Store as Reactive Client Store
    participant API as FastAPI /api/ai/plan
    participant Gemini as Google Gemini 1.5 Flash (Python)
    participant DB as Backend Storage

    Host->>UI: Step 1: Select Event Type (Wedding / Birthday / Community)
    Host->>UI: Step 2: Enter Celebration Title & Cultural Tradition
    Host->>UI: Step 3: Set City, Target Date, Budget & Guest Count
    Host->>UI: Step 4: Click "Generate My Celebration Plan"
    UI->>Store: Set isSynthesizing = true (Diya Flame Loader)
    UI->>API: POST /api/ai/plan with Form Brief
    
    API->>Gemini: generate_content(system_prompt + brief, response_schema)
    
    alt Gemini Returns Valid Plan
        Gemini-->>API: Valid EventPlan JSON
        API->>DB: Persist Event, Budget, Tasks, Vendors, Ideas
        API-->>UI: 200 OK (EventPlan)
        UI->>Store: Set activeEvent & update state
        UI->>Host: Transition to Event Workspace with Celebratory Confetti!
    else Gemini 429 Quota Exhausted or Timeout
        API->>API: Catch error & load deterministic regional seed
        API->>DB: Persist Fallback Plan
        API-->>UI: 200 OK (Fallback Plan + banner flag)
        UI->>Store: Display "Serving Cached Blueprint" Notification
        UI->>Host: Transition to Event Workspace seamlessly
    end
```

---

### 2.3 Budget Management & AI Re-Balancing Flow
```mermaid
flowchart TD
    BudgetOpen([Open Budget Matrix]) --> ViewTotals[Display: Master Budget vs Allocated vs Paid]
    ViewTotals --> UserModifies{User Action}
    
    UserModifies -->|Edit Line Item Cost| EditCost[Update actual or estimated amount]
    UserModifies -->|Mark Advance Paid| MarkPaid[Update advance paid & payment status]
    UserModifies -->|Add Custom Expense| AddItem[Append new expense to category]
    
    EditCost --> Recalculate[Recalculate Category Sum & Health Indicator]
    MarkPaid --> Recalculate
    AddItem --> Recalculate
    
    Recalculate --> CheckThreshold{Is Allocated > Target Budget?}
    CheckThreshold -->|No: In Budget| NormalBadge[Display Green/Gold Health Badge]
    CheckThreshold -->|Yes: Over Budget| AlertBanner[Display Amber/Vermilion Warning Banner]
    
    AlertBanner --> ClickRebalance{User clicks 'AI Re-Balance'}
    ClickRebalance --> CallRebalanceAPI[POST /api/ai/rebalance-budget]
    CallRebalanceAPI --> GeminiCalc[Gemini adjusts flexible categories via Python]
    GeminiCalc --> ShowPreviewModal[Show Proposed Redistribution & Rationale]
    
    ShowPreviewModal --> ConfirmChoice{User Accepts?}
    ConfirmChoice -->|Yes| ApplyBudget[Apply New Budget Items to State & Database]
    ConfirmChoice -->|No| DiscardBudget[Keep Current Values]
```

---

### 2.4 Timeline Management & Google Calendar Export Flow
```mermaid
flowchart TD
    OpenTimeline([Open Timeline View]) --> RenderPhases[Render 5 Phase Accordions with Due Dates]
    RenderPhases --> Action{User Interaction}
    
    Action -->|Toggle Task Complete| Checkbox[Check Task Box]
    Checkbox --> TriggerConfetti[Fire Golden Confetti Particle Burst]
    TriggerConfetti --> UpdateDB[Update task status = 'Done']
    
    Action -->|Filter by Owner/Phase| Filter[Filter tasks by Host / Caterer / Decorator]
    
    Action -->|Export to Calendar| CalendarCTA{Export Selection}
    CalendarCTA -->|Download .ics| BuildICS[Client / Python generates RFC-5545 .ics file]
    BuildICS --> SaveFile[Trigger browser file download: utsav-timeline.ics]
    
    CalendarCTA -->|Add to Google Calendar| GCalLink[Open Google Calendar URL for single milestone]
    GCalLink --> OpenBrowserTab[Opens calendar.google.com in new tab with pre-filled details]
```

---

### 2.5 Vendor Discovery & Shortlisting Flow
```mermaid
flowchart TD
    OpenVendors([Open Vendor Checklist]) --> SelectCat[Filter by Category: Caterer, Decor, Photo, etc.]
    SelectCat --> DisplayVendors[Display Vendor Cards with Scope & Quote Tiers]
    
    DisplayVendors --> VendorAction{Vendor Action}
    
    VendorAction -->|Update Status| ChangeStatus[Set to 'Shortlisted', 'Contacted', or 'Booked']
    ChangeStatus --> UpdateVendorDB[Sync to vendor collection]
    
    VendorAction -->|Edit Quote Amount| SetQuote[Enter Vendor Quote & Payment Milestones]
    SetQuote --> LinkToBudget[Optionally link quote directly to Budget item]
    
    VendorAction -->|Discover Local Vendors| CheckMapsKey{Google Maps API key available?}
    CheckMapsKey -->|Yes| QueryPlaces[Query Google Places API for event city]
    CheckMapsKey -->|No| CuratedList[Display Curated Regional Vendor Profiles with Estimates]
```

---

### 2.6 Export, Share & Blessing Note Flow
```mermaid
flowchart TD
    OpenExport([Open Export Sheet]) --> PersonalizeNote[User writes personal blessing or family dedication note]
    PersonalizeNote --> PreviewSheet[Live Preview of Printable Celebration Document]
    PreviewSheet --> PrintCTA{User selects format}
    
    PrintCTA -->|Print / Save PDF| BrowserPrint[Trigger window.print with optimized @media print CSS]
    BrowserPrint --> CleanPDF[Generates clean, high-contrast, page-break-safe PDF]
    
    PrintCTA -->|Copy Share Link| GenerateLink[Generate read-only shareable URL]
    GenerateLink --> Clipboard[Copy to system clipboard with success toast]
```

---

### 2.7 Error Resilience & Graceful Offline Path
```mermaid
flowchart TD
    AppRequest([User Triggers Action]) --> NetworkCheck{Is network online?}
    
    NetworkCheck -->|Offline| OfflineMode[Enable Offline Mode: Read from Local Cache]
    OfflineMode --> OfflineToast[Show 'Offline - Edits saved locally' toast]
    
    NetworkCheck -->|Online| APICall[Dispatch FastAPI Request]
    APICall --> APIResult{Response Status}
    
    APIResult -->|200 OK| RenderResult[Render Fresh Data]
    APIResult -->|429 Rate Limit| QuotaStrategy[Serve Fallback Blueprint & notify user]
    APIResult -->|500 Server Error| ErrorBoundary[Catch error: Offer Retry & Cached State]
```
