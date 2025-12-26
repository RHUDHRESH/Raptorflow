import { z } from 'zod';

// ==========================================
// Enums / Unions
// ==========================================

// Legacy types (kept for backward compatibility)
export type BusinessStage = 'idea' | 'pre-launch' | 'beta' | 'live' | 'scaling' | 'early' | 'growth'; // Updated + legacy
export type RevenueModel = 'saas' | 'services' | 'product' | 'marketplace' | 'other';
export type TeamSize = 'solo' | '2-5' | '6-20' | '20+';

export type CustomerType = 'b2b' | 'b2c' | 'b2g' | 'mixed';
export type SCARFDriver = 'status' | 'certainty' | 'autonomy' | 'relatedness' | 'fairness';
export type DecisionStyle = 'satisficer' | 'maximizer';
export type RiskTolerance = 'regret-minimizer' | 'opportunity-seeker';

// ==========================================
// New Types for Know You Flow
// ==========================================

export type BusinessType = 'saas' | 'agency' | 'd2c' | 'local-service' | 'creator' | 'marketplace' | 'other';
export type PriceBand = 'free' | 'under-5k' | '5k-25k' | '25k-1l' | '1l-plus';
export type SalesMotion = 'self-serve' | 'demo-led' | 'hybrid';
export type BuyerRoleChip = 'founder' | 'marketing' | 'sales' | 'hr' | 'ops' | 'finance' | 'other';
export type RegionCode = 'india' | 'us' | 'eu' | 'global' | 'other';
export type LanguageCode = 'english' | 'hinglish' | 'tamil' | 'hindi' | 'other';
export type PrimaryGoal = 'leads' | 'close-deals' | 'increase-conversion' | 'content-engine' | 'launch' | 'retention';
export type Constraint = 'low-budget' | 'no-time' | 'no-design' | 'compliance' | 'no-audience';
export type Channel = 'linkedin' | 'instagram' | 'whatsapp' | 'email' | 'youtube' | 'seo' | 'ads' | 'offline';
export type ToolOption = 'none' | 'sheets' | 'notion' | 'hubspot' | 'zoho' | 'pipedrive' | 'mailchimp' | 'klaviyo' | 'other';
export type ProofType = 'testimonials' | 'case-study' | 'metrics' | 'logos' | 'none';
export type VoicePreference = 'calm-premium' | 'direct-punchy' | 'friendly-warm' | 'technical-precise' | 'bold-contrarian';

// NEW: Trigger event types
export type TriggerEvent =
  | 'hiring-surge' | 'funding-round' | 'missed-target' | 'compliance-change'
  | 'competitor-threat' | 'tech-migration' | 'team-expansion' | 'churn-spike'
  | 'reorg' | 'new-leadership' | 'budget-approval' | 'seasonal-peak';

// NEW: Alternative/competitor types
export type AlternativeType =
  | 'spreadsheets' | 'notion' | 'hubspot' | 'marketo' | 'agencies'
  | 'freelancers' | 'zapier-glue' | 'internal-team' | 'nothing';

// ==========================================
// Phase 1 Discovery Objects (Customer Discovery Output)
// ==========================================

export type ChangeType = 'regulation' | 'tech' | 'behavior' | 'competitor' | 'cost' | 'market' | 'other';
export type BragMetric = 'revenue' | 'leads' | 'cac' | 'roas' | 'activation' | 'retention' | 'churn' | 'nps' | 'hours-saved' | 'other';
export type OptimizingFor = 'acquire' | 'activate' | 'retain' | 'monetize' | 'expand' | 'reposition';
export type OfferType = 'saas' | 'service' | 'course' | 'marketplace' | 'app' | 'hardware' | 'other';
export type DeliveryMode = 'done-for-you' | 'done-with-you' | 'coaching';
export type TimeToValue = 'instant' | 'same-day' | '1-week' | '2-4-weeks' | '1-3-months' | 'longer';
export type PricingMode = 'monthly' | 'annual' | 'per-seat' | 'per-usage' | 'one-time' | 'performance';
export type TriggerType = 'hiring' | 'revenue-drop' | 'growth-plateau' | 'new-launch' | 'competitor' | 'budget-cycle' | 'compliance' | 'burnout' | 'other';
export type VoiceTone = 'calm' | 'bold' | 'technical' | 'friendly' | 'luxury' | 'playful';
export type ArtifactLocation = 'sheets' | 'excel' | 'notion' | 'hubspot' | 'whatsapp' | 'slack' | 'email' | 'trello' | 'in-my-head' | 'other';

export interface IdentityCard {
  name: string;
  pronunciation?: string;
  company: string;
  websiteUrl?: string;
  geo: {
    basedIn: string;
    sellsTo: RegionCode[];
  };
}

export interface OriginStory {
  narrative: string;
  whatPissedYouOff?: string;
  contrarianBelief?: string;
}

export interface WhyNow {
  mission: string;
  recentChange: string;
  changeType: ChangeType;
  changeDate?: string;
}

export interface SuccessDefinition {
  win90Days: string;
  win90Bullets: string[];
  win12Months: string;
  bragMetric: BragMetric;
  bragMetricCustom?: string;
  optimizingFor: OptimizingFor;
}

export interface OfferSpec {
  primaryType: OfferType;
  deliveryMode?: DeliveryMode;
  timeToValue: TimeToValue;
  unfairAdvantage: {
    howWeWin: string;
    whyCantCopy: string;
    whyItMatters: string;
  };
}

export interface ValueMetric {
  pricingMode: PricingMode;
  priceRangeMin?: number;
  priceRangeMax?: number;
  currency: string;
}

export interface BuyerUserMap {
  userRoles: string[];
  buyerRoles: string[];
  samePersonAsBuyer: boolean;
}

export interface TriggerMapItem {
  type: TriggerType;
  freeText?: string;
}

export interface TriggerMap {
  triggers: TriggerMapItem[];
}

export interface WorkflowStep {
  action: string;
  tool: string;
  timeSpent: string;
}

export interface TriedBefore {
  toolOrService: string;
  whatYouHoped: string;
  whatFailed: string;
}

export interface CurrentSystemMap {
  workflowSteps: WorkflowStep[];
  artifacts: ArtifactLocation[];
  triedBefore: TriedBefore[];
}

export interface ProofGuardrails {
  proofAssets: {
    testimonials: boolean;
    caseStudies: boolean;
    numbers: boolean;
    logos: boolean;
    screenshots: boolean;
  };
  forbiddenClaims: string[];
  voiceTone: VoiceTone;
  wordsToAvoid: string[];
}

export interface Phase1Discovery {
  identity: IdentityCard;
  origin: OriginStory;
  whyNow: WhyNow;
  success: SuccessDefinition;
  offer: OfferSpec;
  value: ValueMetric;
  buyerUser: BuyerUserMap;
  triggers: TriggerMap;
  currentSystem: CurrentSystemMap;
  proofGuardrails: ProofGuardrails;
}

// ==========================================
// Phase 3 — Differentiation Blueprint (Framework 3.0)
// ==========================================

// JTBD Forces (Push/Pull/Anxiety/Habit)
export type JobType = 'functional' | 'emotional' | 'social';

export interface JTBDJob {
  id: string;
  type: JobType;
  statement: string;
  isPrimary: boolean;
}

export interface JTBDForces {
  jobs: JTBDJob[];
  functional?: string; // Precision 3.0
  emotional?: string;  // Precision 3.0
  social?: string;     // Precision 3.0
  strugglingMoments: string[];
  forces: {
    push: string[];
    pull: string[];
    anxiety: string[];
    habit: string[];
  };
  switchTriggers: string[];
  successMetrics: string[];
}

export interface MessageHierarchy {
  essence: string;
  coreMessage: string;
  pillars: Array<{
    title: string;
    description: string;
    proofPoints: string[];
  }>;
}

export interface AwarenessMatrix {
  unaware: string;
  problem: string;
  solution: string;
  product: string;
  most: string;
}

// Complete Phase 3 Data
export interface Phase3Data {
  primaryContextId: string;
  primaryContext: PrimaryContext;
  jtbd: JTBDForces;
  hierarchy?: MessageHierarchy; // Precision 3.0
  awarenessMatrix?: AwarenessMatrix; // Precision 3.0
  vpc: VPCData;
  differentiators: Differentiator[];
  strategyCanvas: StrategyCanvas;
  errc: ERRCGrid;
  claims: Claim[];
  primaryClaimId: string;
  proofStack: ProofStackEntry[];
  lockedAt?: string;
}

// Value Proposition Canvas
export interface VPCPain {
  id: string;
  text: string;
  severity: number; // 1-5
}

export interface VPCGain {
  id: string;
  text: string;
  importance: number; // 1-5
}

export interface VPCReliever {
  id: string;
  text: string;
  painId: string; // links to VPCPain
}

export interface VPCCreator {
  id: string;
  text: string;
  gainId: string; // links to VPCGain
}

export interface VPCData {
  customerProfile: {
    jobs: string[];
    pains: VPCPain[];
    gains: VPCGain[];
  };
  valueMap: {
    productsServices: string[];
    painRelievers: VPCReliever[];
    gainCreators: VPCCreator[];
  };
  fitCoverage: {
    score: number; // 0-100%
    gaps: string[];
  };
}

// Strategy Canvas (Blue Ocean)
export interface CanvasFactor {
  id: string;
  name: string;
  mattersToUs: boolean;
  targetLevel: 1 | 2 | 3 | 4 | 5;
}

export interface StrategyCanvas {
  factors: CanvasFactor[];
  curves: {
    statusQuo: number[];
    categoryLeader: number[];
    youCurrent: number[];
    youTarget: number[];
  };
  competitorNames: string[];
}

// ERRC Grid (Eliminate/Reduce/Raise/Create)
export interface ERRCItem {
  factor: string;
  reason: string;
}

export interface ERRCGrid {
  eliminate: ERRCItem[];
  reduce: ERRCItem[];
  raise: ERRCItem[];
  create: ERRCItem[];
}

// USP/UVP Claims
export type ProofStrength = 'A' | 'B' | 'C' | 'D';

export interface Claim {
  id: string;
  audience: string;
  promise: string;
  mechanism: string;
  uniqueness: string;
  proof: string[];
  proofStrength: ProofStrength;
  riskFlags: string[];
  // Reeves USP Gates
  isSpecific: boolean;
  isUnique: boolean;
  movesBuyers: boolean;
}

// Differentiator with proof status
export type DifferentiatorStatus = 'proven' | 'unproven' | 'blocked';

export interface Differentiator {
  id: string;
  capability: string;
  mechanism: string;
  proof: string[];
  status: DifferentiatorStatus;
}

// Proof Stack Entry
export interface ProofStackEntry {
  claim: string;
  proof: string[];
  strength: ProofStrength;
  confidence: number; // 0-1
}

// Primary Context (what we understood)
export interface PrimaryContext {
  youSell: string;
  to: string;
  soTheyCan: string;
}

// Complete Phase 3 Data
export interface Phase3Data {
  primaryContextId: string;
  primaryContext: PrimaryContext;
  jtbd: JTBDForces;
  vpc: VPCData;
  differentiators: Differentiator[];
  strategyCanvas: StrategyCanvas;
  errc: ERRCGrid;
  claims: Claim[];
  primaryClaimId: string;
  proofStack: ProofStackEntry[];
  lockedAt?: string;
}

// ==========================================
// Phase 4 — Positioning Lab (Dunford Compiler)
// ==========================================

// Market Category (Dunford Component #5)
export interface MarketCategory {
  primary: string;
  altLabels: string[];
  whyThisContext: string[];
  risk?: 'too-broad' | 'too-weird' | 'too-crowded' | 'ok';
}

// Competitive Alternative (Dunford Component #1)
export interface CompetitiveAlternative {
  id: string;
  name: string;
  whatUsedFor: string;
  whatBreaks: string;
  whyTolerated: string;
  evidence: string[];
  isConfirmed: boolean;
}

export type CompetitorType = 'statusQuo' | 'direct' | 'indirect';

export interface CompetitiveAlternatives {
  statusQuo: CompetitiveAlternative[];
  direct: CompetitiveAlternative[];
  indirect: CompetitiveAlternative[];
  replacementStory: string;
}

// Differentiated Capability (Dunford Component #2)
export interface DifferentiatedCapability {
  id: string;
  capability: string;
  enables: string;
  evidence: string[];
  easyToCopy: boolean;
}

// Differentiated Value (Dunford Component #3)
export interface DifferentiatedValue {
  id: string;
  value: string;
  forWhom: string;
  because: string;
  evidence: string[];
  isDominant: boolean;
}

// Target Segment (Dunford Component #4)
export interface SegmentScores {
  pain: number;       // 1-5
  budget: number;     // 1-5
  triggers: number;   // 1-5
  switching: number;  // 1-5
  proofFit: number;   // 1-5
}

export interface TargetSegment {
  id: string;
  name: string;
  firmographics: Record<string, string>;
  jtbd: string;
  whyBestFit: string[];
  scores: SegmentScores;
  isPrimary: boolean;
  isExcluded: boolean;
}

// Perceptual Map (2x2)
export interface PerceptualMapAxis {
  label: string;
  rationale: string;
  minLabel?: string;
  maxLabel?: string;
}

export interface PerceptualMapPoint {
  id: string;
  name: string;
  x: number; // -1 to 1
  y: number; // -1 to 1
  isYou: boolean;
}

export interface PerceptualMap {
  xAxis: PerceptualMapAxis;
  yAxis: PerceptualMapAxis;
  points: PerceptualMapPoint[];
}

// Category Ladder (Ries/Trout)
export interface LadderRung {
  brand: string;
  position: number; // 1 = top
  isYou: boolean;
}

export interface CategoryLadder {
  category: string;
  rungs: LadderRung[];
  whyDifferentLadder: string;
}

// TAM/SAM/SOM
export interface MarketSize {
  value: number;
  currency: string;
  formula: string;
}

export interface TAMSAMSOM {
  tam: MarketSize & { category: string };
  sam: MarketSize & { segment: string };
  som: MarketSize & { reachability: string };
  assumptions: string[];
}

// Elevator Pitch variants
export interface ElevatorPitch {
  tenSec: string;
  thirtySec: string;
  twoMin: string;
}

// We Are / We Are Not
export interface WeAreWeAreNot {
  weAre: string[];
  weAreNot: string[];
}

// Objection Killshot
export interface ObjectionKillshot {
  id: string;
  objection: string;
  alternativeTied: string;
  response: string;
  evidence: string;
}

// Phase 4 Visuals Bundle
export interface Phase4Visuals {
  perceptualMap: PerceptualMap;
  ladder: CategoryLadder;
  strategyCanvas: StrategyCanvas;
  errc: ERRCGrid;
}

// Complete Phase 4 Data
export interface Phase4Data {
  marketCategory: MarketCategory;
  categoryOptions: MarketCategory[]; // 3-7 candidates
  competitiveAlternatives: CompetitiveAlternatives;
  differentiatedCapabilities: DifferentiatedCapability[];
  differentiatedValue: DifferentiatedValue[];
  targetSegments: TargetSegment[];
  positioningStatement: string;
  elevatorPitch: ElevatorPitch;
  weAreWeAreNot: WeAreWeAreNot;
  objectionKillshots: ObjectionKillshot[];
  visuals: Phase4Visuals;
  tamSamSom: TAMSAMSOM;
  proofStack: ProofStackEntry[];
  version: string;
  lockedAt?: string;
}

// ==========================================
// Phase 5 — ICP Engine (ICP Compiler)
// ==========================================

// Data Confidence Tag
export type DataConfidence = 'proven' | 'inferred' | 'assumed';

// Firmographics (ICP account-level)
export interface ICPFirmographics {
  industries: string[];
  excludedIndustries: string[];
  companySizeMin: number;
  companySizeMax: number;
  revenueMin: number;
  revenueMax: number;
  geographies: string[];
  excludedGeos: string[];
}

// Technographics (stack signals)
export interface ICPTechnographics {
  mustHave: string[];
  niceToHave: string[];
  disqualifiers: string[];
  unknownStack: boolean;
}

// JTBD per ICP
export interface ICPJTBD {
  functional: string;
  emotional: string;
  social: string;
}

// Forces of Progress item
export interface ForceItem {
  text: string;
  confidence: DataConfidence;
}

// Forces of Progress (JTBD switching physics)
export interface ICPForcesOfProgress {
  push: ForceItem[];
  pull: ForceItem[];
  anxiety: ForceItem[];
  habit: ForceItem[];
}

// Buying Role (inside Buying Group)
export interface BuyingRole {
  id: string;
  role: string;
  isActive: boolean;
  influence: 'high' | 'medium' | 'low';
}

// Buying Job (Gartner model)
export type BuyingJobType = 'problem-id' | 'solution-explore' | 'requirements' | 'supplier-select';

export interface BuyingJob {
  job: BuyingJobType;
  primaryRoleId: string;
  supportRoleIds: string[];
}

// Buying Group (consensus physics)
export interface BuyingGroup {
  roles: BuyingRole[];
  buyingJobs: BuyingJob[];
  consensusPath: string[];
  frictionLevel: number; // 1-5
}

// Habitat / Discovery
export interface ICPHabitat {
  platforms: string[];
  communities: string[];
  searchTermsProblem: string[];
  searchTermsSolution: string[];
  contentTypes: string[];
  triggerMoments: string[];
  trustSources: string[];
}

// Fit Score
export interface ICPFitScore {
  valueFit: number;      // 1-5
  switchability: number; // 1-5
  reachability: number;  // 1-5
  dealSize: number;      // 1-5
  confidence: number;    // 1-5
  total: number;
}

// Persona Goal/Objection with confidence
export interface PersonaItem {
  text: string;
  confidence: DataConfidence;
}

// Persona (inside ICP)
export interface ICPPersona {
  id: string;
  role: string;
  goals: PersonaItem[];
  kpis: string[];
  objections: PersonaItem[];
  proofNeeds: string[];
  language: string[];
}

// Candidate Segment (pre-ICP)
export interface CandidateSegment {
  id: string;
  label: string;
  displacedAlternative: string;
  dominantValue: string;
  fitScore: ICPFitScore;
  kept: boolean;
  reason?: string;
}

// ICP (account-level)
export interface ICP {
  id: string;
  name: string;
  firmographics: ICPFirmographics;
  technographics: ICPTechnographics;
  jtbd: ICPJTBD;
  forces: ICPForcesOfProgress;
  triggers: string[];
  buyingGroup: BuyingGroup;
  personas: ICPPersona[];
  habitat: ICPHabitat;
  objections: string[];
  fitScore: ICPFitScore;
  displacedAlternative: string;
  dominantValue: string;
  dataConfidence: {
    proven: string[];
    inferred: string[];
    assumed: string[];
  };
}

// Inter-ICP Graph Node
export interface ICPGraphNode {
  id: string;
  type: 'icp' | 'influencer';
  label: string;
}

// Inter-ICP Graph Edge
export type ICPEdgeType = 'influences' | 'refers' | 'upstream' | 'downstream';

export interface ICPGraphEdge {
  id: string;
  from: string;
  to: string;
  type: ICPEdgeType;
  weight: number; // 1-5
}

// Inter-ICP Relationship Graph
export interface InterICPGraph {
  nodes: ICPGraphNode[];
  edges: ICPGraphEdge[];
  primaryWedgeICP: string;
}

// Complete Phase 5 Data
export interface Phase5Data {
  candidateSegments: CandidateSegment[];
  icps: ICP[];
  interICPGraph: InterICPGraph;
  version: string;
  lockedAt?: string;
}

// ==========================================
// Phase 6 — Soundbite Forge (Messaging Engine)
// ==========================================

// Awareness Stage (Schwartz)
export type AwarenessStage = 'unaware' | 'problem' | 'solution' | 'product' | 'most';

// Soundbite Types (Precision 3.0 - 7 types)
export type SoundbiteType =
  | 'problem_revelation'
  | 'agitation'
  | 'mechanism'
  | 'objection_handling'
  | 'transformation'
  | 'positioning'
  | 'urgency';

// Rigor Gate Scores
export interface RigorScores {
  specificity: number;      // 1-5: penalize empty adjectives
  proof: number;            // 1-5: attached proof type
  differentiation: number;  // 1-5: competitor couldn't say this
  awarenessFit: number;     // 1-5: matches awareness stage
  cognitiveLoad: number;    // 1-5: length/complexity
  total: number;
  passing: boolean;
}

// Soundbite
export interface Soundbite {
  id: string;
  type: SoundbiteType;
  text: string;
  icpId: string;
  awarenessStage: AwarenessStage;
  buyingJob: BuyingJobType;
  proofIds: string[];
  scores: RigorScores;
  isLocked: boolean;
  alternatives: string[];
}

// Messaging Pillar
export interface MessagingPillar {
  id: string;
  name: string;
  proofIds: string[];
  isProven: boolean;
  priority: number;
}

// Messaging Blueprint (hierarchy)
export interface MessagingBlueprint {
  controllingIdea: string;
  coreMessage: string;
  pillars: MessagingPillar[];
  missingProofAlerts: string[];
}

// Soundbite Variants (channel-ready)
export interface SoundbiteVariants {
  soundbiteId: string;
  landingHero: string;
  subhead: string;
  adHooks: string[];
  emailSubjects: string[];
  salesOpener: string;
  linkedInOpener: string;
}

// Reality Check (auditable validation)
export interface CompetitorCheck {
  soundbiteId: string;
  couldSay: boolean;
  competitor: string;
  reason: string;
}

export interface ProofQualityCheck {
  soundbiteId: string;
  quality: 'weak' | 'medium' | 'strong';
  reason: string;
}

export interface RealityCheck {
  competitorChecks: CompetitorCheck[];
  proofQuality: ProofQualityCheck[];
  awarenessMismatches: string[];
  claimsAtRisk: string[];
}

// Constraint Policy
export type TonePreference = 'direct' | 'warm' | 'premium' | 'aggressive';

export interface ConstraintPolicy {
  bannedClaims: string[];
  bannedWords: string[];
  regulatedFlags: string[];
  tonePreference: TonePreference;
}

// Complete Phase 6 Data
export interface Phase6Data {
  blueprint: MessagingBlueprint;
  soundbites: Soundbite[];
  variants: SoundbiteVariants[];
  realityCheck: RealityCheck;
  constraints: ConstraintPolicy;
  version: string;
  lockedAt?: string;
}

// ==========================================
// Section Data Interfaces
// ==========================================

export interface BusinessBasics {
  name: string;
  industry: string;
  stage: BusinessStage | '';
  businessType?: BusinessType | '';        // NEW: Type of business
  revenueModel: RevenueModel[] | RevenueModel | '';
  teamSize: TeamSize | '';
  contextFiles?: string[];
  websiteUrl?: string;                     // NEW: The one link
  offerStatement?: string;                 // NEW: One-line offer
  priceBand?: PriceBand | '';              // NEW
  salesMotion?: SalesMotion | '';          // NEW
}

export interface ConfessionData {
  expensiveProblem: string;
  embarrassingTruth: string;
  stupidIdea: string;
  signaling: string;
  friction: string;
}

export interface CohortData {
  customerType: CustomerType[] | CustomerType | '';
  buyerRole: string;
  buyerRoleChips?: BuyerRoleChip[];        // NEW: Chip-based buyer role
  primaryRegions?: RegionCode[];            // NEW: Regions where they sell
  languages?: LanguageCode[];               // NEW: Languages they use
  primaryDrivers: SCARFDriver[];
  decisionStyle: DecisionStyle | '';
  riskTolerance: RiskTolerance | '';
  // B2B conditional fields
  companySize?: string;
  salesCycle?: string;
  // D2C conditional field
  averageOrderValue?: string;
}

export interface PositioningData {
  category: string;
  targetAudience: string;
  psychologicalOutcome: string;
  ownedPosition: string;
  reframedWeakness: string;
}

export interface MessagingData {
  primaryHeuristic: string;
  beliefPillar: string;
  promisePillar: string;
  proofPillar: string;
  voicePreference?: VoicePreference | '';   // NEW: Voice preference
}

// NEW: Goals section for Know You flow
export interface GoalsData {
  primaryGoal?: PrimaryGoal | '';
  constraints?: Constraint[];
}

// NEW: Current reality section
export interface CurrentRealityData {
  currentChannels?: Channel[];
  currentTools?: ToolOption[];
}

// NEW: Proof inventory section
export interface ProofData {
  proofTypes?: ProofType[];
}

// NEW: Customer insights section (best customers, triggers, alternatives, pains)
export interface CustomerInsightsData {
  bestCustomers?: string[];           // 3 best customer descriptions
  triggerEvents?: TriggerEvent[];     // What makes them buy now
  alternatives?: AlternativeType[];   // What they used before
  painRanking?: string[];             // Ranked list of pains
}

// ==========================================
// Derived Data Interfaces (from Backend)
// ==========================================

// ICP Reveal Response
export interface DerivedICP {
  id: string;
  name: string;
  priority: 'primary' | 'secondary' | 'expansion';
  confidence: number;
  description: string;

  firmographics: {
    companySize: string;
    industry: string[];
    geography: string[];
    budget: string;
  };

  painMap: {
    primary: string;
    secondary: string[];
    triggers: string[];
    urgency: 'now' | 'soon' | 'someday';
  };

  social: {
    platforms: Array<{ name: string; timing: string; vibe: string }>;
    authorities: string[];
  };

  buying: {
    committee: Array<{ role: string; focus: string }>;
    timeline: string;
    proofNeeded: string[];
    blockers: string[];
  };

  behavioral: {
    biases: Array<{ name: string; implication: string }>;
    deRisking: string[];
  };
}

// Positioning Reveal Response
export interface DerivedPositioning {
  matrix: {
    xAxis: { label: string; lowEnd: string; highEnd: string };
    yAxis: { label: string; lowEnd: string; highEnd: string };
    positions: Array<{ name: string; x: number; y: number; isYou: boolean }>;
  };

  ladder: Array<{
    rung: number;
    name: string;
    description: string;
    score: number;
    isYou: boolean;
  }>;

  statement: {
    forWhom: string;
    company: string;
    category: string;
    differentiator: string;
    unlikeCompetitor: string;
    because: string;
  };

  oneThing: string;
  defensibility: 'low' | 'medium' | 'high';
}

// Competitive Reveal Response
export interface DerivedCompetitive {
  statusQuo: {
    name: string;
    description: string;
    manualPatches: string[];
    toleratedPain: string;
    yourWedge: string;
  };

  indirect: Array<{
    name: string;
    mechanism: string;
    priceRange: string;
    weakness: string;
    yourEdge: string;
  }>;

  direct: Array<{
    name: string;
    positioning: string;
    weakness: string;
    yourEdge: string;
    featureOverlap: 'low' | 'medium' | 'high';
  }>;
}

// Soundbites Reveal Response
export interface DerivedSoundbites {
  oneLiner: string;

  soundbites: Array<{
    type: 'problem' | 'agitation' | 'mechanism' | 'objection' | 'transformation' | 'proof' | 'urgency';
    awarenessLevel: 'unaware' | 'problem' | 'solution' | 'product' | 'most';
    text: string;
    useCase: string;
  }>;
}

// Market Reveal Response
export interface DerivedMarket {
  tam: { value: number; confidence: 'low' | 'med' | 'high'; method: string };
  sam: { value: number; confidence: 'low' | 'med' | 'high'; method: string };
  som: { value: number; confidence: 'low' | 'med' | 'high'; timeline: string };

  assumptions: Array<{
    factor: string;
    value: string;
    confidence: 'low' | 'med' | 'high';
  }>;

  pathToSom: {
    customersNeeded: number;
    leadsPerMonth: number;
    winRate: number;
    channelMix: Array<{ channel: string; percentage: number }>;
  };

  sliderDefaults: {
    targetAccounts: number;
    reachablePercent: number;
    qualifiedPercent: number;
    adoptionPercent: number;
    arpa: number;
  };
}

// Combined Derived Data
export interface DerivedData {
  derivedAt?: string;
  icps?: DerivedICP[];
  positioning?: DerivedPositioning;
  competitive?: DerivedCompetitive;
  soundbites?: DerivedSoundbites;
  market?: DerivedMarket;
}

// ==========================================
// Proof Vault Types
// ==========================================

export interface ProofItem {
  id: string;
  type: 'testimonial' | 'case_study' | 'metric' | 'logo' | 'screenshot' | 'document';
  title: string;
  content: string;
  source?: string;
  date?: string;
  tags: string[];
  rating?: number;
  verified?: boolean;
  linkedPhases?: number[];
}

// ==========================================
// Main Foundation Data
// ==========================================

export const brandKitSchema = z.object({
  brandVoice: z.string().min(1, 'Brand voice is required'),
  positioning: z.string().min(1, 'Positioning statement is required'),
  messagingPillars: z.array(z.string().min(1))
    .min(1, 'At least one messaging pillar is required')
    .max(5, 'Maximum of 5 messaging pillars allowed'),
});

export type BrandKit = z.infer<typeof brandKitSchema>;

export const defaultBrandKit: BrandKit = {
  brandVoice: '',
  positioning: '',
  messagingPillars: [''],
};

export interface FoundationData {
  currentStep: number;
  completedAt?: string;

  // Core sections
  business: BusinessBasics;
  confession: ConfessionData;
  cohorts: CohortData;
  positioning: PositioningData;
  messaging: MessagingData;

  // Know You sections
  goals?: GoalsData;
  reality?: CurrentRealityData;
  proof?: ProofData;
  customerInsights?: CustomerInsightsData;  // NEW

  // Derived data (from backend)
  derived?: DerivedData;

  // NEW: Phase 1 Customer Discovery
  phase1?: Phase1Discovery;

  // NEW: Phase 3 Differentiation Blueprint
  phase3?: Phase3Data;

  // NEW: Phase 4 Positioning Lab
  phase4?: Phase4Data;

  // NEW: Phase 5 ICP Engine
  phase5?: Phase5Data;

  // NEW: Phase 6 Soundbite Forge
  phase6?: Phase6Data;

  // NEW: Evidence & Proof Vault
  proofVault?: ProofItem[];

  // Legacy support
  brandVoice?: string;
}

// ==========================================
// Initial State
// ==========================================

export const emptyFoundation: FoundationData = {
  currentStep: 0,
  business: {
    name: '',
    industry: '',
    stage: '',
    businessType: '',
    revenueModel: '',
    teamSize: '',
    websiteUrl: '',
    offerStatement: '',
    priceBand: '',
    salesMotion: '',
  },
  confession: {
    expensiveProblem: '',
    embarrassingTruth: '',
    stupidIdea: '',
    signaling: '',
    friction: ''
  },
  cohorts: {
    customerType: '',
    buyerRole: '',
    buyerRoleChips: [],
    primaryRegions: [],
    languages: [],
    primaryDrivers: [],
    decisionStyle: '',
    riskTolerance: '',
    companySize: '',
    salesCycle: '',
    averageOrderValue: '',
  },
  positioning: {
    category: '',
    targetAudience: '',
    psychologicalOutcome: '',
    ownedPosition: '',
    reframedWeakness: ''
  },
  messaging: {
    primaryHeuristic: '',
    beliefPillar: '',
    promisePillar: '',
    proofPillar: '',
    voicePreference: '',
  },
  goals: {
    primaryGoal: '',
    constraints: [],
  },
  reality: {
    currentChannels: [],
    currentTools: [],
  },
  proof: {
    proofTypes: [],
  },
  customerInsights: {
    bestCustomers: [],
    triggerEvents: [],
    alternatives: [],
    painRanking: [],
  },
  brandVoice: ''
};

// Empty Phase 1 Discovery for initialization
export const emptyPhase1Discovery: Phase1Discovery = {
  identity: {
    name: '',
    company: '',
    geo: { basedIn: '', sellsTo: [] }
  },
  origin: { narrative: '' },
  whyNow: { mission: '', recentChange: '', changeType: 'other' },
  success: {
    win90Days: '',
    win90Bullets: [],
    win12Months: '',
    bragMetric: 'revenue',
    optimizingFor: 'acquire'
  },
  offer: {
    primaryType: 'saas',
    timeToValue: 'instant',
    unfairAdvantage: { howWeWin: '', whyCantCopy: '', whyItMatters: '' }
  },
  value: { pricingMode: 'monthly', currency: 'INR' },
  buyerUser: { userRoles: [], buyerRoles: [], samePersonAsBuyer: true },
  triggers: { triggers: [] },
  currentSystem: { workflowSteps: [], artifacts: [], triedBefore: [] },
  proofGuardrails: {
    proofAssets: { testimonials: false, caseStudies: false, numbers: false, logos: false, screenshots: false },
    forbiddenClaims: [],
    voiceTone: 'calm',
    wordsToAvoid: []
  }
};

// Empty Phase 3 Differentiation Blueprint for initialization
export const emptyPhase3: Phase3Data = {
  primaryContextId: '',
  primaryContext: { youSell: '', to: '', soTheyCan: '' },
  jtbd: {
    jobs: [],
    functional: '',
    emotional: '',
    social: '',
    strugglingMoments: [],
    forces: { push: [], pull: [], anxiety: [], habit: [] },
    switchTriggers: [],
    successMetrics: []
  },
  hierarchy: {
    essence: '',
    coreMessage: '',
    pillars: []
  },
  awarenessMatrix: {
    unaware: '',
    problem: '',
    solution: '',
    product: '',
    most: ''
  },
  vpc: {
    customerProfile: { jobs: [], pains: [], gains: [] },
    valueMap: { productsServices: [], painRelievers: [], gainCreators: [] },
    fitCoverage: { score: 0, gaps: [] }
  },
  differentiators: [],
  strategyCanvas: {
    factors: [],
    curves: { statusQuo: [], categoryLeader: [], youCurrent: [], youTarget: [] },
    competitorNames: []
  },
  errc: { eliminate: [], reduce: [], raise: [], create: [] },
  claims: [],
  primaryClaimId: '',
  proofStack: []
};

// Empty Phase 4 Positioning Lab for initialization
export const emptyPhase4: Phase4Data = {
  marketCategory: { primary: '', altLabels: [], whyThisContext: [] },
  categoryOptions: [],
  competitiveAlternatives: {
    statusQuo: [],
    direct: [],
    indirect: [],
    replacementStory: ''
  },
  differentiatedCapabilities: [],
  differentiatedValue: [],
  targetSegments: [],
  positioningStatement: '',
  elevatorPitch: { tenSec: '', thirtySec: '', twoMin: '' },
  weAreWeAreNot: { weAre: [], weAreNot: [] },
  objectionKillshots: [],
  visuals: {
    perceptualMap: {
      xAxis: { label: '', rationale: '' },
      yAxis: { label: '', rationale: '' },
      points: []
    },
    ladder: { category: '', rungs: [], whyDifferentLadder: '' },
    strategyCanvas: {
      factors: [],
      curves: { statusQuo: [], categoryLeader: [], youCurrent: [], youTarget: [] },
      competitorNames: []
    },
    errc: { eliminate: [], reduce: [], raise: [], create: [] }
  },
  tamSamSom: {
    tam: { value: 0, currency: 'USD', formula: '', category: '' },
    sam: { value: 0, currency: 'USD', formula: '', segment: '' },
    som: { value: 0, currency: 'USD', formula: '', reachability: '' },
    assumptions: []
  },
  proofStack: [],
  version: '1.0'
};

// Empty Phase 5 ICP Engine for initialization
export const emptyPhase5: Phase5Data = {
  candidateSegments: [],
  icps: [],
  interICPGraph: {
    nodes: [],
    edges: [],
    primaryWedgeICP: ''
  },
  version: '1.0'
};

// Empty Phase 6 Soundbite Forge for initialization
export const emptyPhase6: Phase6Data = {
  blueprint: {
    controllingIdea: '',
    coreMessage: '',
    pillars: [],
    missingProofAlerts: []
  },
  soundbites: [],
  variants: [],
  realityCheck: {
    competitorChecks: [],
    proofQuality: [],
    awarenessMismatches: [],
    claimsAtRisk: []
  },
  constraints: {
    bannedClaims: [],
    bannedWords: [],
    regulatedFlags: [],
    tonePreference: 'direct'
  },
  version: '1.0'
};

// ==========================================
// Storage & Helpers
// ==========================================

import { supabase } from './supabase';

const STORAGE_KEY = 'rf_brand_kit';
const FOUNDATION_STORAGE_KEY = 'rf_foundation';

export const saveBrandKit = (kit: BrandKit) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(kit));
  }
};

export const getBrandKit = (): BrandKit | null => {
  if (typeof window !== 'undefined') {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  }
  return null;
};

export const saveFoundation = async (data: FoundationData) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(FOUNDATION_STORAGE_KEY, JSON.stringify(data));

    // Sync to Supabase
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        await supabase
          .from('foundation_state')
          .upsert({
            tenant_id: user.id,
            data: data,
            updated_at: new Date().toISOString()
          });
      }
    } catch (err) {
      console.warn('Failed to sync foundation to Supabase', err);
    }

    // Sync minimal data to legacy brand kit
    const legacyKit: BrandKit = {
      brandVoice: data.brandVoice || '',
      positioning: `We are the ${data.positioning.category} for ${data.positioning.targetAudience} who want ${data.positioning.psychologicalOutcome}.`,
      messagingPillars: [data.messaging.beliefPillar, data.messaging.promisePillar, data.messaging.proofPillar].filter(Boolean)
    };
    if (legacyKit.messagingPillars.length === 0) legacyKit.messagingPillars = [''];
    saveBrandKit(legacyKit);
  }
};

export const loadFoundation = (): FoundationData => {
  // This is the sync version for initial mount or legacy
  if (typeof window !== 'undefined') {
    const data = localStorage.getItem(FOUNDATION_STORAGE_KEY);
    if (data) return JSON.parse(data);
  }
  return emptyFoundation;
};

export const loadFoundationDB = async (): Promise<FoundationData> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      const { data, error } = await supabase
        .from('foundation_state')
        .select('data')
        .eq('tenant_id', user.id)
        .single();

      if (data && !error) {
        // Update local cache
        if (typeof window !== 'undefined') {
          localStorage.setItem(FOUNDATION_STORAGE_KEY, JSON.stringify(data.data));
        }
        return data.data as FoundationData;
      }
    }
  } catch (err) {
    console.warn('Failed to load foundation from Supabase', err);
  }
  return loadFoundation();
};

export const ONBOARDING_STEPS = [
  { id: 'business', name: 'Business Basics', description: 'Your core identity' },
  { id: 'confession', name: 'Confession', description: 'Current reality check' },
  { id: 'cohorts', name: 'Cohorts', description: 'Who you serve' },
  { id: 'positioning', name: 'Positioning', description: 'How you win' },
  { id: 'messaging', name: 'Messaging', description: 'What you say' },
  { id: 'review', name: 'Review', description: 'Verify & Launch' },
];

export async function uploadLogo(file: File): Promise<{ url: string; status: string }> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const { data: { user } } = await supabase.auth.getUser();
  const tenantId = user?.id || '00000000-0000-0000-0000-000000000000';

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/v1/assets/upload-logo`, {
    method: 'POST',
    headers: {
      'X-Tenant-ID': tenantId
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload logo');
  }

  return await response.json();
}
