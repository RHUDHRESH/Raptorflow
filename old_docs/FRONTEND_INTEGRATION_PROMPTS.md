# 🚀 RaptorFlow Frontend Integration - 10 Corrected Prompts

> **Updated for actual backend state after merging main branch**
> All prompts now reflect the **world-class backend** with memory, performance prediction, enhanced critic/guardian, semantic intelligence, and meta-learning.

---

## 📋 **Prompt 1: Enhance API Layer with Advanced Features**

### Files & Paths:
```
src/lib/services/backend-api.ts          (enhance existing)
src/types/api.ts                         (create new)
package.json                              (add uuid dependency)
```

### Tasks:

#### 1. Add UUID Dependency
```bash
npm install uuid
npm install --save-dev @types/uuid
```

#### 2. Add Correlation ID Tracking

Update `backend-api.ts`:
```typescript
import { v4 as uuidv4 } from 'uuid';

async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const { data: { session } } = await supabase.auth.getSession();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'X-Correlation-ID': uuidv4(),  // ← ADD THIS
    ...options.headers,
  };

  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }

  const response = await fetch(`${BACKEND_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}
```

#### 3. Add Memory API

Add to `backend-api.ts`:
```typescript
/**
 * Memory API - Advanced memory system integration
 */
export const memoryAPI = {
  /**
   * Store information in workspace memory
   */
  async remember(workspaceId: string, key: string, value: any, metadata?: any) {
    return apiFetch('/memory/remember', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        key,
        value,
        metadata
      })
    });
  },

  /**
   * Recall information from workspace memory
   */
  async recall(workspaceId: string, key: string) {
    return apiFetch(`/memory/recall/${workspaceId}/${key}`);
  },

  /**
   * Semantic search across all memory
   */
  async search(workspaceId: string, query: string, topK: number = 5) {
    const params = new URLSearchParams({
      query,
      top_k: topK.toString()
    });
    return apiFetch(`/memory/search/${workspaceId}?${params}`);
  },

  /**
   * Get full context for a task type
   */
  async getContext(workspaceId: string, taskType: string) {
    return apiFetch(`/memory/context/${workspaceId}/${taskType}`);
  },

  /**
   * Store feedback for agent learning
   */
  async learnFromFeedback(agentName: string, feedback: any, workspaceId: string) {
    return apiFetch('/memory/learn', {
      method: 'POST',
      body: JSON.stringify({
        agent_name: agentName,
        feedback,
        workspace_id: workspaceId
      })
    });
  }
};
```

#### 4. Add Performance Prediction API

Add to `backend-api.ts`:
```typescript
/**
 * Performance Prediction API
 */
export const performanceAPI = {
  /**
   * Predict engagement for content before publishing
   */
  async predictEngagement(data: {
    content: string;
    icp_id: string;
    channel: 'linkedin' | 'twitter' | 'blog' | 'email';
    content_type: 'blog' | 'email' | 'social';
  }) {
    return apiFetch('/analytics/predict/performance', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Score viral potential of content
   */
  async scoreViralPotential(content: string, channel: string) {
    return apiFetch('/analytics/predict/viral', {
      method: 'POST',
      body: JSON.stringify({ content, channel })
    });
  },

  /**
   * Get conversion optimization suggestions
   */
  async optimizeConversion(content: string, goal: string) {
    return apiFetch('/analytics/optimize/conversion', {
      method: 'POST',
      body: JSON.stringify({ content, goal })
    });
  }
};
```

#### 5. Update Cohorts API Endpoint Names

Fix existing `icpAPI` → `cohortsAPI`:
```typescript
/**
 * Cohorts API (formerly ICP API)
 */
export const cohortsAPI = {
  /**
   * Generate a new cohort from business inputs
   */
  async generate(data: {
    businessDescription: string;
    productDescription?: string;
    targetMarket?: string;
    valueProposition?: string;
    topCustomers?: string;
    location?: string;
  }) {
    return apiFetch('/cohorts/generate', {  // Changed from /customer-intelligence/create
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * List all cohorts
   */
  async list() {
    return apiFetch('/cohorts/');  // Changed from /customer-intelligence/list
  },

  /**
   * Get specific cohort
   */
  async get(cohortId: string) {
    return apiFetch(`/cohorts/${cohortId}`);
  },

  /**
   * Compute psychographics for cohort
   */
  async computePsychographics(cohortId: string, cohortData: any) {
    return apiFetch('/cohorts/compute_psychographics', {  // Changed from /enrich
      method: 'POST',
      body: JSON.stringify({ cohort: cohortData })
    });
  },

  /**
   * Delete cohort
   */
  async delete(cohortId: string) {
    return apiFetch(`/cohorts/${cohortId}`, {
      method: 'DELETE'
    });
  }
};
```

#### 6. Create Comprehensive TypeScript Types

Create `src/types/api.ts`:
```typescript
import { UUID } from 'crypto';

// ========== Cohorts / ICP Types ==========

export interface CohortGenerateRequest {
  businessDescription: string;
  productDescription?: string;
  targetMarket?: string;
  valueProposition?: string;
  topCustomers?: string;
  location?: string;
  currentMarketing?: string;
  timeAvailable?: string;
  goals?: string;
}

export interface CohortData {
  name: string;
  executiveSummary: string;
  demographics: {
    companySize?: string;
    industry?: string;
    revenue?: string;
    location?: string;
  };
  buyerRole: string;
  psychographics: {
    values?: string[];
    decisionStyle?: string;
    priorities?: string[];
  };
  painPoints: string[];
  goals: string[];
  behavioralTriggers: string[];
  communication: {
    channels?: string[];
    tone?: string;
    format?: string;
  };
  budget: string;
  timeline: string;
  decisionStructure?: string;
}

export interface Cohort {
  id: string;
  workspace_id: string;
  name: string;
  data: CohortData;
  created_at: string;
  updated_at: string;
}

// ========== Content Types ==========

export interface BlogRequest {
  persona_id: string;
  topic: string;
  goal?: string;
  keywords?: string[];
  tone?: 'professional' | 'conversational' | 'thought_leadership' | 'educational';
  word_count?: number;
  workspace_id: string;
  correlation_id?: string;
}

export interface DimensionScore {
  score: number;
  issues: string[];
  suggestions: string[];
}

export interface ReadabilityScore extends DimensionScore {
  flesch_reading_ease?: number;
  flesch_kincaid_grade?: number;
  gunning_fog?: number;
  grade_level?: string;
}

export interface CriticReview {
  overall_score: number;
  dimensions: {
    clarity: DimensionScore;
    brand_alignment: DimensionScore;
    audience_fit: DimensionScore;
    engagement: DimensionScore;
    factual_accuracy: DimensionScore;
    seo_optimization: DimensionScore;
    readability: ReadabilityScore;
  };
  approval_recommendation: 'approve' | 'approve_with_revisions' | 'reject';
  priority_fixes: string[];
  optional_improvements: string[];
}

export interface CheckResult {
  passed: boolean;
  issues: string[];
  suggestions?: string[];
}

export interface GuardianCheck {
  status: 'approved' | 'flagged' | 'blocked';
  confidence: number;
  checks: {
    legal_compliance: CheckResult;
    brand_safety: CheckResult;
    competitor_mentions?: CheckResult;
    copyright_risk: CheckResult;
    inclusive_language: CheckResult;
    regulatory_compliance?: CheckResult;
  };
  required_actions: string[];
  recommended_actions: string[];
}

export interface Prediction {
  estimated: number;
  range: [number, number];
  confidence: number;
}

export interface PerformancePrediction {
  likes: Prediction;
  shares: Prediction;
  comments: Prediction;
  click_through_rate: Prediction;
  conversion_rate: Prediction;
  engagement_score: number;
  viral_potential: number;
  improvement_suggestions: Array<{
    feature: string;
    current: number;
    target: number;
    action: string;
    expected_lift: string;
  }>;
}

export interface ContentResponse {
  content: string;
  critic_review: CriticReview;
  guardian_check: GuardianCheck;
  performance_prediction?: PerformancePrediction;
  hooks?: Array<{
    text: string;
    style: string;
    score: number;
  }>;
  word_count?: number;
  metadata?: any;
}

// ========== Memory Types ==========

export interface MemoryContext {
  workspace_id: string;
  brand_voice?: {
    formality: number;
    tone: string;
    style_guide: string;
    examples: string[];
  };
  user_preferences?: {
    paragraph_length: string;
    use_emojis: boolean;
    banned_words: string[];
    preferred_formats: string[];
  };
  past_successes?: Array<{
    content_type: string;
    topic: string;
    performance_score: number;
    key_elements: string[];
  }>;
  icp_profiles?: any[];
}

// ========== Strategy & Campaign Types ==========

export interface StrategyRequest {
  goal: string;
  timeframe_days?: number;
  target_cohort_ids?: string[];
  constraints?: Record<string, any>;
}

export interface Campaign {
  id: string;
  name: string;
  goal: string;
  timeframe_days: number;
  target_cohort_ids: string[];
  channels: string[];
  status: 'planning' | 'active' | 'paused' | 'completed';
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'completed';
  due_date?: string;
}

// ========== Analytics Types ==========

export interface AnalyticsResponse {
  metrics: {
    impressions: number;
    clicks: number;
    conversions: number;
    engagement_rate: number;
  };
  insights: string[];
  trends: any[];
}

// Export all
export type {
  UUID,
  // ... all types above
};
```

#### 7. Update exports

At the bottom of `backend-api.ts`:
```typescript
export const backendAPI = {
  onboarding: onboardingAPI,
  cohorts: cohortsAPI,  // Changed from icp
  strategy: strategyAPI,
  campaigns: campaignsAPI,
  content: contentAPI,
  analytics: analyticsAPI,
  integrations: integrationsAPI,
  memory: memoryAPI,        // NEW
  performance: performanceAPI, // NEW
};

export default backendAPI;
```

### Deliverables:
✅ Correlation ID tracking on all requests
✅ Memory API with 5 methods
✅ Performance prediction API
✅ Fixed cohorts endpoint names
✅ Comprehensive TypeScript types
✅ Enhanced content response types

---

## 📋 **Prompt 2: Build Real Onboarding Wizard**

### Files & Paths:
```
src/pages/onboarding/index.tsx           (enhance existing)
src/components/OnboardingQuestion.tsx    (create new)
src/context/OnboardingContext.tsx        (create new)
```

### Tasks:

#### 1. Create Onboarding Context

Create `src/context/OnboardingContext.tsx`:
```typescript
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface OnboardingContextType {
  sessionId: string | null;
  setSessionId: (id: string) => void;
  workspaceId: string | null;
  setWorkspaceId: (id: string) => void;
  icpId: string | null;
  setIcpId: (id: string) => void;
  isComplete: boolean;
  setIsComplete: (complete: boolean) => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

export const OnboardingProvider = ({ children }: { children: ReactNode }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [icpId, setIcpId] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  return (
    <OnboardingContext.Provider value={{
      sessionId, setSessionId,
      workspaceId, setWorkspaceId,
      icpId, setIcpId,
      isComplete, setIsComplete
    }}>
      {children}
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
};
```

#### 2. Create Question Component

Create `src/components/OnboardingQuestion.tsx`:
```typescript
import React from 'react';
import { motion } from 'framer-motion';

interface Question {
  id: string;
  text: string;
  type: 'text' | 'select' | 'multiselect';
  options?: string[];
}

interface Props {
  question: Question;
  answer: any;
  onAnswer: (answer: any) => void;
  onNext: () => void;
}

export const OnboardingQuestion = ({ question, answer, onAnswer, onNext }: Props) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="w-full max-w-2xl mx-auto p-8"
    >
      <form onSubmit={handleSubmit}>
        <h2 className="text-2xl font-bold mb-4">{question.text}</h2>

        {question.type === 'text' && (
          <textarea
            value={answer || ''}
            onChange={(e) => onAnswer(e.target.value)}
            className="w-full p-4 border rounded-lg min-h-32"
            placeholder="Your answer..."
            required
          />
        )}

        {question.type === 'select' && (
          <select
            value={answer || ''}
            onChange={(e) => onAnswer(e.target.value)}
            className="w-full p-4 border rounded-lg"
            required
          >
            <option value="">Select an option...</option>
            {question.options?.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        )}

        {question.type === 'multiselect' && (
          <div className="space-y-2">
            {question.options?.map(opt => (
              <label key={opt} className="flex items-center gap-2 p-3 border rounded hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={answer?.includes(opt) || false}
                  onChange={(e) => {
                    const current = answer || [];
                    if (e.target.checked) {
                      onAnswer([...current, opt]);
                    } else {
                      onAnswer(current.filter((v: string) => v !== opt));
                    }
                  }}
                />
                {opt}
              </label>
            ))}
          </div>
        )}

        <button
          type="submit"
          className="mt-6 px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          disabled={!answer}
        >
          Continue →
        </button>
      </form>
    </motion.div>
  );
};
```

#### 3. Build Dynamic Wizard

Update `src/pages/onboarding/index.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { backendAPI } from '../lib/services/backend-api';
import { useOnboarding } from '../context/OnboardingContext';
import { OnboardingQuestion } from '../components/OnboardingQuestion';

export default function OnboardingWizard() {
  const navigate = useNavigate();
  const { sessionId, setSessionId, setWorkspaceId, setIcpId, setIsComplete } = useOnboarding();

  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [icpSummary, setIcpSummary] = useState<any>(null);

  // Start session on mount
  useEffect(() => {
    async function startSession() {
      try {
        const response = await backendAPI.onboarding.startSession();
        setSessionId(response.session_id);
        setQuestions(response.questions || []);
      } catch (error) {
        console.error('Failed to start onboarding:', error);
      } finally {
        setLoading(false);
      }
    }
    startSession();
  }, []);

  // Handle answer submission
  const handleAnswer = (answer: any) => {
    const questionId = questions[currentIndex].id;
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  // Move to next question or finish
  const handleNext = async () => {
    if (!sessionId) return;

    const questionId = questions[currentIndex].id;
    const answer = answers[questionId];

    try {
      // Submit answer to backend
      await backendAPI.onboarding.submitAnswer(sessionId, questionId, answer);

      // Check if last question
      if (currentIndex === questions.length - 1) {
        // Fetch ICP summary
        const profile = await backendAPI.onboarding.getProfile(sessionId);
        setIcpSummary(profile);
        setWorkspaceId(profile.workspace_id);
        setIcpId(profile.icp_id);
        setIsComplete(true);
      } else {
        // Move to next question
        setCurrentIndex(prev => prev + 1);
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  if (icpSummary) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold mb-4">✅ Profile Created!</h1>

          <div className="space-y-4">
            <div>
              <h3 className="font-semibold">ICP Name:</h3>
              <p>{icpSummary.icp_name}</p>
            </div>

            <div>
              <h3 className="font-semibold">Executive Summary:</h3>
              <p>{icpSummary.executive_summary}</p>
            </div>

            <div>
              <h3 className="font-semibold">Top Pain Points:</h3>
              <ul className="list-disc pl-5">
                {icpSummary.pain_points?.map((point: string, i: number) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-semibold">Suggested Primary Channel:</h3>
              <p>{icpSummary.primary_channel}</p>
            </div>
          </div>

          <button
            onClick={() => navigate('/dashboard')}
            className="mt-6 px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go to Dashboard →
          </button>
        </div>
      </div>
    );
  }

  // Progress bar
  const progress = ((currentIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-600">Question {currentIndex + 1} of {questions.length}</span>
            <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <OnboardingQuestion
          question={questions[currentIndex]}
          answer={answers[questions[currentIndex].id]}
          onAnswer={handleAnswer}
          onNext={handleNext}
        />
      </div>
    </div>
  );
}
```

### Deliverables:
✅ Dynamic question flow from backend
✅ Progress bar
✅ ICP summary display
✅ Context storage for workspace/ICP IDs

---

## 📋 **Prompt 3: Build Cohorts Dashboard**

### Files & Paths:
```
src/pages/cohorts/index.tsx              (create new)
src/pages/cohorts/[cohortId].tsx         (create new)
src/components/CohortCard.tsx            (create new)
src/components/TagSelector.tsx           (create new)
```

### Tasks:

#### 1. Create Cohort List Page

Create `src/pages/cohorts/index.tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { backendAPI } from '../../lib/services/backend-api';
import { CohortCard } from '../../components/CohortCard';
import type { Cohort } from '../../types/api';

export default function CohortsPage() {
  const navigate = useNavigate();
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCohorts() {
      try {
        const data = await backendAPI.cohorts.list();
        setCohorts(data);
      } catch (error) {
        console.error('Failed to load cohorts:', error);
      } finally {
        setLoading(false);
      }
    }
    loadCohorts();
  }, []);

  if (loading) {
    return <div className="p-8">Loading cohorts...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Your Cohorts</h1>
        <button
          onClick={() => navigate('/onboarding')}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Create New ICP
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cohorts.map(cohort => (
          <CohortCard
            key={cohort.id}
            cohort={cohort}
            onClick={() => navigate(`/cohorts/${cohort.id}`)}
          />
        ))}
      </div>

      {cohorts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No cohorts yet</p>
          <button
            onClick={() => navigate('/onboarding')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg"
          >
            Create Your First ICP
          </button>
        </div>
      )}
    </div>
  );
}
```

#### 2. Create Cohort Card Component

Create `src/components/CohortCard.tsx`:
```typescript
import React from 'react';
import type { Cohort } from '../types/api';

interface Props {
  cohort: Cohort;
  onClick: () => void;
}

export const CohortCard = ({ cohort, onClick }: Props) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <h3 className="text-xl font-bold mb-2">{cohort.name}</h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {cohort.data.executiveSummary}
      </p>

      <div className="space-y-2 text-sm">
        <div>
          <span className="font-semibold">Industry:</span>{' '}
          {cohort.data.demographics.industry}
        </div>
        <div>
          <span className="font-semibold">Company Size:</span>{' '}
          {cohort.data.demographics.companySize}
        </div>
        <div>
          <span className="font-semibold">Buyer Role:</span>{' '}
          {cohort.data.buyerRole}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {cohort.data.painPoints?.slice(0, 2).map((point, i) => (
          <span key={i} className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
            {point.substring(0, 20)}...
          </span>
        ))}
      </div>
    </div>
  );
};
```

#### 3. Create Cohort Detail Page

Create `src/pages/cohorts/[cohortId].tsx`:
```typescript
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { backendAPI } from '../../lib/services/backend-api';
import { TagSelector } from '../../components/TagSelector';
import type { Cohort } from '../../types/api';

export default function CohortDetailPage() {
  const { cohortId } = useParams();
  const navigate = useNavigate();
  const [cohort, setCohort] = useState<Cohort | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCohort() {
      if (!cohortId) return;
      try {
        const data = await backendAPI.cohorts.get(cohortId);
        setCohort(data);
      } catch (error) {
        console.error('Failed to load cohort:', error);
      } finally {
        setLoading(false);
      }
    }
    loadCohort();
  }, [cohortId]);

  const handleEnrichWithTags = async (selectedTags: string[]) => {
    if (!cohort) return;
    try {
      const enriched = await backendAPI.cohorts.computePsychographics(
        cohort.id,
        { ...cohort.data, tags: selectedTags }
      );
      setCohort(enriched);
    } catch (error) {
      console.error('Failed to enrich cohort:', error);
    }
  };

  const handleSetActive = () => {
    // Store active ICP in context or localStorage
    localStorage.setItem('activeIcpId', cohort!.id);
    alert('Set as active ICP!');
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!cohort) {
    return <div className="p-8">Cohort not found</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <button
        onClick={() => navigate('/cohorts')}
        className="mb-4 text-blue-600 hover:underline"
      >
        ← Back to Cohorts
      </button>

      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold">{cohort.name}</h1>
          <p className="text-gray-600 mt-2">{cohort.data.executiveSummary}</p>
        </div>
        <button
          onClick={handleSetActive}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Set as Active ICP
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Demographics */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Demographics</h2>
          <table className="w-full">
            <tbody className="divide-y">
              <tr>
                <td className="py-2 font-semibold">Company Size</td>
                <td className="py-2">{cohort.data.demographics.companySize}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Industry</td>
                <td className="py-2">{cohort.data.demographics.industry}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Revenue</td>
                <td className="py-2">{cohort.data.demographics.revenue}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Location</td>
                <td className="py-2">{cohort.data.demographics.location}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Buyer Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Buyer Information</h2>
          <table className="w-full">
            <tbody className="divide-y">
              <tr>
                <td className="py-2 font-semibold">Role</td>
                <td className="py-2">{cohort.data.buyerRole}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Budget</td>
                <td className="py-2">{cohort.data.budget}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Timeline</td>
                <td className="py-2">{cohort.data.timeline}</td>
              </tr>
              <tr>
                <td className="py-2 font-semibold">Decision Structure</td>
                <td className="py-2">{cohort.data.decisionStructure}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Psychographics */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Psychographics</h2>
        <div className="space-y-4">
          <div>
            <span className="font-semibold">Values:</span>{' '}
            <div className="flex flex-wrap gap-2 mt-2">
              {cohort.data.psychographics.values?.map((v, i) => (
                <span key={i} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
                  {v}
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="font-semibold">Decision Style:</span>{' '}
            {cohort.data.psychographics.decisionStyle}
          </div>
          <div>
            <span className="font-semibold">Priorities:</span>{' '}
            <div className="flex flex-wrap gap-2 mt-2">
              {cohort.data.psychographics.priorities?.map((p, i) => (
                <span key={i} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                  {p}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Pain Points */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Pain Points</h2>
        <ul className="space-y-2">
          {cohort.data.painPoints.map((point, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-red-500 mt-1">●</span>
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Goals */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Goals</h2>
        <ul className="space-y-2">
          {cohort.data.goals.map((goal, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-green-500 mt-1">●</span>
              <span>{goal}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Tag Selector */}
      <TagSelector onSelectTags={handleEnrichWithTags} />
    </div>
  );
}
```

#### 4. Create Tag Selector Component

Create `src/components/TagSelector.tsx`:
```typescript
import React, { useState } from 'react';

const AVAILABLE_TAGS = [
  // From backend/models/persona.py tag taxonomy
  'Early adopter', 'Risk-averse', 'Data-driven', 'ROI-focused',
  'Innovation-seeking', 'Cost-sensitive', 'Quality-driven',
  'Community-driven', 'Independent', 'Visual learner',
  // ... add all 50+ tags from backend
];

interface Props {
  onSelectTags: (tags: string[]) => void;
}

export const TagSelector = ({ onSelectTags }: Props) => {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  const handleToggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleApply = () => {
    onSelectTags(selectedTags);
    setIsOpen(false);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Enrich with Tags</h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          {isOpen ? 'Close' : 'Add Tags'}
        </button>
      </div>

      {isOpen && (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4 max-h-64 overflow-y-auto">
            {AVAILABLE_TAGS.map(tag => (
              <label
                key={tag}
                className={`
                  flex items-center gap-2 p-2 border rounded cursor-pointer transition-colors
                  ${selectedTags.includes(tag) ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50'}
                `}
              >
                <input
                  type="checkbox"
                  checked={selectedTags.includes(tag)}
                  onChange={() => handleToggleTag(tag)}
                  className="rounded"
                />
                <span className="text-sm">{tag}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleApply}
            disabled={selectedTags.length === 0}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            Apply {selectedTags.length} Tags
          </button>
        </div>
      )}

      {selectedTags.length > 0 && !isOpen && (
        <div className="flex flex-wrap gap-2">
          {selectedTags.map(tag => (
            <span key={tag} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
```

### Deliverables:
✅ Cohort list page with cards
✅ Cohort detail page with full data
✅ Tag selector with 50+ options
✅ Active ICP selection

---

## 📋 **Prompt 4: Memory & Brand Voice Console**

### Files & Paths:
```
src/pages/memory/index.tsx                  (create new)
src/pages/memory/brand-voice.tsx            (create new)
src/components/MemorySearchPanel.tsx        (create new)
src/components/BrandVoiceEditor.tsx         (create new)
```

### Tasks:

#### 1. Create Memory Console Page

Create `src/pages/memory/index.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';
import MemorySearchPanel from '@/components/MemorySearchPanel';

interface MemoryEntry {
  key: string;
  value: any;
  memory_type: string;
  created_at: string;
  updated_at: string;
}

export default function MemoryConsolePage() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [workspaceId, setWorkspaceId] = useState<string>('');

  useEffect(() => {
    fetchMemories();
  }, []);

  const fetchMemories = async () => {
    try {
      setLoading(true);
      const data = await backendAPI.memory.list(workspaceId);
      setMemories(data.memories);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemember = async (key: string, value: any, metadata?: any) => {
    try {
      await backendAPI.memory.remember(workspaceId, key, value, metadata);
      fetchMemories(); // Refresh list
    } catch (error) {
      console.error('Failed to store memory:', error);
    }
  };

  const handleForget = async (key: string) => {
    try {
      await backendAPI.memory.forget(workspaceId, key);
      fetchMemories(); // Refresh list
    } catch (error) {
      console.error('Failed to forget memory:', error);
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Memory Console</h1>
        <button
          onClick={fetchMemories}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Semantic Search Panel */}
      <MemorySearchPanel workspaceId={workspaceId} />

      {/* Memory Entries Grid */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading memories...</p>
          </div>
        ) : memories.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-600">No memories stored yet</p>
          </div>
        ) : (
          memories.map((memory) => (
            <div key={memory.key} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-semibold text-lg">{memory.key}</h3>
                  <span className="text-xs text-gray-500 uppercase">{memory.memory_type}</span>
                </div>
                <button
                  onClick={() => handleForget(memory.key)}
                  className="text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </div>

              <pre className="text-sm bg-gray-50 p-4 rounded overflow-auto max-h-40">
                {JSON.stringify(memory.value, null, 2)}
              </pre>

              <div className="mt-4 text-xs text-gray-500">
                <p>Created: {new Date(memory.created_at).toLocaleDateString()}</p>
                <p>Updated: {new Date(memory.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

#### 2. Create Memory Search Panel

Create `src/components/MemorySearchPanel.tsx`:
```typescript
import React, { useState } from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface SemanticResult {
  key: string;
  value: any;
  similarity_score: number;
  memory_type: string;
}

export default function MemorySearchPanel({ workspaceId }: { workspaceId: string }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SemanticResult[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      setSearching(true);
      const data = await backendAPI.memory.search(workspaceId, query, 10);
      setResults(data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">🔍 Semantic Memory Search</h2>

      <div className="flex gap-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search memories semantically (e.g., 'brand values' or 'customer pain points')..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          onClick={handleSearch}
          disabled={searching || !query.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="font-semibold text-gray-700">Results ({results.length})</h3>
          {results.map((result, idx) => (
            <div key={idx} className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <span className="font-medium">{result.key}</span>
                <span className="text-sm text-gray-500">
                  {(result.similarity_score * 100).toFixed(1)}% match
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <span className="px-2 py-1 bg-gray-100 rounded text-xs mr-2">
                  {result.memory_type}
                </span>
                <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-auto max-h-20">
                  {JSON.stringify(result.value, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### 3. Create Brand Voice Editor

Create `src/pages/memory/brand-voice.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface BrandVoice {
  tone: string[];
  vocabulary: string[];
  forbidden_words: string[];
  sentence_structure: string;
  formality_level: number; // 1-10
  humor_level: number; // 1-10
  examples: string[];
}

export default function BrandVoicePage() {
  const [workspaceId, setWorkspaceId] = useState<string>('');
  const [brandVoice, setBrandVoice] = useState<BrandVoice>({
    tone: [],
    vocabulary: [],
    forbidden_words: [],
    sentence_structure: '',
    formality_level: 5,
    humor_level: 5,
    examples: [],
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadBrandVoice();
  }, []);

  const loadBrandVoice = async () => {
    try {
      const data = await backendAPI.memory.recall(workspaceId, 'brand_voice');
      if (data.value) {
        setBrandVoice(data.value);
      }
    } catch (error) {
      console.error('Failed to load brand voice:', error);
    }
  };

  const saveBrandVoice = async () => {
    try {
      setSaving(true);
      await backendAPI.memory.remember(
        workspaceId,
        'brand_voice',
        brandVoice,
        { type: 'brand_configuration', updated_by: 'user' }
      );
      alert('Brand voice saved successfully!');
    } catch (error) {
      console.error('Failed to save brand voice:', error);
      alert('Failed to save brand voice');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container mx-auto px-6 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">🎨 Brand Voice Configuration</h1>

      <div className="space-y-8">
        {/* Tone Selection */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Tone & Personality</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tone Keywords</label>
              <input
                type="text"
                placeholder="professional, friendly, authoritative..."
                value={brandVoice.tone.join(', ')}
                onChange={(e) => setBrandVoice({
                  ...brandVoice,
                  tone: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Formality Level: {brandVoice.formality_level}/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={brandVoice.formality_level}
                  onChange={(e) => setBrandVoice({
                    ...brandVoice,
                    formality_level: parseInt(e.target.value)
                  })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Casual</span>
                  <span>Formal</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Humor Level: {brandVoice.humor_level}/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={brandVoice.humor_level}
                  onChange={(e) => setBrandVoice({
                    ...brandVoice,
                    humor_level: parseInt(e.target.value)
                  })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Serious</span>
                  <span>Playful</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Vocabulary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Vocabulary</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Preferred Words</label>
              <textarea
                placeholder="One word per line..."
                value={brandVoice.vocabulary.join('\n')}
                onChange={(e) => setBrandVoice({
                  ...brandVoice,
                  vocabulary: e.target.value.split('\n').filter(Boolean)
                })}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Forbidden Words</label>
              <textarea
                placeholder="One word per line..."
                value={brandVoice.forbidden_words.join('\n')}
                onChange={(e) => setBrandVoice({
                  ...brandVoice,
                  forbidden_words: e.target.value.split('\n').filter(Boolean)
                })}
                rows={6}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        </div>

        {/* Examples */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Example Content</h2>
          <p className="text-sm text-gray-600 mb-4">
            Provide examples of content that matches your brand voice
          </p>
          {brandVoice.examples.map((example, idx) => (
            <div key={idx} className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium">Example {idx + 1}</label>
                <button
                  onClick={() => setBrandVoice({
                    ...brandVoice,
                    examples: brandVoice.examples.filter((_, i) => i !== idx)
                  })}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>
              <textarea
                value={example}
                onChange={(e) => {
                  const newExamples = [...brandVoice.examples];
                  newExamples[idx] = e.target.value;
                  setBrandVoice({ ...brandVoice, examples: newExamples });
                }}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          ))}
          <button
            onClick={() => setBrandVoice({
              ...brandVoice,
              examples: [...brandVoice.examples, '']
            })}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            + Add Example
          </button>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={saveBrandVoice}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Brand Voice'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Deliverables:
✅ Memory console with list/search/delete
✅ Semantic search panel with similarity scores
✅ Brand voice configuration editor
✅ Memory persistence to backend

---

## 📋 **Prompt 5: Content Generation Pages (Blog, Email, Social)**

### Files & Paths:
```
src/pages/content/blog.tsx                  (create new)
src/pages/content/email.tsx                 (create new)
src/pages/content/social.tsx                (create new)
src/components/ContentGenerator.tsx         (create new)
src/components/CriticReviewPanel.tsx        (create new)
src/components/GuardianCheckPanel.tsx       (create new)
src/components/PerformancePredictionPanel.tsx (create new)
```

### Tasks:

#### 1. Create Blog Generation Page

Create `src/pages/content/blog.tsx`:
```typescript
import React, { useState } from 'react';
import { backendAPI } from '@/lib/services/backend-api';
import CriticReviewPanel from '@/components/CriticReviewPanel';
import GuardianCheckPanel from '@/components/GuardianCheckPanel';
import PerformancePredictionPanel from '@/components/PerformancePredictionPanel';

export default function BlogGeneratorPage() {
  const [topic, setTopic] = useState('');
  const [keywords, setKeywords] = useState<string[]>([]);
  const [tone, setTone] = useState('professional');
  const [personaId, setPersonaId] = useState('');

  const [generating, setGenerating] = useState(false);
  const [content, setContent] = useState<any>(null);
  const [criticReview, setCriticReview] = useState<any>(null);
  const [guardianCheck, setGuardianCheck] = useState<any>(null);
  const [performancePrediction, setPerformancePrediction] = useState<any>(null);

  const handleGenerate = async () => {
    try {
      setGenerating(true);

      // Step 1: Generate blog content
      const blogData = await backendAPI.content.generateBlog({
        persona_id: personaId,
        topic,
        keywords,
        tone,
      });
      setContent(blogData);

      // Step 2: Get Critic review
      const review = await backendAPI.content.reviewContent(blogData.content_id);
      setCriticReview(review);

      // Step 3: Get Guardian compliance check
      const guardianData = await backendAPI.content.guardianCheck(blogData.content_id);
      setGuardianCheck(guardianData);

      // Step 4: Get performance prediction
      const prediction = await backendAPI.performance.predictEngagement({
        content: blogData.content,
        icp_id: personaId,
        channel: 'blog',
        content_type: 'blog',
      });
      setPerformancePrediction(prediction);

    } catch (error) {
      console.error('Failed to generate blog:', error);
      alert('Failed to generate blog. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async () => {
    if (!content) return;

    try {
      await backendAPI.content.approveContent(content.content_id, true);
      alert('Content approved and ready for publishing!');
    } catch (error) {
      console.error('Failed to approve content:', error);
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">📝 Blog Generator</h1>

      {/* Input Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., 'The Future of AI in Marketing'"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Keywords (comma-separated)</label>
            <input
              type="text"
              value={keywords.join(', ')}
              onChange={(e) => setKeywords(e.target.value.split(',').map(k => k.trim()))}
              placeholder="AI, marketing automation, ROI"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="authoritative">Authoritative</option>
              <option value="friendly">Friendly</option>
              <option value="educational">Educational</option>
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={generating || !topic || !personaId}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? 'Generating... (This may take 30-60 seconds)' : 'Generate Blog Post'}
          </button>
        </div>
      </div>

      {/* Generated Content */}
      {content && (
        <div className="space-y-6">
          {/* Blog Preview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-4">{content.title}</h2>
            <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: content.content }} />
          </div>

          {/* Critic Review Panel */}
          {criticReview && <CriticReviewPanel review={criticReview} />}

          {/* Guardian Check Panel */}
          {guardianCheck && <GuardianCheckPanel check={guardianCheck} />}

          {/* Performance Prediction Panel */}
          {performancePrediction && <PerformancePredictionPanel prediction={performancePrediction} />}

          {/* Approval Actions */}
          <div className="flex justify-end gap-4">
            <button
              onClick={() => {
                setContent(null);
                setCriticReview(null);
                setGuardianCheck(null);
                setPerformancePrediction(null);
              }}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Discard
            </button>
            <button
              onClick={handleGenerate}
              className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Regenerate
            </button>
            <button
              onClick={handleApprove}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Approve & Publish
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 2. Create Critic Review Panel

Create `src/components/CriticReviewPanel.tsx`:
```typescript
import React from 'react';
import { CriticReview, DimensionScore } from '@/types/api';

interface Props {
  review: CriticReview;
}

const ScoreBadge = ({ score }: { score: number }) => {
  const color = score >= 8 ? 'green' : score >= 6 ? 'yellow' : 'red';
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold bg-${color}-100 text-${color}-700`}>
      {score}/10
    </span>
  );
};

const DimensionCard = ({ name, dimension }: { name: string; dimension: DimensionScore }) => (
  <div className="bg-gray-50 rounded-lg p-4">
    <div className="flex justify-between items-center mb-2">
      <h4 className="font-medium">{name}</h4>
      <ScoreBadge score={dimension.score} />
    </div>
    <p className="text-sm text-gray-600">{dimension.feedback}</p>
    {dimension.suggestions && dimension.suggestions.length > 0 && (
      <ul className="mt-2 text-sm text-gray-700 space-y-1">
        {dimension.suggestions.map((suggestion, idx) => (
          <li key={idx}>• {suggestion}</li>
        ))}
      </ul>
    )}
  </div>
);

export default function CriticReviewPanel({ review }: Props) {
  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'approve': return 'green';
      case 'approve_with_revisions': return 'yellow';
      case 'reject': return 'red';
      default: return 'gray';
    }
  };

  const color = getRecommendationColor(review.approval_recommendation);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">🔍 Critic Agent Review</h3>
        <div className="flex items-center gap-4">
          <span className="text-2xl font-bold">{review.overall_score}/10</span>
          <span className={`px-4 py-2 rounded-lg bg-${color}-100 text-${color}-700 font-semibold`}>
            {review.approval_recommendation.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Priority Fixes */}
      {review.priority_fixes && review.priority_fixes.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="font-semibold text-red-800 mb-2">⚠️ Priority Fixes Required</h4>
          <ul className="space-y-1">
            {review.priority_fixes.map((fix, idx) => (
              <li key={idx} className="text-sm text-red-700">• {fix}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Dimension Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DimensionCard name="Clarity" dimension={review.dimensions.clarity} />
        <DimensionCard name="Brand Alignment" dimension={review.dimensions.brand_alignment} />
        <DimensionCard name="Audience Fit" dimension={review.dimensions.audience_fit} />
        <DimensionCard name="Engagement Potential" dimension={review.dimensions.engagement} />
        <DimensionCard name="Factual Accuracy" dimension={review.dimensions.factual_accuracy} />
        <DimensionCard name="SEO Optimization" dimension={review.dimensions.seo_optimization} />
      </div>

      {/* Readability */}
      <div className="mt-4 bg-blue-50 rounded-lg p-4">
        <h4 className="font-medium mb-2">📖 Readability Analysis</h4>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Flesch-Kincaid:</span>
            <span className="ml-2 font-semibold">{review.dimensions.readability.flesch_kincaid_grade}</span>
          </div>
          <div>
            <span className="text-gray-600">Reading Time:</span>
            <span className="ml-2 font-semibold">{review.dimensions.readability.estimated_reading_time} min</span>
          </div>
          <div>
            <span className="text-gray-600">Sentence Avg:</span>
            <span className="ml-2 font-semibold">{review.dimensions.readability.average_sentence_length} words</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

#### 3. Create Guardian Check Panel

Create `src/components/GuardianCheckPanel.tsx`:
```typescript
import React from 'react';
import { GuardianCheck, CheckResult } from '@/types/api';

interface Props {
  check: GuardianCheck;
}

const CheckResultCard = ({ name, result }: { name: string; result: CheckResult }) => {
  const statusColor = result.status === 'passed' ? 'green' : result.status === 'warning' ? 'yellow' : 'red';

  return (
    <div className={`bg-${statusColor}-50 border border-${statusColor}-200 rounded-lg p-4`}>
      <div className="flex justify-between items-center mb-2">
        <h4 className="font-medium">{name}</h4>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-${statusColor}-100 text-${statusColor}-700`}>
          {result.status.toUpperCase()}
        </span>
      </div>
      <p className="text-sm text-gray-700">{result.message}</p>
      {result.issues && result.issues.length > 0 && (
        <ul className="mt-2 space-y-1">
          {result.issues.map((issue, idx) => (
            <li key={idx} className="text-sm text-gray-600">⚠️ {issue}</li>
          ))}
        </ul>
      )}
      <div className="mt-2 text-xs text-gray-500">
        Confidence: {(result.confidence * 100).toFixed(1)}%
      </div>
    </div>
  );
};

export default function GuardianCheckPanel({ check }: Props) {
  const overallColor = check.status === 'approved' ? 'green' : check.status === 'flagged' ? 'yellow' : 'red';

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">🛡️ Guardian Compliance Check</h3>
        <span className={`px-4 py-2 rounded-lg bg-${overallColor}-100 text-${overallColor}-700 font-semibold`}>
          {check.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CheckResultCard name="Legal Compliance" result={check.checks.legal_compliance} />
        <CheckResultCard name="Brand Safety" result={check.checks.brand_safety} />
        <CheckResultCard name="Copyright Risk" result={check.checks.copyright_risk} />
        <CheckResultCard name="Inclusive Language" result={check.checks.inclusive_language} />
      </div>

      {check.status === 'blocked' && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="font-semibold text-red-800">
            ⛔ Content blocked: Critical compliance issues detected. Please review and revise.
          </p>
        </div>
      )}
    </div>
  );
}
```

#### 4. Create Performance Prediction Panel

Create `src/components/PerformancePredictionPanel.tsx`:
```typescript
import React from 'react';
import { PerformancePrediction, Prediction } from '@/types/api';

interface Props {
  prediction: PerformancePrediction;
}

const MetricCard = ({ name, prediction }: { name: string; prediction: Prediction }) => (
  <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4">
    <h4 className="text-sm text-gray-600 mb-1">{name}</h4>
    <div className="text-2xl font-bold mb-2">{prediction.predicted_value}</div>
    <div className="text-xs text-gray-500">
      Range: {prediction.confidence_interval.lower} - {prediction.confidence_interval.upper}
      <br />
      Confidence: {(prediction.confidence * 100).toFixed(0)}%
    </div>
  </div>
);

export default function PerformancePredictionPanel({ prediction }: Props) {
  const engagementColor = prediction.engagement_score >= 80 ? 'green' :
                          prediction.engagement_score >= 60 ? 'blue' :
                          prediction.engagement_score >= 40 ? 'yellow' : 'red';

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold">📊 Performance Prediction (AI)</h3>
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-500">Engagement Score</div>
            <div className={`text-3xl font-bold text-${engagementColor}-600`}>
              {prediction.engagement_score}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Viral Potential</div>
            <div className="text-3xl font-bold text-purple-600">
              {prediction.viral_potential}%
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <MetricCard name="👍 Likes" prediction={prediction.likes} />
        <MetricCard name="🔄 Shares" prediction={prediction.shares} />
        <MetricCard name="💬 Comments" prediction={prediction.comments} />
        <MetricCard name="🔗 CTR" prediction={prediction.click_through_rate} />
        <MetricCard name="✅ Conversion" prediction={prediction.conversion_rate} />
      </div>

      {/* Best Time to Post */}
      {prediction.optimal_posting_time && (
        <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
          <h4 className="font-semibold mb-2">⏰ Optimal Posting Time</h4>
          <p className="text-sm">
            Best time to post: <strong>{prediction.optimal_posting_time.day_of_week}</strong> at{' '}
            <strong>{prediction.optimal_posting_time.hour}:00</strong>
          </p>
          <p className="text-xs text-gray-600 mt-1">
            Expected {prediction.optimal_posting_time.expected_boost}% boost in engagement
          </p>
        </div>
      )}
    </div>
  );
}
```

### Deliverables:
✅ Blog, email, and social content generators
✅ Critic review panel with 7 dimensions
✅ Guardian compliance panel with 6 checks
✅ Performance prediction panel with metrics
✅ Approve/reject workflow

---

## 📋 **Prompt 6: Strategy & Campaign Interfaces**

### Files & Paths:
```
src/pages/strategy/index.tsx                (create new)
src/pages/strategy/[strategyId].tsx         (create new)
src/pages/campaigns/index.tsx               (create new)
src/pages/campaigns/[campaignId].tsx        (create new)
src/components/ADAPTFrameworkVisual.tsx     (create new)
src/components/TaskChecklist.tsx            (create new)
```

### Tasks:

#### 1. Create Strategy List Page

Create `src/pages/strategy/index.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { backendAPI } from '@/lib/services/backend-api';

export default function StrategyListPage() {
  const [strategies, setStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const data = await backendAPI.strategy.listStrategies();
      setStrategies(data.strategies);
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">🎯 Marketing Strategies</h1>
        <Link
          to="/strategy/create"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + New Strategy
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : strategies.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-600">No strategies yet. Create your first one!</p>
          </div>
        ) : (
          strategies.map((strategy) => (
            <Link
              key={strategy.strategy_id}
              to={`/strategy/${strategy.strategy_id}`}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <h3 className="font-semibold text-lg mb-2">{strategy.goal}</h3>
              <p className="text-sm text-gray-600 mb-4">
                {strategy.timeframe_days} days • {strategy.moves?.length || 0} moves
              </p>
              <div className="flex flex-wrap gap-2">
                {strategy.target_cohorts?.slice(0, 3).map((cohort: any) => (
                  <span key={cohort.id} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {cohort.nickname}
                  </span>
                ))}
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
```

#### 2. Create ADAPT Framework Visual

Create `src/components/ADAPTFrameworkVisual.tsx`:
```typescript
import React from 'react';

interface Move {
  move_number: number;
  move_name: string;
  objective: string;
  tactics: string[];
  channels: string[];
  duration_days: number;
  success_metrics: any;
}

interface Props {
  moves: Move[];
}

export default function ADAPTFrameworkVisual({ moves }: Props) {
  const phases = [
    { name: 'Awareness', color: 'blue', icon: '👁️' },
    { name: 'Desire', color: 'purple', icon: '❤️' },
    { name: 'Action', color: 'green', icon: '⚡' },
    { name: 'Persistence', color: 'orange', icon: '🔄' },
    { name: 'Trust', color: 'red', icon: '🤝' },
  ];

  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-8">
      <h2 className="text-2xl font-bold mb-6 text-center">🎯 ADAPT Framework</h2>

      <div className="space-y-6">
        {phases.map((phase, phaseIdx) => {
          const phaseMoves = moves.filter(m => {
            const moveName = m.move_name.toLowerCase();
            return moveName.includes(phase.name.toLowerCase());
          });

          return (
            <div key={phase.name} className="relative">
              {/* Phase Header */}
              <div className={`flex items-center gap-4 mb-4 p-4 bg-${phase.color}-100 rounded-lg`}>
                <span className="text-3xl">{phase.icon}</span>
                <div>
                  <h3 className="text-xl font-bold">{phase.name}</h3>
                  <p className="text-sm text-gray-600">{phaseMoves.length} moves</p>
                </div>
              </div>

              {/* Moves */}
              <div className="ml-12 space-y-3">
                {phaseMoves.map((move) => (
                  <div key={move.move_number} className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="text-xs text-gray-500">Move {move.move_number}</span>
                        <h4 className="font-semibold">{move.move_name}</h4>
                      </div>
                      <span className="text-xs text-gray-500">{move.duration_days} days</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{move.objective}</p>
                    <div className="flex flex-wrap gap-2">
                      {move.channels.map((channel) => (
                        <span key={channel} className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {channel}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Connector Line */}
              {phaseIdx < phases.length - 1 && (
                <div className="absolute left-6 top-full h-6 w-0.5 bg-gray-300"></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

#### 3. Create Task Checklist Component

Create `src/components/TaskChecklist.tsx`:
```typescript
import React from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface Task {
  task_id: string;
  task_name: string;
  task_type: string;
  status: 'pending' | 'in_progress' | 'completed';
  due_date: string;
  assigned_agent?: string;
}

interface Props {
  moveId: string;
  tasks: Task[];
  onTaskComplete: (taskId: string) => void;
}

export default function TaskChecklist({ moveId, tasks, onTaskComplete }: Props) {
  const [completing, setCompleting] = useState<string | null>(null);

  const handleComplete = async (taskId: string) => {
    try {
      setCompleting(taskId);
      await backendAPI.campaigns.completeTask(moveId, taskId);
      onTaskComplete(taskId);
    } catch (error) {
      console.error('Failed to complete task:', error);
    } finally {
      setCompleting(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'in_progress': return 'blue';
      default: return 'gray';
    }
  };

  const todayTasks = tasks.filter(t => {
    const dueDate = new Date(t.due_date);
    const today = new Date();
    return dueDate.toDateString() === today.toDateString();
  });

  const upcomingTasks = tasks.filter(t => {
    const dueDate = new Date(t.due_date);
    const today = new Date();
    return dueDate > today;
  });

  return (
    <div className="space-y-6">
      {/* Today's Tasks */}
      <div>
        <h3 className="text-xl font-bold mb-4">📅 Today's Tasks ({todayTasks.length})</h3>
        <div className="space-y-3">
          {todayTasks.map((task) => (
            <div key={task.task_id} className="bg-white rounded-lg p-4 shadow-sm flex items-center gap-4">
              <input
                type="checkbox"
                checked={task.status === 'completed'}
                onChange={() => handleComplete(task.task_id)}
                disabled={completing === task.task_id}
                className="w-5 h-5"
              />
              <div className="flex-1">
                <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-400' : ''}`}>
                  {task.task_name}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-2 py-1 rounded bg-${getStatusColor(task.status)}-100 text-${getStatusColor(task.status)}-700`}>
                    {task.status}
                  </span>
                  {task.assigned_agent && (
                    <span className="text-xs text-gray-500">
                      🤖 {task.assigned_agent}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Tasks */}
      {upcomingTasks.length > 0 && (
        <div>
          <h3 className="text-xl font-bold mb-4">📆 Upcoming ({upcomingTasks.length})</h3>
          <div className="space-y-2">
            {upcomingTasks.slice(0, 5).map((task) => (
              <div key={task.task_id} className="bg-gray-50 rounded-lg p-3 flex justify-between items-center">
                <span className="text-sm">{task.task_name}</span>
                <span className="text-xs text-gray-500">
                  {new Date(task.due_date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### Deliverables:
✅ Strategy list and detail pages
✅ ADAPT framework visual representation
✅ Campaign task checklist
✅ Move sequence visualization

---

## 📋 **Prompt 7: Analytics Dashboard with Predictions**

### Files & Paths:
```
src/pages/analytics/index.tsx               (create new)
src/pages/analytics/campaign/[id].tsx       (create new)
src/components/MetricsChart.tsx             (create new)
src/components/InsightsPanel.tsx            (create new)
src/components/PivotSuggestion.tsx          (create new)
```

### Tasks:

#### 1. Create Analytics Dashboard

Create `src/pages/analytics/index.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';
import MetricsChart from '@/components/MetricsChart';
import InsightsPanel from '@/components/InsightsPanel';

export default function AnalyticsDashboardPage() {
  const [workspaceMetrics, setWorkspaceMetrics] = useState<any>(null);
  const [learnings, setLearnings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [metrics, crossLearnings] = await Promise.all([
        backendAPI.analytics.getWorkspaceMetrics('current-workspace-id'),
        backendAPI.analytics.getLearnings(30),
      ]);
      setWorkspaceMetrics(metrics);
      setLearnings(crossLearnings.learnings);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">📊 Analytics Dashboard</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6">
          <div className="text-sm opacity-80 mb-1">Total Reach</div>
          <div className="text-3xl font-bold">{workspaceMetrics?.total_reach?.toLocaleString()}</div>
          <div className="text-xs opacity-70 mt-2">+12% vs last month</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6">
          <div className="text-sm opacity-80 mb-1">Engagement Rate</div>
          <div className="text-3xl font-bold">{workspaceMetrics?.engagement_rate?.toFixed(2)}%</div>
          <div className="text-xs opacity-70 mt-2">+3.2% vs last month</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6">
          <div className="text-sm opacity-80 mb-1">Conversions</div>
          <div className="text-3xl font-bold">{workspaceMetrics?.total_conversions}</div>
          <div className="text-xs opacity-70 mt-2">+8% vs last month</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-lg p-6">
          <div className="text-sm opacity-80 mb-1">ROI</div>
          <div className="text-3xl font-bold">{workspaceMetrics?.roi?.toFixed(1)}x</div>
          <div className="text-xs opacity-70 mt-2">+0.5x vs last month</div>
        </div>
      </div>

      {/* Metrics Chart */}
      {workspaceMetrics?.time_series && (
        <MetricsChart data={workspaceMetrics.time_series} />
      )}

      {/* Cross-Campaign Learnings */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">🧠 AI Learnings (Last 30 Days)</h2>
        <div className="space-y-4">
          {learnings.map((learning, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start gap-4">
                <span className="text-3xl">💡</span>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">{learning.title}</h3>
                  <p className="text-gray-700 mb-3">{learning.insight}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                      Confidence: {(learning.confidence * 100).toFixed(0)}%
                    </span>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                      Impact: {learning.impact_level}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

#### 2. Create Metrics Chart Component

Create `src/components/MetricsChart.tsx`:
```typescript
import React from 'react';

interface DataPoint {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
}

interface Props {
  data: DataPoint[];
}

export default function MetricsChart({ data }: Props) {
  // Simplified chart - in production, use recharts or chart.js
  const maxImpressions = Math.max(...data.map(d => d.impressions));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-6">📈 Performance Trends</h2>

      <div className="space-y-4">
        {data.map((point, idx) => (
          <div key={idx}>
            <div className="flex justify-between text-sm mb-1">
              <span>{new Date(point.date).toLocaleDateString()}</span>
              <span className="text-gray-600">{point.impressions.toLocaleString()} impressions</span>
            </div>
            <div className="h-8 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full"
                style={{ width: `${(point.impressions / maxImpressions) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 flex gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>Impressions</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span>Clicks</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500"></div>
          <span>Conversions</span>
        </div>
      </div>
    </div>
  );
}
```

#### 3. Create Pivot Suggestion Component

Create `src/components/PivotSuggestion.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface Props {
  moveId: string;
}

export default function PivotSuggestion({ moveId }: Props) {
  const [suggestion, setSuggestion] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSuggestion();
  }, [moveId]);

  const fetchSuggestion = async () => {
    try {
      setLoading(true);
      const data = await backendAPI.analytics.getPivotSuggestion(moveId);
      setSuggestion(data);
    } catch (error) {
      console.error('Failed to fetch pivot suggestion:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;
  if (!suggestion || !suggestion.should_pivot) return null;

  return (
    <div className="bg-gradient-to-r from-orange-50 to-red-50 border-2 border-orange-200 rounded-lg p-6">
      <div className="flex items-start gap-4">
        <span className="text-4xl">⚠️</span>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-orange-800 mb-2">
            Pivot Recommendation
          </h3>
          <p className="text-gray-700 mb-4">{suggestion.reason}</p>

          <div className="bg-white rounded-lg p-4 mb-4">
            <h4 className="font-semibold mb-2">Suggested Changes:</h4>
            <ul className="space-y-2">
              {suggestion.suggested_changes.map((change: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-green-600">→</span>
                  <span className="text-sm">{change}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">Confidence:</span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-500"
                style={{ width: `${suggestion.confidence * 100}%` }}
              />
            </div>
            <span className="text-sm font-semibold">
              {(suggestion.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Deliverables:
✅ Analytics dashboard with key metrics
✅ Performance trends chart
✅ Cross-campaign AI learnings
✅ Pivot suggestions with confidence scores

---

## 📋 **Prompt 8: Agent Run Inspector (Advanced)**

### Files & Paths:
```
src/pages/debug/agent-runs.tsx              (create new)
src/components/AgentExecutionTrace.tsx      (create new)
src/components/CorrelationIDSearch.tsx      (create new)
```

### Tasks:

#### 1. Create Agent Runs Page

Create `src/pages/debug/agent-runs.tsx`:
```typescript
import React, { useState } from 'react';
import CorrelationIDSearch from '@/components/CorrelationIDSearch';
import AgentExecutionTrace from '@/components/AgentExecutionTrace';

export default function AgentRunsPage() {
  const [selectedCorrelationId, setSelectedCorrelationId] = useState<string>('');

  return (
    <div className="container mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-8">🔍 Agent Run Inspector</h1>

      <CorrelationIDSearch onSelect={setSelectedCorrelationId} />

      {selectedCorrelationId && (
        <div className="mt-8">
          <AgentExecutionTrace correlationId={selectedCorrelationId} />
        </div>
      )}
    </div>
  );
}
```

#### 2. Create Correlation ID Search

Create `src/components/CorrelationIDSearch.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface Props {
  onSelect: (correlationId: string) => void;
}

export default function CorrelationIDSearch({ onSelect }: Props) {
  const [recentRuns, setRecentRuns] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchRecentRuns();
  }, []);

  const fetchRecentRuns = async () => {
    try {
      const data = await backendAPI.orchestration.listRecentRuns(20);
      setRecentRuns(data.runs);
    } catch (error) {
      console.error('Failed to fetch recent runs:', error);
    }
  };

  const filteredRuns = recentRuns.filter(run =>
    run.correlation_id.includes(searchQuery) ||
    run.graph_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Recent Agent Runs</h2>

      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search by correlation ID or graph name..."
        className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
      />

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredRuns.map((run) => (
          <button
            key={run.correlation_id}
            onClick={() => onSelect(run.correlation_id)}
            className="w-full text-left p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="font-mono text-sm text-blue-600">{run.correlation_id}</span>
              <span className={`text-xs px-2 py-1 rounded ${
                run.status === 'completed' ? 'bg-green-100 text-green-700' :
                run.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {run.status}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              {run.graph_name} • {new Date(run.started_at).toLocaleString()}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
```

#### 3. Create Agent Execution Trace

Create `src/components/AgentExecutionTrace.tsx`:
```typescript
import React, { useState, useEffect } from 'react';
import { backendAPI } from '@/lib/services/backend-api';

interface Props {
  correlationId: string;
}

interface TraceStep {
  step_number: number;
  agent_name: string;
  action: string;
  input: any;
  output: any;
  duration_ms: number;
  timestamp: string;
  metadata?: any;
}

export default function AgentExecutionTrace({ correlationId }: Props) {
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchTrace();
  }, [correlationId]);

  const fetchTrace = async () => {
    try {
      setLoading(true);
      const data = await backendAPI.orchestration.getExecutionTrace(correlationId);
      setTrace(data.steps);
    } catch (error) {
      console.error('Failed to fetch trace:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleStep = (stepNumber: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepNumber)) {
      newExpanded.delete(stepNumber);
    } else {
      newExpanded.add(stepNumber);
    }
    setExpandedSteps(newExpanded);
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Execution Trace</h2>
      <p className="text-sm text-gray-600 mb-6">
        Correlation ID: <span className="font-mono">{correlationId}</span>
      </p>

      <div className="space-y-4">
        {trace.map((step) => (
          <div key={step.step_number} className="border border-gray-200 rounded-lg">
            <button
              onClick={() => toggleStep(step.step_number)}
              className="w-full p-4 flex items-center justify-between hover:bg-gray-50"
            >
              <div className="flex items-center gap-4">
                <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold text-sm">
                  {step.step_number}
                </span>
                <div className="text-left">
                  <div className="font-semibold">{step.agent_name}</div>
                  <div className="text-sm text-gray-600">{step.action}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">{step.duration_ms}ms</span>
                <span className="text-xl">{expandedSteps.has(step.step_number) ? '−' : '+'}</span>
              </div>
            </button>

            {expandedSteps.has(step.step_number) && (
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Input</h4>
                    <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-64">
                      {JSON.stringify(step.input, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Output</h4>
                    <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-64">
                      {JSON.stringify(step.output, null, 2)}
                    </pre>
                  </div>
                </div>
                {step.metadata && (
                  <div className="mt-4">
                    <h4 className="font-semibold text-sm mb-2">Metadata</h4>
                    <pre className="text-xs bg-white p-3 rounded overflow-auto">
                      {JSON.stringify(step.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Deliverables:
✅ Agent run inspector page
✅ Correlation ID search
✅ Execution trace visualization
✅ Step-by-step debugging with input/output

---

## 📋 **Prompt 9: UI/UX Polish & Animations**

### Files & Paths:
```
src/components/LoadingStates.tsx            (create new)
src/components/EmptyStates.tsx              (create new)
src/components/Notifications.tsx            (create new)
tailwind.config.js                          (update)
```

### Tasks:

#### 1. Create Loading States

Create `src/components/LoadingStates.tsx`:
```typescript
import React from 'react';

export const SkeletonCard = () => (
  <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
    <div className="h-3 bg-gray-200 rounded w-5/6"></div>
  </div>
);

export const SpinnerLoader = ({ message }: { message?: string }) => (
  <div className="flex flex-col items-center justify-center py-12">
    <div className="relative">
      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <span className="text-2xl">🦖</span>
      </div>
    </div>
    {message && (
      <p className="mt-4 text-gray-600 animate-pulse">{message}</p>
    )}
  </div>
);

export const ProgressBar = ({ progress }: { progress: number }) => (
  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
    <div
      className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
      style={{ width: `${progress}%` }}
    />
  </div>
);
```

#### 2. Create Empty States

Create `src/components/EmptyStates.tsx`:
```typescript
import React from 'react';

interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="text-center py-16">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export const NoCohortsState = ({ onCreate }: { onCreate: () => void }) => (
  <EmptyState
    icon="👥"
    title="No Cohorts Yet"
    description="Create your first customer cohort to start building targeted marketing strategies"
    actionLabel="Create Cohort"
    onAction={onCreate}
  />
);

export const NoStrategiesState = ({ onCreate }: { onCreate: () => void }) => (
  <EmptyState
    icon="🎯"
    title="No Strategies Yet"
    description="Generate your first AI-powered marketing strategy using the ADAPT framework"
    actionLabel="Create Strategy"
    onAction={onCreate}
  />
);
```

#### 3. Create Toast Notifications

Create `src/components/Notifications.tsx`:
```typescript
import React, { createContext, useContext, useState } from 'react';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface ToastContextValue {
  showToast: (type: Toast['type'], message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (type: Toast['type'], message: string) => {
    const id = Math.random().toString(36);
    setToasts(prev => [...prev, { id, type, message }]);

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-4 rounded-lg shadow-lg animate-slide-in-right ${
              toast.type === 'success' ? 'bg-green-600' :
              toast.type === 'error' ? 'bg-red-600' :
              toast.type === 'warning' ? 'bg-yellow-600' :
              'bg-blue-600'
            } text-white`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
```

#### 4. Update Tailwind Config

Update `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

### Deliverables:
✅ Loading skeleton components
✅ Empty state components
✅ Toast notification system
✅ Custom animations

---

## 📋 **Prompt 10: Mock Mode & Testing**

### Files & Paths:
```
src/lib/services/mock-api.ts                (create new)
src/lib/services/backend-api.ts             (update)
.env.development                            (update)
```

### Tasks:

#### 1. Create Mock API

Create `src/lib/services/mock-api.ts`:
```typescript
/**
 * Mock API for frontend development without backend
 */

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const mockAPI = {
  onboarding: {
    async startSession() {
      await delay(500);
      return {
        session_id: 'mock-session-123',
        current_question: {
          question_id: 'q1',
          question_text: 'What type of entity are you onboarding?',
          question_type: 'single_choice',
          options: ['Business', 'Personal Brand', 'Executive', 'Agency'],
        },
      };
    },

    async submitAnswer(sessionId: string, questionId: string, answer: any) {
      await delay(800);
      return {
        next_question: {
          question_id: 'q2',
          question_text: 'What is your primary marketing goal?',
          question_type: 'text',
        },
      };
    },

    async getProfile(sessionId: string) {
      await delay(500);
      return {
        entity_type: 'Business',
        industry: 'SaaS',
        goals: ['Increase brand awareness', 'Generate leads'],
      };
    },
  },

  icp: {
    async createICP(data: any) {
      await delay(1000);
      return {
        cohort_id: 'mock-cohort-123',
        nickname: data.nickname,
        ...data,
      };
    },

    async listICPs() {
      await delay(500);
      return {
        cohorts: [
          {
            cohort_id: '1',
            nickname: 'Tech Startup Founders',
            role: 'CEO',
            biggest_pain_point: 'Limited marketing budget',
            psychographic_tags: ['innovative', 'risk-taker', 'data-driven'],
          },
          {
            cohort_id: '2',
            nickname: 'Marketing Managers',
            role: 'Marketing Manager',
            biggest_pain_point: 'Proving ROI',
            psychographic_tags: ['analytical', 'creative', 'strategic'],
          },
        ],
      };
    },
  },

  content: {
    async generateBlog(data: any) {
      await delay(3000); // Simulate LLM generation time
      return {
        content_id: 'mock-content-123',
        title: `How to ${data.topic}`,
        content: `<h1>${data.topic}</h1><p>This is mock blog content generated for testing...</p>`,
      };
    },

    async reviewContent(contentId: string) {
      await delay(2000);
      return {
        overall_score: 8.5,
        dimensions: {
          clarity: { score: 9, feedback: 'Very clear and well-structured' },
          brand_alignment: { score: 8, feedback: 'Good alignment with brand voice' },
          audience_fit: { score: 8.5, feedback: 'Well-tailored to target audience' },
          engagement: { score: 8, feedback: 'Strong hooks and engaging content' },
          factual_accuracy: { score: 9, feedback: 'All facts verified' },
          seo_optimization: { score: 7, feedback: 'Could use more keywords' },
          readability: {
            score: 8,
            flesch_kincaid_grade: 8,
            estimated_reading_time: 5,
            average_sentence_length: 15,
          },
        },
        approval_recommendation: 'approve_with_revisions',
        priority_fixes: ['Add more SEO keywords', 'Include meta description'],
      };
    },
  },

  performance: {
    async predictEngagement(data: any) {
      await delay(1500);
      return {
        likes: { predicted_value: 245, confidence: 0.82, confidence_interval: { lower: 200, upper: 290 } },
        shares: { predicted_value: 48, confidence: 0.75, confidence_interval: { lower: 35, upper: 60 } },
        comments: { predicted_value: 32, confidence: 0.70, confidence_interval: { lower: 25, upper: 40 } },
        click_through_rate: { predicted_value: 3.2, confidence: 0.85, confidence_interval: { lower: 2.8, upper: 3.6 } },
        conversion_rate: { predicted_value: 1.5, confidence: 0.78, confidence_interval: { lower: 1.2, upper: 1.8 } },
        engagement_score: 78,
        viral_potential: 65,
        optimal_posting_time: {
          day_of_week: 'Tuesday',
          hour: 10,
          expected_boost: 15,
        },
      };
    },
  },

  memory: {
    async remember(workspaceId: string, key: string, value: any) {
      await delay(500);
      return { success: true };
    },

    async recall(workspaceId: string, key: string) {
      await delay(500);
      return {
        value: { tone: ['professional', 'friendly'], formality_level: 7 },
      };
    },

    async search(workspaceId: string, query: string, topK: number) {
      await delay(800);
      return {
        results: [
          {
            key: 'brand_voice',
            value: { tone: ['professional'], formality_level: 8 },
            similarity_score: 0.92,
            memory_type: 'workspace',
          },
        ],
      };
    },
  },
};
```

#### 2. Add Mock Mode Toggle

Update `src/lib/services/backend-api.ts`:
```typescript
import { supabase } from '../supabase';
import { mockAPI } from './mock-api';

const BACKEND_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true';

// Wrapper to switch between real and mock API
function createAPI<T extends object>(realAPI: T, mockImplementation: T): T {
  if (USE_MOCK_API) {
    console.log('🎭 Using MOCK API');
    return mockImplementation;
  }
  return realAPI;
}

// ... existing apiFetch function ...

// Export wrapped APIs
export const onboardingAPI = createAPI(
  { /* real implementation */ },
  mockAPI.onboarding
);

export const icpAPI = createAPI(
  { /* real implementation */ },
  mockAPI.icp
);

export const contentAPI = createAPI(
  { /* real implementation */ },
  mockAPI.content
);

export const performanceAPI = createAPI(
  { /* real implementation */ },
  mockAPI.performance
);

export const memoryAPI = createAPI(
  { /* real implementation */ },
  mockAPI.memory
);
```

#### 3. Update Environment Variables

Create `.env.development`:
```env
# Backend API
VITE_BACKEND_API_URL=http://localhost:8000/api/v1

# Enable mock API for frontend-only development
VITE_USE_MOCK_API=false

# Supabase
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Deliverables:
✅ Complete mock API implementation
✅ Mock mode toggle via environment variable
✅ Realistic delays and data for testing
✅ Frontend development without backend dependency

---

## 🎉 **All 10 Prompts Complete!**

### Summary Checklist:

- [x] **Prompt 1**: Enhanced API layer (memory, performance, correlation IDs)
- [x] **Prompt 2**: Onboarding wizard with dynamic questions
- [x] **Prompt 3**: Cohorts dashboard with psychographic tags
- [x] **Prompt 4**: Memory console & brand voice editor
- [x] **Prompt 5**: Content generation with critic/guardian/performance
- [x] **Prompt 6**: Strategy & campaign interfaces with ADAPT framework
- [x] **Prompt 7**: Analytics dashboard with AI learnings
- [x] **Prompt 8**: Agent run inspector for debugging
- [x] **Prompt 9**: UI/UX polish with loading states and animations
- [x] **Prompt 10**: Mock API mode for frontend-only development

### 🚀 Next Steps:

1. **Install Dependencies**:
   ```bash
   npm install uuid
   npm install --save-dev @types/uuid
   ```

2. **Start with Prompt 1**: Enhance the API layer first (foundation for everything)

3. **Work Sequentially**: Each prompt builds on the previous one

4. **Test as You Go**: Use mock mode (`VITE_USE_MOCK_API=true`) for rapid iteration

5. **Backend Integration**: Once UI is ready, switch to real backend and test end-to-end

---

**Ready to build the world's most advanced AI marketing platform! 🦖✨**
