#!/bin/bash

# Start Redis in background if not provided as service
# redis-server --daemonize yes

# Start Backend
echo "Starting Backend..."
cd /app/backend
python main.py &

# Start Frontend (Dev mode for testing since we want to interact)
# For real production we would use the build + static server
echo "Starting Frontend..."
cd /app/frontend
npm run dev &

# Keep script running
wait -n

# Exit with status of process that exited first
exit $?
