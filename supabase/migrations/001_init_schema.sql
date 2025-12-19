-- Create users table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create campaigns table
CREATE TABLE IF NOT EXISTS public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  objective TEXT NOT NULL,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'paused')),
  week_number INT DEFAULT 1,
  kpi_primary TEXT,
  kpi_baseline INT,
  kpi_target INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create moves table
CREATE TABLE IF NOT EXISTS public.moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES public.campaigns(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  objective TEXT,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'shipped', 'completed')),
  channel TEXT NOT NULL CHECK (channel IN ('email', 'social', 'web', 'direct', 'other')),
  due_date TIMESTAMP WITH TIME ZONE,
  shipped_date TIMESTAMP WITH TIME ZONE,
  proof_url TEXT,
  proof_screenshot TEXT,
  asset_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create assets table
CREATE TABLE IF NOT EXISTS public.assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES public.moves(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('email', 'carousel', 'script', 'image', 'video', 'copy', 'other')),
  content JSONB,
  version INT DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_campaigns_user_id ON public.campaigns(user_id);
CREATE INDEX idx_moves_campaign_id ON public.moves(campaign_id);
CREATE INDEX idx_moves_due_date ON public.moves(due_date);
CREATE INDEX idx_assets_move_id ON public.assets(move_id);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can read own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Create RLS policies for campaigns table
CREATE POLICY "Users can read own campaigns" ON public.campaigns
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create campaigns" ON public.campaigns
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own campaigns" ON public.campaigns
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own campaigns" ON public.campaigns
  FOR DELETE USING (auth.uid() = user_id);

-- Create RLS policies for moves table
CREATE POLICY "Users can read moves in own campaigns" ON public.moves
  FOR SELECT USING (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create moves in own campaigns" ON public.moves
  FOR INSERT WITH CHECK (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update moves in own campaigns" ON public.moves
  FOR UPDATE USING (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete moves in own campaigns" ON public.moves
  FOR DELETE USING (
    campaign_id IN (
      SELECT id FROM public.campaigns WHERE user_id = auth.uid()
    )
  );

-- Create RLS policies for assets table
CREATE POLICY "Users can read assets in own moves" ON public.assets
  FOR SELECT USING (
    move_id IN (
      SELECT m.id FROM public.moves m
      WHERE m.campaign_id IN (
        SELECT c.id FROM public.campaigns c
        WHERE c.user_id = auth.uid()
      )
    )
  );

CREATE POLICY "Users can create assets in own moves" ON public.assets
  FOR INSERT WITH CHECK (
    move_id IN (
      SELECT m.id FROM public.moves m
      WHERE m.campaign_id IN (
        SELECT c.id FROM public.campaigns c
        WHERE c.user_id = auth.uid()
      )
    )
  );

-- Create trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON public.campaigns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_moves_updated_at BEFORE UPDATE ON public.moves
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
