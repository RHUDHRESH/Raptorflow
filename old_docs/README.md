# 🦅 RaptorFlow Strategic Marketing System

> **Transform scattered marketing activities into coordinated, data-driven campaigns**

A comprehensive strategic marketing command center that unifies positioning, campaigns, cohorts, and creative execution with AI-powered insights.

---

## ✨ Features

### 🎯 Strategic Foundation
- **Positioning Workshop** - 6-step wizard for positioning statements
- **Message Architecture** - Proof points and messaging framework
- **AI Generation** - Auto-generate messaging from positioning

### 👥 Cohort Intelligence (6 Dimensions)
- **Buying Triggers** - What drives urgency
- **Decision Criteria** - What matters most (with weights)
- **Objection Map** - Concerns and responses
- **Attention Windows** - Channel preferences and timing
- **Journey Distribution** - Awareness stage breakdown
- **Competitive Frame** - Alternatives and decision-making unit

### 📊 Campaign Orchestration
- **5-Step Wizard** - Strategic foundation → objective → cohorts → channels → launch
- **Health Tracking** - Real-time health scores (0-100)
- **Pacing Indicators** - Ahead/on track/behind/at risk
- **Move Recommendations** - AI-generated tactical moves
- **Progress Monitoring** - Metrics, budget, and move completion

### 🎨 Creative Automation
- **Auto-Generated Briefs** - From moves with full strategic context
- **Single-Minded Proposition** - The ONE thing to communicate
- **Tone Determination** - Based on journey stage and intensity
- **Mandatories & No-Gos** - Guardrails for asset creation
- **Export to Markdown** - Shareable brief format

### 🧠 Strategic Insights
- **Campaign Analysis** - Pacing, channels, moves, cohorts
- **Cohort Validation** - Completeness, freshness, journey health
- **Positioning Effectiveness** - Success rate tracking
- **Workspace Analytics** - Aggregated metrics
- **Feedback Loops** - Act/dismiss for continuous improvement

---

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and npm
- **Supabase account** - Sign up at [supabase.com](https://supabase.com)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/raptorflow.git
cd raptorflow

# Install dependencies
npm install
```

### Environment Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env.local
   ```

2. **Configure Supabase** (Required):
   - Go to your [Supabase Dashboard](https://app.supabase.com)
   - Create a new project (or use existing)
   - Navigate to **Settings** → **API**
   - Copy your **Project URL** and **anon/public key**
   - Update `.env.local`:
     ```bash
     VITE_SUPABASE_URL=https://your-project.supabase.co
     VITE_SUPABASE_ANON_KEY=your_actual_anon_key_here
     ```

3. **Run database migrations** (see Database Setup below)

### Start Development Server

```bash
npm run dev
```

Navigate to `http://localhost:5173`

### Database Setup

Run these migrations in your Supabase SQL Editor (in order):

1. **Workspace Tables** - Creates `workspaces`, `workspace_members`, `profiles` tables
2. **Positioning Tables** - Creates `positioning_profiles` table
3. **Enable RLS** - Sets up Row Level Security policies

See `supabase/migrations/` folder for SQL scripts.


---

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **[Final Summary](FINAL_SUMMARY.md)** - Complete project overview
- **[Walkthrough](walkthrough.md)** - Detailed examples
- **[Testing Guide](PHASE_8_COMPLETE.md)** - End-to-end testing

---

## 🏗️ Architecture

### Frontend Stack
- **React 19** - UI framework with concurrent features
- **Vite** - Fast build tool and dev server
- **React Router 7** - Client-side routing
- **Tailwind CSS** - Utility-first styling with custom design system
- **Framer Motion** - Smooth animations and transitions
- **Zod** - Schema validation
- **Supabase JS Client** - Database and auth integration

### Backend Stack
- **Python FastAPI** - REST API framework
- **Supabase** - PostgreSQL database with real-time features
- **Vertex AI** - AI-powered insights and generation

### Frontend Architecture Layers

#### 1. Auth Layer (`src/context/AuthContext.tsx`)
- Manages authentication state: `loading`, `authenticated`, `unauthenticated`
- Handles Supabase auth flows: email/password, OAuth
- User session management and persistence
- Profile and subscription data

#### 2. Workspace Layer (`src/context/WorkspaceContext.tsx`)
- Multi-workspace support for users
- Workspace selection and persistence (localStorage)
- Row Level Security (RLS) scoped data access
- Workspace member roles: owner, admin, member, viewer

#### 3. Protected Routes (`src/components/ProtectedRoute.tsx`)
- Guards authenticated pages
- Redirects to `/auth` when unauthenticated
- Shows loading states during auth check

#### 4. App Shell
- Sidebar navigation
- Topbar with workspace selector and user menu
- Consistent layout across workspace pages

### Database Schema
- **8 Core Tables** - workspaces, profiles, positioning, campaigns, etc.
- **JSONB Columns** - Flexible strategic attributes
- **RLS Policies** - Workspace-scoped security
- **Triggers** - Auto-create profiles, auto-assign workspace owners


---

## 🎯 Key Workflows

### 1. Create Positioning → Campaign → Assets

```
Positioning Workshop
    ↓
Message Architecture
    ↓
Campaign Builder
    ↓
Move Recommendations
    ↓
Creative Briefs
    ↓
Muse (Asset Creation)
```

### 2. Enhance Cohort → Target Campaign

```
Create Cohort
    ↓
Add Intelligence (6 dimensions)
    ↓
Health Score Increases
    ↓
Use in Campaign Targeting
    ↓
Briefs Include Cohort Context
```

### 3. Monitor Performance → Insights → Adjust

```
Launch Campaign
    ↓
Track Performance
    ↓
Generate Insights
    ↓
Act on Recommendations
    ↓
Adjust Strategy
    ↓
Improved Results
```

---

## 🎨 Design System

### Luxe Black & White Aesthetic
- Premium animations
- Smooth transitions
- Glassmorphism effects
- Micro-interactions
- Responsive layouts

### Color Coding
- **Green** - Positive/healthy (80-100)
- **Blue** - Good/on track (60-79)
- **Amber** - Warning/fair (40-59)
- **Red** - Critical/needs work (0-39)

---

## 🧪 Testing

### Unit Testing
```bash
npm test
```

### UI Testing (Mock Data)
```bash
npm run dev

# Test pages:
# /strategy/positioning
# /strategy/cohorts/:id
# /strategy/campaigns/new
# /strategy/campaigns
# /strategy/insights
```

### API Testing
```bash
# Test endpoints with curl
curl -X POST http://localhost:8000/api/positioning \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", ...}'
```

### Database Testing
```sql
-- Test in Supabase SQL Editor
SELECT * FROM positioning;
SELECT * FROM campaigns;
SELECT * FROM cohorts;
```

---

## 📊 Metrics

### Campaign Health (0-100)
- Pacing vs target (40%)
- Budget utilization (20%)
- Move completion (20%)
- Engagement metrics (20%)

### Cohort Health (0-100)
- Completeness (40%)
- Freshness (20%)
- Journey distribution (20%)
- Recent engagement (20%)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- React & Framer Motion
- FastAPI & Supabase
- AI-powered insights
- Love for strategic marketing

---

## 📞 Support

- **Documentation**: See `FINAL_SUMMARY.md`
- **Issues**: GitHub Issues
- **Questions**: Discussions

---

**Transform your marketing from chaos to coordination** 🚀

Built with ❤️ by the RaptorFlow Team
