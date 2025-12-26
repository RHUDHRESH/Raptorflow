-- RaptorFlow Migration: Precision Soundbite Framework 3.0
-- Introduces tables for JTBD, Message Hierarchy, Awareness Matrix, Proof Vault, and 7 Precision Soundbites

-- 1. Jobs to Be Done (JTBD) - Phase 3
CREATE TABLE IF NOT EXISTS foundation_jtbd (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    functional_job TEXT NOT NULL,
    emotional_job TEXT NOT NULL,
    social_job TEXT NOT NULL,

    context_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Message Hierarchy Pyramid - Phase 3
CREATE TABLE IF NOT EXISTS foundation_message_hierarchy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    essence TEXT NOT NULL, -- Brand Essence
    core_message TEXT NOT NULL,
    pillars JSONB DEFAULT '[]'::jsonb, -- Array of messaging pillars
    proof_points JSONB DEFAULT '[]'::jsonb, -- Supporting proof for pillars

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Customer Awareness Matrix - Phase 3
CREATE TABLE IF NOT EXISTS foundation_awareness_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    unaware_strategy TEXT,
    problem_aware_strategy TEXT,
    solution_aware_strategy TEXT,
    product_aware_strategy TEXT,
    most_aware_strategy TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Evidence & Proof Vault - Phase 5 (Shared)
CREATE TABLE IF NOT EXISTS foundation_proof_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    type TEXT NOT NULL CHECK (type IN ('stat', 'testimonial', 'guarantee', 'case_study')),
    content TEXT NOT NULL,
    source_link TEXT,
    source_name TEXT,
    is_verified BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Precision Soundbites (The 7 Soundbites) - Phase 6
CREATE TABLE IF NOT EXISTS foundation_precision_soundbites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    type TEXT NOT NULL CHECK (type IN (
        'problem_revelation',
        'agitation',
        'mechanism',
        'objection_handling',
        'transformation',
        'positioning',
        'urgency'
    )),
    content TEXT NOT NULL,
    draft_content TEXT,
    ai_variation_a TEXT,
    ai_variation_b TEXT,

    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'final')),
    clarity_score NUMERIC,
    proof_links UUID[] DEFAULT '{}', -- Array of proof_vault IDs

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Extend Foundation State to support new phases
ALTER TABLE foundation_state
ADD COLUMN IF NOT EXISTS jtbd_id UUID REFERENCES foundation_jtbd(id),
ADD COLUMN IF NOT EXISTS message_hierarchy_id UUID REFERENCES foundation_message_hierarchy(id),
ADD COLUMN IF NOT EXISTS awareness_matrix_id UUID REFERENCES foundation_awareness_matrix(id);

-- Enable RLS on new tables (if not handled globally)
-- Assuming a global script handles basic RLS, but we can add specific ones if needed.
-- For now, we'll follow the project convention of having a separate RLS migration.
