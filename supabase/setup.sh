#!/bin/bash

# RaptorFlow Supabase Setup Script
echo "🚀 Setting up RaptorFlow Supabase Project..."

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Please install it first:"
    echo "   npm install -g supabase"
    exit 1
fi

# Login to Supabase
echo "📝 Logging in to Supabase..."
echo "Please get your access token from: https://supabase.com/dashboard/account/tokens"
supabase login

# Link to project
echo "🔗 Linking to project..."
supabase link --project-ref vpwwzsanuyhpkvgorcnc

# Check status
echo "📊 Checking project status..."
supabase status

# Push migrations
echo "⬆️ Pushing database migrations..."
supabase db push

# Generate types
echo "📝 Generating TypeScript types..."
supabase gen types typescript --local > ../frontend/src/types/supabase.ts

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc"
echo "2. Configure Authentication > Providers > Google"
echo "3. Set site URL to https://raptorflow.in"
echo "4. Add redirect URLs"
