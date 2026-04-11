# State: RaptorFlow

**Project:** RaptorFlow - Marketing Intelligence & Campaign Orchestration
**Current Phase:** Planning (pre-Phase 1)
**Core Value:** Organizations can launch data-driven marketing campaigns faster by leveraging AI agent councils that debate and synthesize strategy, with real-time visualization through an interactive office canvas where AI avatars represent different strategic perspectives.

## Current Position

**Phase:** Planning
**Focus:** Roadmap creation complete, ready for Phase 1 planning

**Roadmap Progress:**

- Total phases: 6
- Current phase: None (planning mode)
- Next action: Plan Phase 1 via `/gsd-plan-phase 1`

## Performance Metrics

| Metric              | Value |
| ------------------- | ----- |
| Total Phases        | 6     |
| Total Requirements  | 36    |
| Requirements Mapped | 36/36 |
| Phases Complete     | 0/6   |

## Phase Status

| Phase | Name              | Status      | Requirements |
| ----- | ----------------- | ----------- | ------------ |
| 1     | Auth & Foundation | Not started | 15           |
| 2     | Campaign Core     | Not started | 10           |
| 3     | Intelligence      | Not started | 5            |
| 4     | AI Communication  | Not started | 9            |
| 5     | Real-Time Office  | Not started | 5            |
| 6     | Billing           | Not started | 4            |

## Accumulated Context

### Key Decisions

| Decision                          | Rationale                                               | Phase   |
| --------------------------------- | ------------------------------------------------------- | ------- |
| PRL treated as Phase 1 dependency | Core memory infrastructure needed by council/office     | Phase 1 |
| Content pipeline in Phase 2       | Depends on foundation data and campaign structure       | Phase 2 |
| Billing isolated to Phase 6       | Can parallelize with other phases, depends only on auth | Phase 6 |

### Research Flags

| Phase   | Flag                                     | Notes                                                  |
| ------- | ---------------------------------------- | ------------------------------------------------------ |
| Phase 3 | Legal boundaries for competitor scraping | Jurisdiction-dependent, evolving                       |
| Phase 5 | PixiJS implementation                    | Limited references, real-time patterns well-documented |

### Dependencies Discovered

```
AUTH + PRL (Phase 1)
    ↓
FOUND (Phase 1)
    ↓
CAMP + CONTENT (Phase 2)
    ↓
COUNC + MUSE (Phase 4)
    ↓
OFFICE (Phase 5)

INTEL (Phase 3) - depends on FOUND
BILL (Phase 6) - depends on AUTH only
```

## Session Continuity

**Created:** 2026-04-11
**Next action:** `/gsd-plan-phase 1` to plan Auth & Foundation phase

---

_State updated: 2026-04-11_
