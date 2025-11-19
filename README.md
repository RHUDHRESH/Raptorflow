# Raptorflow - Strategy Execution Platform

A modern, fashion-house inspired strategy execution platform built with React, Tailwind CSS, and Framer Motion.

## Features

### 🎯 Core Features

- **Move Management**: Track strategic moves with progress monitoring
- **Move Detail View**: Comprehensive move details with tabbed interface:
  - Daily Logging (habit tracker)
  - Weekly Review (scale/tweak/kill decisions)
  - Linked Assets
- **Strategy Wizard**: 30-minute onboarding flow to build your strategy
- **Weekly Review Ritual**: Make data-driven decisions (Scale/Tweak/Kill)
- **ICP Manager**: Define and manage Ideal Customer Profiles with AI recommendations
- **Analytics Dashboard**: Data-driven insights with actionable optimizations
- **Support & History**: Feedback loop and activity tracking

### 🎨 Design Philosophy

- **Fashion House Aesthetic**: Sophisticated, minimal, luxurious design
- **Smooth Animations**: Framer Motion powered transitions
- **Attention to Detail**: Perfect typography, spacing, and visual hierarchy
- **Modern UI**: Glass morphism, gradients, and elegant components

## Tech Stack

- **React 19** - UI framework
- **React Router DOM 7** - Routing
- **Tailwind CSS 4** - Styling
- **Framer Motion 12** - Animations
- **Lucide React** - Icons
- **Vite** - Build tool

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   └── Layout.jsx          # Main layout with sidebar navigation
├── pages/
│   ├── Dashboard.jsx       # Main dashboard
│   ├── Moves.jsx           # Moves list view
│   ├── MoveDetail.jsx      # Move detail with tabs
│   ├── Strategy.jsx        # Strategy overview
│   ├── StrategyWizard.jsx  # Strategy onboarding wizard
│   ├── Analytics.jsx       # Analytics dashboard
│   ├── WeeklyReview.jsx    # Weekly review ritual
│   ├── ICPManager.jsx      # ICP management
│   ├── Support.jsx         # Support & feedback
│   └── History.jsx         # Activity history
├── utils/
│   └── cn.js               # Class name utility
├── App.jsx                 # Main app component with routes
├── main.jsx                # Entry point
└── index.css               # Global styles
```

## Color Palette

- **Primary**: Warm neutrals (#9d7f5a - #2a2119)
- **Accent**: Warm oranges (#f1783d - #793218)
- **Neutral**: Grays (#fafafa - #171717)

## Typography

- **Display**: Playfair Display (headings)
- **Sans**: Inter (body text)
- **Mono**: JetBrains Mono (code)

## Key Pages

### Dashboard
Overview of all moves, stats, and quick actions.

### Moves
List view of all strategic moves with filtering and search.

### Move Detail
Detailed view with three tabs:
- **Daily Logging**: Track daily progress and habits
- **Weekly Review**: Make scale/tweak/kill decisions
- **Linked Assets**: Manage related documents and resources

### Strategy Wizard
Step-by-step wizard to build your strategy:
1. Business Context
2. Target Market
3. Value Proposition
4. Success Metrics

### Weekly Review
Ritual interface to review moves and make decisions based on metrics.

### ICP Manager
Manage Ideal Customer Profiles with AI-powered recommendations.

### Analytics
Data-driven insights with actionable optimization recommendations.

## Development Notes

- All components use Framer Motion for animations
- Tailwind CSS for styling with custom theme
- React Router for navigation
- Responsive design (mobile-first)

## License

MIT

