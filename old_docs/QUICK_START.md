# RaptorFlow Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Run the Frontend
```bash
npm run dev
```
Navigate to: `http://localhost:5173`

### Step 2: Test Key Pages

**1. Positioning Workshop** → `/strategy/positioning`
- Create your positioning statement
- Generate message architecture
- Export as Markdown

**2. Cohort Intelligence** → `/strategy/cohorts/:id`
- Click any cohort
- Add buying triggers
- Define decision criteria
- Map objections
- Set journey distribution
- Watch health score increase

**3. Campaign Builder** → `/strategy/campaigns/new`
- Select positioning
- Choose objective (conversion)
- Target cohorts
- Configure channels
- Generate move recommendations

**4. Campaign Dashboard** → `/strategy/campaigns`
- View all campaigns
- Check health scores
- Monitor pacing
- Pause/resume campaigns

**5. Strategic Insights** → `/strategy/insights`
- View AI-generated insights
- Filter by severity
- Act on recommendations
- Dismiss irrelevant insights

**6. Muse** → `/muse`
- View creative briefs
- Create assets with strategic context

---

## 📁 File Structure

```
Raptorflow/
├── backend/
│   ├── services/
│   │   ├── positioning_service.py ✅
│   │   ├── campaign_service.py ✅
│   │   ├── cohort_intelligence_service.py ✅
│   │   ├── creative_brief_service.py ✅
│   │   └── strategy_insights_service.py ✅
│   └── routers/
│       ├── positioning.py ✅
│       ├── campaigns.py ✅
│       ├── cohorts.py ✅
│       ├── briefs.py ✅
│       └── insights.py ✅
├── src/
│   └── pages/
│       ├── strategy/
│       │   ├── PositioningWorkshop.jsx ✅
│       │   ├── CohortDetail.jsx ✅
│       │   ├── CampaignBuilderLuxe.jsx ✅
│       │   ├── CampaignDashboard.jsx ✅
│       │   └── StrategicInsights.jsx ✅
│       └── muse/
│           └── components/
│               └── CreativeBriefCard.jsx ✅
├── database/
│   └── migrations/
│       ├── 009_strategic_system_foundation.sql ✅
│       └── 010_enhance_existing_tables.sql ✅
└── Documentation/
    ├── FINAL_SUMMARY.md ✅
    ├── PROJECT_SUMMARY.md ✅
    ├── PHASE_1_COMPLETE.md → PHASE_8_COMPLETE.md ✅
    └── walkthrough.md ✅
```

---

## 🎯 Common Tasks

### Create a Complete Campaign

**1. Start with Positioning:**
```
/strategy/positioning
→ Fill 6-step wizard
→ Generate message architecture
→ Save
```

**2. Enhance Your Cohort:**
```
/strategy/cohorts/cohort-123
→ Add 3 buying triggers
→ Add 3 decision criteria (weights sum to 1.0)
→ Add 3 objections with responses
→ Set journey distribution
→ Health score increases to 85+
```

**3. Create Campaign:**
```
/strategy/campaigns/new
→ Select positioning (auto-loads)
→ Choose "Conversion" objective
→ Target: 50 demo requests
→ Select cohort: Enterprise CTOs
→ Journey: Problem Aware → Solution Aware
→ Channels: LinkedIn, Email, Phone
→ Generate moves (4 recommended)
→ Launch
```

**4. Monitor Performance:**
```
/strategy/campaigns
→ View campaign card
→ Check health score
→ Monitor pacing (ahead/on track/behind)
→ View progress bars
```

**5. Review Insights:**
```
/strategy/insights
→ View AI recommendations
→ Act on insights
→ Adjust campaign
```

---

## 🔧 Database Setup (One-time)

```sql
-- In Supabase SQL Editor
\i database/migrations/009_strategic_system_foundation.sql
\i database/migrations/010_enhance_existing_tables.sql
```

---

## 📊 Key Metrics to Track

### Campaign Health Score (0-100)
- 80-100: Excellent (green)
- 60-79: Good (blue)
- 40-59: Fair (amber)
- 0-39: Needs Work (red)

### Cohort Health Score (0-100)
Based on:
- Completeness (40%)
- Freshness (20%)
- Journey distribution (20%)
- Recent engagement (20%)

### Pacing Status
- **Ahead** - Exceeding targets
- **On Track** - Meeting expectations
- **Behind** - Slightly behind
- **At Risk** - Significantly behind

---

## 🎨 UI Components

All components use the **luxe black/white aesthetic**:
- Premium animations (Framer Motion)
- Smooth transitions
- Micro-interactions
- Glassmorphism effects
- Responsive layouts

---

## 📚 Documentation

- **`FINAL_SUMMARY.md`** - Complete project overview
- **`PROJECT_SUMMARY.md`** - Technical summary
- **`PHASE_8_COMPLETE.md`** - Testing guide
- **`walkthrough.md`** - Detailed walkthrough with examples
- **`implementation_plan.md`** - Original implementation plan

---

## 🐛 Troubleshooting

**Issue: Components not loading**
- Check if dev server is running (`npm run dev`)
- Clear browser cache
- Check console for errors

**Issue: Mock data not showing**
- Mock data is hardcoded in components
- Check component files for `MOCK_*` constants

**Issue: Routes not working**
- Check React Router configuration
- Verify route paths in `App.jsx`

---

## 🚀 Next Steps

### Immediate
1. ✅ Test all UI components with mock data
2. ✅ Review documentation
3. ✅ Explore code structure

### Short-term
1. Connect API routers to backend services
2. Add authentication middleware
3. Configure CORS
4. Test endpoints

### Long-term
1. Deploy to staging
2. User testing
3. Production deployment
4. Monitor and iterate

---

## 💡 Pro Tips

1. **Start with Positioning** - Everything flows from positioning
2. **Enhance Cohorts First** - Better intelligence = better campaigns
3. **Use Journey Stages** - Map cohort awareness to campaign objectives
4. **Monitor Health Scores** - Early warning system for issues
5. **Act on Insights** - Feedback loop improves recommendations

---

**Need Help?**
- Review `FINAL_SUMMARY.md` for complete overview
- Check `PHASE_8_COMPLETE.md` for testing guide
- Read `walkthrough.md` for detailed examples

---

**Built with ❤️ for strategic marketers**  
**Powered by AI-driven intelligence**
