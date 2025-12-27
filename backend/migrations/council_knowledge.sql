-- Expert Council Knowledge Schema
-- Stores heuristics, exploits, and agent DNA

-- Heuristics (Never/Always rules)
CREATE TABLE agent_heuristics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL, -- No FK yet to avoid breaking if table doesn't exist
    agent_role VARCHAR(50), -- e.g., 'brand_philosopher' or NULL for all
    rule_type VARCHAR(20) NOT NULL, -- 'never' or 'always'
    content TEXT NOT NULL,
    source_doc VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Exploits (Proven high-ROI patterns)
CREATE TABLE agent_exploits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    predicted_roi DECIMAL(5,2),
    actual_roi DECIMAL(5,2),
    agent_roles JSONB DEFAULT '[]', -- List of agents this exploit applies to
    precedent_id VARCHAR(50), -- e.g., 'RF-94-NK'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_heuristics_workspace ON agent_heuristics(workspace_id);
CREATE INDEX idx_heuristics_agent ON agent_heuristics(agent_role);
CREATE INDEX idx_exploits_workspace ON agent_exploits(workspace_id);

-- Trigger for updated_at
CREATE TRIGGER update_agent_heuristics_updated_at BEFORE UPDATE ON agent_heuristics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_exploits_updated_at BEFORE UPDATE ON agent_exploits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
