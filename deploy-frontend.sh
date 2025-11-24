#!/bin/bash
# Deploy RaptorFlow Frontend to Vercel

set -e

echo "🚀 RaptorFlow Frontend Deployment to Vercel"
echo "============================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install with: npm install -g vercel"
    exit 1
fi

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Link project if not already linked
if [ ! -d ".vercel" ]; then
    echo "📝 Linking to Vercel project..."
    vercel link
fi

# Set environment variables
echo "🔐 Setting environment variables..."
read -p "Enter VITE_SUPABASE_URL: " SUPABASE_URL
read -p "Enter VITE_SUPABASE_ANON_KEY: " SUPABASE_KEY
read -p "Enter VITE_BACKEND_API_URL: " BACKEND_URL
read -p "Enter VITE_POSTHOG_KEY (optional): " POSTHOG_KEY

vercel env add VITE_SUPABASE_URL "$SUPABASE_URL" --yes
vercel env add VITE_SUPABASE_ANON_KEY "$SUPABASE_KEY" --yes
vercel env add VITE_BACKEND_API_URL "$BACKEND_URL" --yes
[ ! -z "$POSTHOG_KEY" ] && vercel env add VITE_POSTHOG_KEY "$POSTHOG_KEY" --yes

# Build and deploy
echo "🏗️  Building and deploying to Vercel..."
npm ci
vercel deploy --prod

echo "✅ Frontend deployed successfully!"
echo "📊 Check your deployment: https://vercel.com/dashboard"
