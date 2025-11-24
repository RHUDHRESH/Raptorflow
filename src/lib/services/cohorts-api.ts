/**
 * Cohorts API Service
 * Handles all cohort-related API calls to the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface CohortGenerateInputs {
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

interface CohortData {
  name?: string;
  executiveSummary: string;
  demographics: {
    companySize: string;
    industry: string;
    revenue: string;
    location: string;
  };
  buyerRole: string;
  psychographics: {
    values: string[];
    decisionStyle: string;
    priorities: string[];
  };
  painPoints: string[];
  goals: string[];
  behavioralTriggers: string[];
  communication: {
    channels: string[];
    tone: string;
    format: string;
  };
  budget: string;
  timeline: string;
  decisionStructure?: string;
}

interface PsychographicsData {
  values: string[];
  decisionStyle: string;
  personalityTraits: string[];
  interests: string[];
  painPsychology: {
    primaryFear: string;
    motivation: string;
    emotionalDriver: string;
  };
  contentPreferences: {
    format: string;
    tone: string;
    channels: string[];
  };
}

const dedupeStrings = (items: string[]): string[] => {
  return Array.from(new Set(items.filter((item) => Boolean(item && item.trim()))));
};

const buildLocalCohortFromInputs = (inputs: CohortGenerateInputs): CohortData => {
  const safe = (value?: string) => (value || '').trim();
  const business = safe(inputs.businessDescription);
  const product = safe(inputs.productDescription);
  const target = safe(inputs.targetMarket);
  const valueProposition = safe(inputs.valueProposition);
  const topCustomers = safe(inputs.topCustomers);

  const combined = `${business} ${product} ${target} ${valueProposition} ${topCustomers}`.toLowerCase();
  const contains = (keywords: string[]) => keywords.some((keyword) => combined.includes(keyword));

  const companySize = contains(['enterprise', 'fortune', 'global'])
    ? '1000+'
    : contains(['mid', 'scale', 'series b', 'series c'])
      ? '201-500'
      : contains(['startup', 'early', 'seed', 'small'])
        ? '11-50'
        : '51-200';

  const revenue = companySize === '1000+'
    ? '$100M+'
    : companySize === '201-500'
      ? '$25M-$100M'
      : companySize === '11-50'
        ? '$1M-$5M'
        : '$5M-$25M';

  const industry = contains(['ecommerce', 'e-commerce', 'retail'])
    ? 'E-commerce'
    : contains(['health', 'med', 'clinic'])
      ? 'Healthcare'
      : contains(['finance', 'fintech'])
        ? 'Finance'
        : contains(['manufacturing', 'supply chain'])
          ? 'Manufacturing'
          : contains(['education', 'learning', 'edtech'])
            ? 'Education'
            : contains(['real estate'])
              ? 'Real Estate'
              : contains(['agency', 'services', 'consulting'])
                ? 'Consulting / Agency'
                : contains(['saas', 'software', 'platform', 'product'])
                  ? 'SaaS / Software'
                  : 'Professional Services';

  const location = contains(['uk', 'europe', 'emea'])
    ? 'United Kingdom / Europe'
    : contains(['australia', 'nz', 'anz'])
      ? 'Australia / New Zealand'
      : contains(['canada'])
        ? 'North America (Canada focus)'
        : contains(['asia', 'singapore', 'india'])
          ? 'Asia Pacific'
          : contains(['latin', 'latam', 'brazil'])
            ? 'Latin America'
            : 'North America';

  const buyerRole = contains(['marketing', 'cmo', 'demand', 'growth'])
    ? 'VP / Head of Marketing'
    : contains(['sales', 'revenue'])
      ? 'VP of Sales / CRO'
      : contains(['product', 'cto', 'technology', 'engineering', 'platform'])
        ? 'CTO / Head of Product'
        : contains(['ops', 'operations'])
          ? 'COO / Operations Lead'
          : 'Founder / CEO';

  const shortTarget = (target.split(/[,.;]/)[0] || 'high-fit operators').trim();
  const cohortName = shortTarget ? `${shortTarget} Cohort` : 'High-fit Cohort';

  const summaryParts = [
    shortTarget ? `Companies like ${shortTarget}` : '',
    product ? `who deliver ${product.toLowerCase()}` : '',
    valueProposition ? `and prioritize ${valueProposition.toLowerCase()}` : '',
    'looking to scale with tighter positioning'
  ].filter(Boolean);

  const executiveSummary = summaryParts.length
    ? `${summaryParts.join(', ')}.`
    : 'High-fit companies that value clarity around their best-fit customer and consistent GTM execution.';

  const values = dedupeStrings([
    contains(['data', 'analytics']) ? 'Data-driven decision makers' : '',
    contains(['community', 'brand']) ? 'Community-minded leaders' : '',
    contains(['innovation', 'modern', 'new']) ? 'Innovation-forward' : '',
    'Operational excellence',
    'Measurable ROI'
  ]);

  const priorities = dedupeStrings([
    valueProposition || '',
    contains(['pipeline', 'demand']) ? 'Predictable pipeline growth' : '',
    contains(['retention', 'success']) ? 'Customer retention' : '',
    'Focus on high-propensity accounts'
  ]);

  const painPoints = dedupeStrings([
    contains(['manual', 'spreadsheet']) ? 'Manual workflows that don\'t scale' : '',
    contains(['churn', 'retention']) ? 'Revenue leakage from churn' : '',
    'Hard to articulate their sharpest positioning',
    'Limited bandwidth to act on insights'
  ]);

  const goals = dedupeStrings([
    'Clarify who their best-fit customer really is',
    'Improve close rates by mirroring the right messaging',
    'Reduce wasted spend on low-fit accounts'
  ]);

  const communicationChannels = dedupeStrings([
    contains(['community', 'linkedin']) ? 'LinkedIn' : '',
    contains(['events', 'conference']) ? 'Industry events' : '',
    'Email',
    'Founder communities'
  ]);

  const behavioralTriggers = [
    'New funding or aggressive growth mandate',
    'Team capacity is tapped out and needs leverage',
    'Losing deals to more specialized competitors'
  ];

  const communicationTone = contains(['enterprise']) ? 'Formal and data-backed' : 'Pragmatic and candid';
  const communicationFormat = contains(['technical']) ? 'Deep dives with proof points' : 'Concise briefs with next steps';

  return {
    name: cohortName,
    executiveSummary,
    demographics: {
      companySize,
      industry,
      revenue,
      location
    },
    buyerRole,
    psychographics: {
      values: values.length ? values : ['Operational excellence', 'Measurable ROI'],
      decisionStyle: contains(['fast', 'scrappy', 'startup'])
        ? 'Fast-moving and experimental'
        : 'Analytical with collaborative input',
      priorities: priorities.length ? priorities : ['Predictable growth', 'Focus on best-fit accounts']
    },
    painPoints: painPoints.length ? painPoints : ['Need clarity on their best-fit customer'],
    goals: goals.length ? goals : ['Ship sharper ICP messaging'],
    behavioralTriggers,
    communication: {
      channels: communicationChannels.length ? communicationChannels : ['LinkedIn', 'Email', 'Founder communities'],
      tone: communicationTone,
      format: communicationFormat
    },
    budget: companySize === '11-50'
      ? '$10k - $30k / year'
      : companySize === '201-500'
        ? '$40k - $120k / year'
        : companySize === '1000+'
          ? '$150k+ / year'
          : '$25k - $60k / year',
    timeline: contains(['urgent', 'immediately', 'now']) ? 'Under 30 days' : '30-90 days',
    decisionStructure: buyerRole === 'Founder / CEO'
      ? 'Founder-led with marketing / ops input'
      : 'Small committee with a clear economic buyer'
  };
};

/**
 * Get auth token from localStorage or session
 */
function getAuthToken(): string {
  // Try to get from localStorage first (Supabase auth)
  const session = localStorage.getItem('supabase.auth.token');
  if (session) {
    try {
      const parsed = JSON.parse(session);
      return parsed.access_token || '';
    } catch (e) {
      console.warn('Failed to parse auth token');
    }
  }
  
  // For development, return a dummy token
  return 'dev-token';
}

/**
 * Generate a cohort from business inputs using backend AI
 */
export async function generateCohortFromInputs(inputs: CohortGenerateInputs): Promise<CohortData> {
  const fallback = (reason: unknown) => {
    console.warn('Falling back to local cohort builder because remote generation failed.', reason);
    return buildLocalCohortFromInputs(inputs);
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify(inputs),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.warn('Backend cohort generation returned an error, using fallback.', error);
      return fallback(error);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Cohort generation failed:', error);
    return fallback(error);
  }
}

/**
 * Compute psychographics for a cohort using backend AI
 */
export async function computePsychographics(cohort: CohortData): Promise<PsychographicsData> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/psychographics`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify({ cohort }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Failed to compute psychographics: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Psychographics computation failed:', error);
    throw error;
  }
}

/**
 * Save a cohort to the database
 */
export async function saveCohort(cohortData: CohortData): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify(cohortData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Failed to save cohort: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cohort save failed:', error);
    throw error;
  }
}

/**
 * List all cohorts for the current workspace
 */
export async function listCohorts(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Failed to list cohorts: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cohort list failed:', error);
    throw error;
  }
}

/**
 * Get a specific cohort by ID
 */
export async function getCohort(cohortId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/${cohortId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Failed to get cohort: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cohort fetch failed:', error);
    throw error;
  }
}

/**
 * Delete a cohort by ID
 */
export async function deleteCohort(cohortId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cohorts/${cohortId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `Failed to delete cohort: ${response.status}`);
    }
  } catch (error) {
    console.error('Cohort delete failed:', error);
    throw error;
  }
}

