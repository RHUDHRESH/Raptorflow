# Testing Setup Guide

This guide will help you set up and test the RaptorFlow application locally.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ and npm installed
- Supabase project created (get URL and keys from Supabase dashboard)
- Google Cloud Project with Vertex AI enabled (for backend AI features)
- Redis running locally (optional, for caching)

## Step 1: Configure Frontend Environment Variables

1. Create `.env.local` in the project root (already created as template)
2. Fill in your actual values:

```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Where to get Supabase values:**
- Go to https://app.supabase.com/
- Select your project
- Go to Settings → API
- Copy the "Project URL" and "anon public" key

## Step 2: Configure Backend Environment Variables

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   # On Windows PowerShell:
   Copy-Item .env.example .env
   
   # On Linux/Mac:
   cp .env.example .env
   ```

3. Edit `.env` and fill in your actual values:
   - `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
   - `SUPABASE_URL` - Same as frontend
   - `SUPABASE_SERVICE_KEY` - From Supabase Settings → API → "service_role" key
   - `SUPABASE_ANON_KEY` - Same as frontend
   - `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
   - `GOOGLE_APPLICATION_CREDENTIALS` - Path to your service account JSON key
   - `SECRET_KEY` - Generate a random secret key for JWT tokens

## Step 3: Install Backend Dependencies

1. Make sure you're in the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the specific packages mentioned:
   ```bash
   pip install google-cloud-aiplatform anthropic[vertex]
   ```

## Step 4: Start the Backend Server

From the `backend` directory:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

The backend API will be available at `http://localhost:8000`

## Step 5: Start the Frontend Development Server

1. Open a **new terminal** (keep backend running)
2. Navigate to the project root:
   ```bash
   cd C:\Users\hp\OneDrive\Desktop\Raptorflow
   ```

3. Install frontend dependencies (if not already installed):
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network:  use --host to expose
```

The frontend will be available at `http://localhost:5173`

## Step 6: Test the Application

1. Open your browser and navigate to `http://localhost:5173`
2. Try logging in with Google OAuth (if configured)
3. Complete the onboarding flow
4. Test the cohort generation feature
5. Check browser console (F12) for any errors
6. Check backend terminal for API logs

## Troubleshooting

### Backend won't start
- Check that all required environment variables are set in `backend/.env`
- Verify Python version: `python --version` (should be 3.9+)
- Check if port 8000 is already in use: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Mac/Linux)

### Frontend can't connect to backend
- Verify `VITE_API_URL` in `.env.local` matches backend URL
- Check that backend is running on port 8000
- Check CORS settings in `backend/main.py`

### Supabase connection errors
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are correct
- Check Supabase project is active and not paused
- Verify Google OAuth is configured in Supabase dashboard

### Vertex AI errors
- Verify Google Cloud credentials are set up correctly
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure Vertex AI API is enabled in your GCP project
- Verify `GOOGLE_CLOUD_PROJECT` matches your project ID

## Quick Commands Reference

```bash
# Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in new terminal)
npm run dev

# Install backend deps
cd backend
pip install -r requirements.txt
pip install google-cloud-aiplatform anthropic[vertex]

# Install frontend deps
npm install
```

## Next Steps

- Review the API documentation at `http://localhost:8000/docs` (FastAPI Swagger UI)
- Check `docs/` folder for more detailed documentation
- Review `SETUP_GUIDE.md` for production deployment instructions

