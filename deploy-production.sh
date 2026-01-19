#!/bin/bash

# 🚀 RAPTORFLOW PRODUCTION DEPLOYMENT SCRIPT
# Automated deployment for frontend and backend

set -e  # Exit on any error

echo "🎯 Starting Raptorflow Production Deployment..."
echo "=================================================="

# Check if required tools are installed
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }

# Frontend deployment
echo ""
echo "📦 Step 1: Frontend Deployment"
echo "----------------------------"

cd frontend

# Check if Vercel CLI is installed
if ! command -v vercel >/dev/null 2>&1; then
    echo "📥 Installing Vercel CLI..."
    npm install -g vercel
fi

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Deploy to Vercel
echo "🚀 Deploying frontend to Vercel..."
vercel --prod

# Get the deployed frontend URL
FRONTEND_URL=$(vercel ls --scope $VERCEL_ORG_ID | grep raptorflow | awk '{print $2}' | head -1)
echo "✅ Frontend deployed: https://$FRONTEND_URL"

# Backend deployment
echo ""
echo "📦 Step 2: Backend Deployment"
echo "----------------------------"

cd ../backend

# Check if Render CLI is available (or use manual deployment)
echo "🔨 Building backend..."
python -m pip install -r requirements.txt

# Test backend locally first
echo "🧪 Testing backend..."
python -c "
import main_minimal
print('✅ Backend imports successfully')
"

echo "📋 Backend deployment instructions:"
echo "1. Push code to GitHub repository"
echo "2. Connect Render account: https://render.com"
echo "3. Create new Web Service"
echo "4. Configure environment variables:"
echo "   - PORT: 8001"
echo "   - PYTHON_VERSION: 3.12"
echo "   - START_COMMAND: python -m uvicorn main_minimal:app --host 0.0.0.0 --port \$PORT"
echo "5. Deploy the service"

# Database setup
echo ""
echo "📦 Step 3: Database Setup"
echo "-----------------------"

echo "📋 Database setup instructions:"
echo "1. Access Supabase Dashboard: https://supabase.com/dashboard"
echo "2. Go to SQL Editor"
echo "3. Execute the following SQL:"

# Generate SQL for database setup
cat << 'EOF'
-- Create user_profiles table
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  subscription_plan TEXT CHECK (subscription_plan IN ('soar', 'glide', 'ascent')),
  subscription_status TEXT CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
  subscription_expires_at TIMESTAMPTZ,
  storage_quota_mb INTEGER DEFAULT 100,
  storage_used_mb INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Create payments table
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  transaction_id TEXT UNIQUE NOT NULL,
  plan_id TEXT NOT NULL CHECK (plan_id IN ('soar', 'glide', 'ascent')),
  amount INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
  payment_method TEXT DEFAULT 'phonepe',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.user_profiles
  FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.user_profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view own payments" ON public.payments
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own payments" ON public.payments
  FOR INSERT WITH CHECK (auth.uid() = user_id);
EOF

echo ""
echo "📦 Step 4: Environment Configuration"
echo "-----------------------------------"

echo "📋 Frontend environment variables (.env.local):"
cat << 'EOF'
NEXT_PUBLIC_APP_URL=https://your-domain.vercel.app
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_VERTEX_AI_API_KEY=AQ.Ab8RN6IUsXQOIdywX4O_vrP6lSO5JS-fY_bQG4o84BajiSrIPg
EOF

echo ""
echo "📋 Backend environment variables (Render):"
cat << 'EOF'
PORT=8001
PYTHON_VERSION=3.12
START_COMMAND=python -m uvicorn main_minimal:app --host 0.0.0.0 --port $PORT
NEXT_PUBLIC_SUPABASE_URL=https://vpwwzsanuyhpkvgorcnc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VERTEX_AI_API_KEY=AQ.Ab8RN6IUsXQOIdywX4O_vrP6lSO5JS-fY_bQG4o84BajiSrIPg
PHONEPE_CLIENT_ID=your-phonepe-client-id
PHONEPE_CLIENT_SECRET=your-phonepe-client-secret
PHONEPE_ENV=UAT
EOF

# Final testing
echo ""
echo "📦 Step 5: Post-Deployment Testing"
echo "--------------------------------"

echo "🧪 Testing checklist:"
echo "□ Frontend loads at https://$FRONTEND_URL"
echo "□ Backend health endpoint responds"
echo "□ Database connections work"
echo "□ Authentication flow functions"
echo "□ Onboarding process completes"
echo "□ Payment integration works (with test keys)"
echo "□ AI features respond"

echo ""
echo "🎉 Deployment Summary"
echo "===================="
echo "✅ Frontend: Ready for Vercel deployment"
echo "✅ Backend: Ready for Render deployment"
echo "✅ Database: SQL schema prepared"
echo "✅ Environment: Variables documented"
echo ""
echo "📋 Next Steps:"
echo "1. Deploy frontend to Vercel"
echo "2. Deploy backend to Render"
echo "3. Setup database in Supabase"
echo "4. Configure environment variables"
echo "5. Test end-to-end functionality"
echo ""
echo "🚀 Raptorflow is ready for production!"
echo "======================================"
