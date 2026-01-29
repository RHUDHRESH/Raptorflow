#!/bin/bash

# RaptorFlow Migration Script
# Apply migrations in correct order

echo "🚀 Applying RaptorFlow Phase 1 Migrations..."

# Migration files in order
MIGRATIONS=(
    "000_base_schema_clean.sql"
    "001_auth_triggers.sql"
    "002_payment_transactions.sql"
    "005_subscriptions.sql"
)

# Check if we have Supabase project URL
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ ERROR: SUPABASE_URL environment variable not set"
    echo "Set it: export SUPABASE_URL=https://your-project.supabase.co"
    exit 1
fi

# Check if we have Supabase service key
if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ ERROR: SUPABASE_SERVICE_ROLE_KEY environment variable not set"
    echo "Set it: export SUPABASE_SERVICE_ROLE_KEY=your-service-role-key"
    exit 1
fi

echo "✅ Environment variables found"
echo "📍 Target: $SUPABASE_URL"

# Apply each migration
for migration in "${MIGRATIONS[@]}"; do
    echo ""
    echo "📋 Applying migration: $migration"

    if [ -f "supabase/migrations/$migration" ]; then
        # Use curl to send the SQL to Supabase
        response=$(curl -s -X POST \
            "$SUPABASE_URL/rest/v1/rpc/execute_sql" \
            -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Content-Type: application/json" \
            -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
            -d "{\"sql\": \"$(cat supabase/migrations/$migration | tr '\n' ' ' | sed 's/"/\\"/g')\"}")

        if [ $? -eq 0 ]; then
            echo "✅ Migration $migration applied successfully"
        else
            echo "❌ Migration $migration failed"
            echo "Response: $response"
            exit 1
        fi
    else
        echo "❌ Migration file not found: supabase/migrations/$migration"
        exit 1
    fi
done

echo ""
echo "🎉 All migrations applied successfully!"
echo "🔍 Verify tables in Supabase dashboard"
