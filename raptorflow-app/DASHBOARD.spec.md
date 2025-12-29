# RaptorFlow — Dashboard Specification

This is the exact spec for the War Room dashboard.

---

## Purpose Gate

**Primary job:** Show the founder what to do next.
**Primary CTA:** "Start Move" button.
**Next screen:** Move execution flow.

---

## Layout

```
┌─────────────────────────────────────────────────────┐
│ [Sidebar 220px]  │  [Main Content, max 1000px]      │
│                  │                                   │
│  RF logo         │  Page Header                     │
│  ───────         │    Title (serif, 40px)           │
│  Dashboard ●     │    Subtitle (muted)              │
│  Foundation      │    [Primary CTA]                 │
│  Cohorts         │                                   │
│  Moves           │  ─────────────────────────────── │
│  Campaigns       │                                   │
│  Muse            │  Next Move (Hero Card)           │
│  Matrix          │    Move name (heading)           │
│  Blackbox        │    Outcome + effort              │
│  ───────         │    [Start] button                │
│  Settings        │                                   │
│                  │  ─────────────────────────────── │
│                  │                                   │
│                  │  Focus (single column list)      │
│                  │    • Positioning  status         │
│                  │    • Cohorts      status         │
│                  │    • Offer        status ●       │
│                  │    • Distribution status         │
│                  │    • Pipeline     status         │
│                  │                                   │
│                  │  ─────────────────────────────── │
│                  │                                   │
│                  │  Campaign                        │
│                  │    Week 3/12  ═══════───────     │
│                  │    Today: milestone              │
│                  │    Next: milestone               │
│                  │                                   │
└─────────────────────────────────────────────────────┘
```

---

## Blocks (Exact)

### 1. Page Header

```
Layout:       flex, space-between, align-start
Margin-bottom: 48px

Left:
  Title:      "Dashboard" (Playfair, 40px, #171717)
  Subtitle:   "This week: [goal]" (Inter, 16px, #737373)

Right:
  [Empty - no CTA here, it's in the hero card]
```

### 2. Hero Move Card

```
Layout:       Card default, full width
Padding:      32px
Margin-bottom: 48px

Content:
  Label:      "NEXT MOVE" (12px, uppercase, #A3A3A3, tracking-wide)
  Title:      Move name (20px, semibold, #171717)
  Outcome:    "→ [outcome]" (16px, #737373)
  Meta:       "3 days · Medium effort" (14px, #A3A3A3)
  CTA:        Primary button "Start" (right-aligned)
```

### 3. Focus List

```
Layout:       Single column, no card wrapper
Margin-bottom: 48px

Header:
  "Focus" (12px, uppercase, #A3A3A3, spacing 8px margin-bottom)

Items (5 max):
  Layout:     flex, space-between, padding 12px 0
  Border:     border-bottom 1px solid #E5E5E5 (last:none)

  Left:
    Dot (8px) + Name (16px, medium)
  Right:
    Status text (14px, #737373)
```

### 4. Campaign Progress

```
Layout:       No card wrapper
Margin-bottom: 48px

Header:
  Name:       Campaign name (16px, semibold)
  Progress:   "Week 3/12" (14px, #737373)

Progress bar:
  Height:     4px
  Background: #E5E5E5
  Fill:       #171717
  Radius:     2px

Milestones:
  Layout:     flex, 2 items, gap 32px

  Today:
    Label:    "TODAY" (12px, #A3A3A3)
    Text:     Milestone (14px, #171717)

  Next:
    Label:    "NEXT" (12px, #A3A3A3)
    Text:     Milestone (14px, #737373)
```

### 5. Metrics (Optional, below fold)

```
Layout:       flex, 4 items, gap 24px
Margin-bottom: 48px

Item:
  Label:      Metric name (12px, #A3A3A3, uppercase)
  Value:      Number (24px, JetBrains Mono, semibold)
  Delta:      "+8" or "−2" (14px, mono, #737373)

No colored deltas. Just gray with +/- sign.
```

---

## Typography Exact

| Element       | Font           | Size   | Weight | Color   |
| ------------- | -------------- | ------ | ------ | ------- |
| Page title    | Playfair       | 40px   | 600    | #171717 |
| Page subtitle | Inter          | 16px   | 400    | #737373 |
| Section label | Inter          | 12px   | 500    | #A3A3A3 |
| Card title    | Inter          | 20px   | 600    | #171717 |
| Body          | Inter          | 16px   | 400    | #171717 |
| Muted         | Inter          | 14px   | 400    | #737373 |
| Caption       | Inter          | 12px   | 400    | #A3A3A3 |
| Numbers       | JetBrains Mono | varies | 600    | #171717 |

---

## Spacing Exact

| Element               | Value   |
| --------------------- | ------- |
| Page padding          | 48px    |
| Section margin-bottom | 48px    |
| Card padding          | 24-32px |
| List item padding     | 12px 0  |
| Button height         | 44px    |
| Progress bar height   | 4px     |

---

## What's NOT on Dashboard

- No greeting ("Good morning")
- No avatar/profile in header
- No stats row in header
- No table layouts
- No multi-column grid
- No colored status pills
- No charts
- No blockers section (goes in Moves)
- No learnings section (goes in Blackbox)

**Above the fold: Title + Context + Next Move + Start button.**

That's it.

---

## Mobile Adaptation

```
Max-width:    100%
Page padding: 24px
Sidebar:      Collapsed to hamburger
Hero card:    Full width
Focus list:   Full width
CTA:          Full width button
```

---

## Empty State

### No active campaign

```
Title:      "No active campaign"
Body:       "Start a 90-day campaign to get your first moves."
CTA:        "Create Campaign" (primary button)
```

### No moves queued

```
Title:      "Queue is empty"
Body:       "Your next move will appear here when a campaign is active."
CTA:        "View Campaigns" (secondary button)
```
