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
- Node.js 18+
- npm or yarn
- Supabase account (for database)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/raptorflow.git
cd raptorflow

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run database migrations
# In Supabase SQL Editor:
# \i database/migrations/009_strategic_system_foundation.sql
# \i database/migrations/010_enhance_existing_tables.sql

# Start development server
npm run dev
```

Navigate to `http://localhost:5173`

---

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **[Final Summary](FINAL_SUMMARY.md)** - Complete project overview
- **[Project Summary](PROJECT_SUMMARY.md)** - Technical details
- **[Walkthrough](walkthrough.md)** - Detailed examples
- **[Testing Guide](PHASE_8_COMPLETE.md)** - End-to-end testing

---

## 🏗️ Architecture

### Frontend
- **React** - UI framework
- **Framer Motion** - Animations
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **TypeScript** - Type safety

### Backend
- **Python** - Backend language
- **FastAPI** - REST API framework
- **Supabase** - Database (PostgreSQL)
- **Pydantic** - Data validation

### Database
- **8 Tables** - 6 new + 2 enhanced
- **JSONB Columns** - Flexible strategic attributes
- **RLS Policies** - Row-level security
- **Indexes** - Performance optimization

---

## 📁 Project Structure

```
Raptorflow/
├── backend/
│   ├── services/          # 5 backend services
│   ├── routers/           # 5 API routers (40+ endpoints)
│   └── database/          # Migrations and schemas
├── src/
│   ├── pages/
│   │   ├── strategy/      # 5 strategic components
│   │   └── muse/          # Creative brief components
│   └── types/             # TypeScript definitions
└── database/
    └── migrations/        # SQL migrations
```

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
