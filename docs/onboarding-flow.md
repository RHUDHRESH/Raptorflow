# Onboarding Flow & API Integration

This document explains how the frontend (Next.js) should interact with the backend during the onboarding process.

## Overview

The onboarding flow consists of 4 main steps:
1. **Goals**
2. **Audience**
3. **Positioning**
4. **Execution**

Followed by a **Review** step where the user locks the intake and triggers plan generation.

## Authentication

All API requests must include the Supabase JWT in the Authorization header:
`Authorization: Bearer <SUPABASE_ACCESS_TOKEN>`

## API Endpoints

Base URL: `http://localhost:8000/api/onboarding` (Local) or Cloud Run URL (Prod).

### 1. Load Intake
**When:** When the user enters the onboarding flow or switches projects.

- **Endpoint:** `GET /api/onboarding/intake`
- **Query Param:** `projectId` (UUID)
- **Response:**
  ```json
  {
    "id": "...",
    "project_id": "...",
    "goals": { ... },
    "audience": { ... },
    "positioning": { ... },
    "execution": { ... },
    "locked_at": null // or timestamp if locked
  }
  ```
- **Note:** If no intake exists, the backend creates a blank one and returns it.

### 2. Save Section
**When:** When the user completes a step (e.g., clicks "Next" or auto-save).

- **Endpoint:** `POST /api/onboarding/intake`
- **Body:**
  ```json
  {
    "projectId": "...",
    "section": "goals", // or "audience", "positioning", "execution"
    "data": {
      "question1": "answer1",
      ...
    }
  }
  ```
- **Response:** Returns the updated intake object.

### 3. Lock & Generate
**When:** On the Review page, when the user clicks "Generate Plan".

- **Endpoint:** `POST /api/onboarding/lock-and-generate`
- **Body:**
  ```json
  {
    "projectId": "..."
  }
  ```
- **Behavior:**
  1. Sets `locked_at` on the intake (making it effectively read-only).
  2. Creates a new `plan` record in `draft` status.
  3. Queues a job (in Upstash Redis) for the AI pipeline to generate the plan content.
- **Response:**
  ```json
  {
    "planId": "...",
    "status": "queued"
  }
  ```
- **Frontend Action:** Redirect user to `/preview/:planId`.
