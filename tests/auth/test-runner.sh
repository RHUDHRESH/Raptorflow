#!/bin/bash
# Quick Auth Test Runner - No Complexity

echo "🔥 RAPTORFLOW AUTH TEST - QUICK RUN"
echo "=================================="

# Check if dev server is running
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ DEV SERVER NOT RUNNING - Start with: npm run dev"
    exit 1
fi

# Run the simple test
echo "🚀 Running auth tests..."
node tests/auth/simple-auth-test.js

echo ""
echo "✨ DONE! If you see ✅ marks above, auth is working!"
echo "📝 If you see ❌, check the error message above"
