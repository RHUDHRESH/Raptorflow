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
      throw new Error(error.detail || `Failed to generate cohort: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Cohort generation failed:', error);
    throw error;
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

