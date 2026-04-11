# Requirements: RaptorFlow

**Defined:** 2026-04-11
**Core Value:** Organizations can launch data-driven marketing campaigns faster by leveraging AI agent councils that debate and synthesize strategy, with real-time visualization through an interactive office canvas where AI avatars represent different strategic perspectives.

## v1 Requirements

### Authentication

- [ ] **AUTH-01**: User can sign up with email and password
- [ ] **AUTH-02**: User receives email verification after signup
- [ ] **AUTH-03**: User can reset password via email link
- [ ] **AUTH-04**: User session persists across browser refresh
- [ ] **AUTH-05**: Multi-tenant isolation via Clerk JWT with org_id extraction
- [ ] **AUTH-06**: Row-Level Security enforces tenant data isolation

### Foundation

- [ ] **FOUND-01**: User can create organization
- [ ] **FOUND-02**: User can upload company information via 21-screen structured onboarding
- [ ] **FOUND-03**: Foundation data is versioned with snapshots
- [ ] **FOUND-04**: User can trigger foundation scan (quick/deep modes)
- [ ] **FOUND-05**: Foundation sections can be edited and re-injected

### Campaigns

- [ ] **CAMP-01**: User can create campaign with brief
- [ ] **CAMP-02**: User can view campaign details
- [ ] **CAMP-03**: User can update campaign status
- [ ] **CAMP-04**: User can create moves within campaign
- [ ] **CAMP-05**: User can create tasks within move
- [ ] **CAMP-06**: User can generate content for tasks
- [ ] **CAMP-07**: Campaign replan session can be initiated

### Council (Multi-Agent)

- [ ] **COUNC-01**: User can start council session for campaign
- [ ] **COUNC-02**: Multiple AI agents can debate positions
- [ ] **COUNC-03**: Council session streams progress via WebSocket
- [ ] **COUNC-04**: Council synthesis is generated from debate
- [ ] **COUNC-05**: Agent positions are tracked and persisted

### Muse (Conversational AI)

- [ ] **MUSE-01**: User can start conversational session
- [ ] **MUSE-02**: AI responds contextually based on foundation/campaign
- [ ] **MUSE-03**: Conversation history is persisted
- [ ] **MUSE-04**: Route-based conversation handling

### Intel (Competitor Intelligence)

- [ ] **INTEL-01**: User can capture competitor snapshots
- [ ] **INTEL-02**: User can track SEO rankings
- [ ] **INTEL-03**: User can track ad library
- [ ] **INTEL-04**: Intelligence alerts can be generated
- [ ] **INTEL-05**: Daily Wins briefing can be generated

### Office (Real-Time Canvas)

- [ ] **OFFICE-01**: Real-time office canvas renders via PixiJS
- [ ] **OFFICE-02**: WebSocket broadcasts agent movements
- [ ] **OFFICE-03**: Agent walk events display on canvas
- [ ] **OFFICE-04**: Speech bubbles appear for agent dialogue
- [ ] **OFFICE-05**: Council debates visualize on canvas

### PRL (Predictive Ripple Memory)

- [ ] **PRL-01**: Ripples can be created and tracked
- [ ] **PRL-02**: Ripple edges connect related ripples
- [ ] **PRL-03**: Agent essences are persisted
- [ ] **PRL-04**: Decay policies can be applied

### Billing

- [ ] **BILL-01**: User can subscribe to plan via PhonePe
- [ ] **BILL-02**: Payment events are processed
- [ ] **BILL-03**: Subscription status is tracked

### Content & Media

- [ ] **CONT-01**: File uploads to S3 work
- [ ] **CONT-02**: Content pregeneration via SQS queue
- [ ] **CONT-03**: Embedding jobs process asynchronously

## v2 Requirements

### Social

- **SOCIAL-01**: Social publishing to external platforms
- **SOCIAL-02**: Social media integration (native vs third-party TBD)

### Collaboration

- **COLLAB-01**: Multiple users can collaborate on campaign
- **COLLAB-02**: Approval workflows for content
- **COLLAB-03**: User permissions and roles

### Advanced AI

- **ADVAI-01**: Dynamic replanning engine
- **ADVAI-02**: Full 21-agent council support
- **ADVAI-03**: AI skill evolution (EEL)

### Mobile

- **MOBILE-01**: Mobile application (deferred)

## Out of Scope

| Feature                      | Reason                                                    |
| ---------------------------- | --------------------------------------------------------- |
| Real-time chat between users | Office canvas is for AI collaboration, not user messaging |
| Video content support        | Storage/bandwidth costs, defer to v2+                     |
| OAuth social login           | Email/password via Clerk sufficient for v1                |
| Social native publishing     | Integration-first approach                                |
| Mobile app                   | Web-first, mobile later                                   |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase   | Status  |
| ----------- | ------- | ------- |
| AUTH-01     | Phase 1 | Pending |
| AUTH-02     | Phase 1 | Pending |
| AUTH-03     | Phase 1 | Pending |
| AUTH-04     | Phase 1 | Pending |
| AUTH-05     | Phase 1 | Pending |
| AUTH-06     | Phase 1 | Pending |
| FOUND-01    | Phase 1 | Pending |
| FOUND-02    | Phase 1 | Pending |
| FOUND-03    | Phase 1 | Pending |
| FOUND-04    | Phase 1 | Pending |
| FOUND-05    | Phase 1 | Pending |
| PRL-01      | Phase 1 | Pending |
| PRL-02      | Phase 1 | Pending |
| PRL-03      | Phase 1 | Pending |
| PRL-04      | Phase 1 | Pending |
| CAMP-01     | Phase 2 | Pending |
| CAMP-02     | Phase 2 | Pending |
| CAMP-03     | Phase 2 | Pending |
| CAMP-04     | Phase 2 | Pending |
| CAMP-05     | Phase 2 | Pending |
| CAMP-06     | Phase 2 | Pending |
| CAMP-07     | Phase 2 | Pending |
| CONT-01     | Phase 2 | Pending |
| CONT-02     | Phase 2 | Pending |
| CONT-03     | Phase 2 | Pending |
| INTEL-01    | Phase 3 | Pending |
| INTEL-02    | Phase 3 | Pending |
| INTEL-03    | Phase 3 | Pending |
| INTEL-04    | Phase 3 | Pending |
| INTEL-05    | Phase 3 | Pending |
| COUNC-01    | Phase 4 | Pending |
| COUNC-02    | Phase 4 | Pending |
| COUNC-03    | Phase 4 | Pending |
| COUNC-04    | Phase 4 | Pending |
| COUNC-05    | Phase 4 | Pending |
| MUSE-01     | Phase 4 | Pending |
| MUSE-02     | Phase 4 | Pending |
| MUSE-03     | Phase 4 | Pending |
| MUSE-04     | Phase 4 | Pending |
| OFFICE-01   | Phase 5 | Pending |
| OFFICE-02   | Phase 5 | Pending |
| OFFICE-03   | Phase 5 | Pending |
| OFFICE-04   | Phase 5 | Pending |
| OFFICE-05   | Phase 5 | Pending |
| BILL-01     | Phase 6 | Pending |
| BILL-02     | Phase 6 | Pending |
| BILL-03     | Phase 6 | Pending |

**Coverage:**

- v1 requirements: 36 total
- Mapped to phases: 36
- Unmapped: 0 ✓

---

_Requirements defined: 2026-04-11_
_Last updated: 2026-04-11 after initial definition_
