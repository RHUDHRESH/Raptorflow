# Database Foundation - Quick Reference

## ✅ What Was Created

### Migration Files
1. **`009_strategic_system_foundation.sql`** - 6 new tables
   - `positioning` - Strategic positioning statements
   - `message_architecture` - Message hierarchy and proof points
   - `campaigns` - Campaign orchestration
   - `campaign_cohorts` - Campaign-to-cohort mapping
   - `strategy_insights` - AI-generated insights
   - `competitors` - Competitive intelligence

2. **`010_enhance_existing_tables.sql`** - Enhanced existing tables
   - Added 9 columns to `cohorts` table
   - Added 6 columns to `moves` table
   - Created reference tables (`journey_stages`, `channel_roles`)
   - Added validation functions
   - Created helper views

### Type Definitions
- **`src/types/strategic-system.ts`** - Complete TypeScript types for all new entities

### Documentation
- **`database/MIGRATION_GUIDE.md`** - Step-by-step migration instructions

## 📊 Database Schema Summary

### New Tables (6)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `positioning` | Strategic foundation | who_statement, category_frame, differentiator |
| `message_architecture` | Messaging hierarchy | primary_claim, proof_points[], tagline |
| `campaigns` | Orchestration layer | objective, target_value, channel_strategy |
| `campaign_cohorts` | Campaign targeting | campaign_id, cohort_id, journey stages |
| `strategy_insights` | AI recommendations | insight_type, confidence_score, recommended_action |
| `competitors` | Competitive intel | name, strengths[], weaknesses[] |

### Enhanced Tables (2)

**Cohorts** - Added strategic attributes:
- `buying_triggers` - What makes them act NOW
- `decision_criteria` - How they evaluate (weights must sum to 1.0)
- `objection_map` - What stops them + responses
- `attention_windows` - When/where to reach them
- `journey_distribution` - % at each awareness stage (must sum to 1.0)
- `competitive_frame` - Who else they consider
- `decision_making_unit` - Who's involved in decisions
- `health_score` - 0-100 cohort health metric

**Moves** - Added campaign integration:
- `campaign_id` - Links move to campaign
- `journey_stage_from` - Starting awareness stage
- `journey_stage_to` - Target awareness stage
- `message_variant` - Which proof point to emphasize
- `asset_requirements` - What assets to create
- `intensity` - light/standard/aggressive

## 🎯 Key Concepts

### Journey Stages (5)
1. **Unaware** - Don't know they have a problem
2. **Problem Aware** - Know problem, don't know solutions
3. **Solution Aware** - Know solutions exist, don't know your product
4. **Product Aware** - Know your product, not convinced
5. **Most Aware** - Ready to buy, need final push

### Campaign Objectives (5)
1. **Awareness** - Get on their radar
2. **Consideration** - Get them evaluating you
3. **Conversion** - Get them to act
4. **Retention** - Keep them engaged
5. **Advocacy** - Get them promoting you

### Channel Roles (4)
1. **Reach** - Get attention (ads, social)
2. **Engage** - Build interest (content, email)
3. **Convert** - Drive action (landing pages, calls)
4. **Retain** - Keep engaged (community, support)

## 🔗 Data Flow

```
POSITIONING (strategic foundation)
    ↓
CAMPAIGNS (orchestration)
    ↓
CAMPAIGN_COHORTS (targeting)
    ↓
MOVES (execution with journey transitions)
    ↓
ASSETS (created via Muse)
    ↓
STRATEGY_INSIGHTS (feedback from Matrix)
```

## ✅ Validation Rules

### Decision Criteria Weights
```typescript
// Must sum to 1.0
[
  { criterion: "ROI in 90 days", weight: 0.4 },
  { criterion: "Easy integration", weight: 0.3 },
  { criterion: "Good support", weight: 0.2 },
  { criterion: "Price", weight: 0.1 }
]
// Total: 1.0 ✅
```

### Journey Distribution
```typescript
// Must sum to 1.0
{
  unaware: 0.10,
  problem_aware: 0.30,
  solution_aware: 0.25,
  product_aware: 0.20,
  most_aware: 0.15
}
// Total: 1.0 ✅
```

## 🚀 Next Steps

1. **Run Migrations** - Follow `MIGRATION_GUIDE.md`
2. **Verify Tables** - Run verification queries
3. **Build UI Components** - Phase 2: Positioning Workshop
4. **Create Services** - Backend API endpoints
5. **Test Integration** - End-to-end flow

## 📝 Example Data

### Positioning Example
```sql
INSERT INTO positioning (workspace_id, name, for_cohort_id, who_statement, category_frame, differentiator, reason_to_believe, is_active)
VALUES (
  'workspace-uuid',
  'Primary Positioning',
  'cohort-uuid',
  'who are drowning in marketing chaos',
  'RaptorFlow is the strategic command center',
  'that turns scattered activities into coordinated campaigns',
  'because we combine AI-powered cohort intelligence with battle-tested frameworks',
  true
);
```

### Campaign Example
```sql
INSERT INTO campaigns (workspace_id, positioning_id, name, objective, objective_statement, primary_metric, target_value, status)
VALUES (
  'workspace-uuid',
  'positioning-uuid',
  'Q1 Enterprise CTO Conversion',
  'conversion',
  'Increase demo requests by 40% in Q1',
  'Demo requests',
  50,
  'active'
);
```

### Enhanced Cohort Example
```sql
UPDATE cohorts SET
  buying_triggers = '[
    {"trigger": "End of quarter budget pressure", "strength": "high", "timing": "Q4", "signal": "Mentions budget deadline"}
  ]'::jsonb,
  decision_criteria = '[
    {"criterion": "ROI in 90 days", "weight": 0.4},
    {"criterion": "Easy integration", "weight": 0.3},
    {"criterion": "Good support", "weight": 0.2},
    {"criterion": "Price", "weight": 0.1}
  ]'::jsonb,
  journey_distribution = '{
    "unaware": 0.10,
    "problem_aware": 0.30,
    "solution_aware": 0.25,
    "product_aware": 0.20,
    "most_aware": 0.15
  }'::jsonb
WHERE id = 'cohort-uuid';
```

## 🔍 Useful Queries

### Get Active Positioning
```sql
SELECT * FROM positioning 
WHERE workspace_id = 'your-workspace-id' 
AND is_active = true;
```

### Get Campaign Health Summary
```sql
SELECT * FROM campaign_health_summary 
WHERE workspace_id = 'your-workspace-id';
```

### Get Cohort Journey Distribution
```sql
SELECT * FROM cohort_journey_summary 
WHERE workspace_id = 'your-workspace-id';
```

### Get Moves by Campaign
```sql
SELECT m.*, c.name as campaign_name
FROM moves m
JOIN campaigns c ON m.campaign_id = c.id
WHERE c.workspace_id = 'your-workspace-id'
ORDER BY c.start_date DESC, m.created_at ASC;
```

### Get Latest Strategy Insights
```sql
SELECT * FROM strategy_insights
WHERE workspace_id = 'your-workspace-id'
AND status = 'new'
ORDER BY impact_score DESC, confidence_score DESC
LIMIT 10;
```
