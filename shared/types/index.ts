/**
 * Shared TypeScript types for RaptorFlow
 * These types are used by both frontend and backend to ensure type safety
 */

// User & Authentication
export interface User {
  id: string;
  email: string;
  name?: string;
  subscriptionTier: "ascent" | "glide" | "soar" | "enterprise";
  createdAt: string;
  updatedAt: string;
}

// ICP (Ideal Customer Profile)
export interface ICP {
  id: string;
  userId: string;
  name: string;
  role?: string;
  industry?: string;
  painPoints: string[];
  interests: string[];
  tags: string[]; // Psychographic tags (~50 per persona)
  buyingBehavior?: "fast" | "slow" | "comparison" | "impulse";
  createdAt: string;
  updatedAt: string;
}

// Business Identity
export interface Business {
  id: string;
  userId: string;
  name: string;
  description: string;
  legalName?: string;
  gstNumber?: string;
  location?: {
    address?: string;
    city?: string;
    country?: string;
    coordinates?: { lat: number; lng: number };
  };
  website?: string;
  createdAt: string;
  updatedAt: string;
}

// Marketing Goal
export interface MarketingGoal {
  id: string;
  userId: string;
  title: string;
  description: string;
  targetMetric: string;
  targetValue: number;
  timeframe: number; // days
  status: "draft" | "active" | "completed" | "paused";
  createdAt: string;
  updatedAt: string;
}

// ADAPT Strategy
export interface AdaptStrategy {
  id: string;
  userId: string;
  // Audience Alignment
  audienceAlignment: {
    icps: string[]; // ICP IDs
    keyPainPoints: string[];
    summary: string;
  };
  // Design & Differentiate
  designDifferentiate: {
    bigIdea: string;
    tagline?: string;
    keyMessages: string[];
    narrative: string;
  };
  // Assemble & Automate
  assembleAutomate: {
    contentTypes: string[];
    channels: string[];
    assets: string[];
    automation: string[];
  };
  // Promote & Participate
  promoteParticipate: {
    timeline: string;
    engagementStrategy: string;
    channels: string[];
  };
  // Track & Tweak
  trackTweak: {
    keyMetrics: string[];
    targets: Record<string, number>;
    feedbackPlan: string;
  };
  status: "draft" | "active" | "archived";
  createdAt: string;
  updatedAt: string;
}

// Move (Campaign)
export interface Move {
  id: string;
  userId: string;
  strategyId: string;
  name: string;
  goal: string;
  objective: string;
  startDate: string;
  endDate: string;
  status: "draft" | "active" | "completed" | "paused";
  progress: number; // 0-100
  metrics: {
    target: Record<string, number>;
    current: Record<string, number>;
  };
  createdAt: string;
  updatedAt: string;
}

// Daily Task
export interface Task {
  id: string;
  moveId: string;
  userId: string;
  title: string;
  description: string;
  type: "content" | "publish" | "outreach" | "review" | "other";
  status: "pending" | "in_progress" | "completed" | "skipped";
  dueDate: string;
  assignedTo: "user" | "ai" | "both";
  aiGenerated: boolean;
  createdAt: string;
  updatedAt: string;
}

// Content Piece
export interface Content {
  id: string;
  userId: string;
  moveId?: string;
  type: "blog" | "social" | "email" | "ad" | "video" | "other";
  title?: string;
  body: string;
  status: "draft" | "review" | "approved" | "published";
  platform?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

// Asset
export interface Asset {
  id: string;
  userId: string;
  moveId?: string;
  contentTypeId?: string;
  type: "image" | "video" | "document" | "other";
  url: string;
  filename: string;
  size: number;
  metadata?: Record<string, unknown>;
  createdAt: string;
}

// Groundwork Response
export interface GroundworkData {
  business: Omit<Business, "id" | "userId" | "createdAt" | "updatedAt">;
  icps: Omit<ICP, "id" | "userId" | "createdAt" | "updatedAt">[];
  goals: Omit<MarketingGoal, "id" | "userId" | "status" | "createdAt" | "updatedAt">[];
  brandEnergy?: {
    tone: Record<string, number>; // sliders
    voice: string;
    admiredBrands?: string[];
  };
  assets?: {
    logo?: string;
    brandColors?: string[];
    documents?: string[];
  };
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

