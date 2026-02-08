import os


def verify_vertex_ai() -> None:
    api_key = os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    project_id = os.getenv("VERTEX_AI_PROJECT_ID") or os.getenv("GCP_PROJECT_ID") or ""
    location = os.getenv("VERTEX_AI_LOCATION") or os.getenv("GCP_REGION") or "us-central1"

    if not api_key:
        raise SystemExit("Set VERTEX_AI_API_KEY (or GOOGLE_API_KEY) to run this check.")

    try:
        import google.generativeai as genai
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"google-generativeai is not available: {exc}")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    print("Vertex AI (GenAI) configured.")
    if project_id:
        print(f"project_id: {project_id}")
    print(f"location: {location}")
    print(f"model: {model.model_name}")


if __name__ == "__main__":
    verify_vertex_ai()
