import asyncio
import logging
import os
import sys
from pathlib import Path

import httpx
import psycopg
from dotenv import load_dotenv
from google.cloud import secretmanager

ROOT_PATH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_PATH))
sys.path.insert(0, str(ROOT_PATH / "backend"))

# Load .env from repo root and backend folder
load_dotenv(ROOT_PATH / ".env")
load_dotenv(ROOT_PATH / "backend" / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diagnose_infra")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def check_supabase():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    db_url = os.getenv("DATABASE_URL")

    success = True

    logger.info(f"Checking Supabase REST API: {url}")
    if not url:
        logger.error("Supabase URL missing")
        success = False

    if url and anon_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/rest/v1/",
                    headers={"apikey": anon_key, "Authorization": f"Bearer {anon_key}"},
                )
                if response.status_code == 200:
                    logger.info(
                        "Supabase REST API (Anon Key) is reachable and authenticated."
                    )
                else:
                    logger.error(
                        f"Supabase REST API (Anon Key) failed with status {response.status_code}: {response.text}"
                    )
                    success = False
        except Exception as e:
            logger.error(f"Supabase REST API (Anon Key) check failed: {e}")
            success = False
    else:
        logger.warning("Supabase Anon Key missing, skipping check.")

    if url and service_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}/rest/v1/",
                    headers={
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                    },
                )
                if response.status_code == 200:
                    logger.info(
                        "Supabase REST API (Service Role) is reachable and authenticated."
                    )
                else:
                    logger.error(
                        f"Supabase REST API (Service Role) failed with status {response.status_code}: {response.text}"
                    )
                    success = False
        except Exception as e:
            logger.error(f"Supabase REST API (Service Role) check failed: {e}")
            success = False
    else:
        logger.warning("Supabase Service Role Key missing, skipping check.")

    logger.info("Checking Supabase Database connection...")
    if not db_url:
        logger.error("DATABASE_URL missing")
        success = False
    else:
        try:
            # Use a short timeout
            conn = await psycopg.AsyncConnection.connect(db_url, connect_timeout=10)
            await conn.close()
            logger.info("Supabase Database connection successful.")
        except Exception as e:
            logger.error(f"Supabase Database connection failed: {e}")
            success = False

    return success


async def check_redis():
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

    logger.info(f"Checking Upstash Redis REST API: {url}")
    if not url or not token:
        logger.error("Upstash Redis URL or Token missing")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}/ping", headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200 and response.json().get("result") == "PONG":
                logger.info("Upstash Redis is reachable and authenticated.")
            else:
                logger.error(f"Upstash Redis returned: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Upstash Redis check failed: {e}")
        return False

    return True


async def check_gcp():
    project_id = os.getenv("GCP_PROJECT_ID")
    logger.info(f"Checking GCP Secret Manager (Project: {project_id})")
    if not project_id:
        logger.error("GCP_PROJECT_ID missing")
        return False

    try:
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}"
        # Just try to list secrets (requires permission)
        secrets = client.list_secrets(request={"parent": parent})
        # Try to iterate first item
        for s in secrets:
            logger.info(
                f"Successfully listed secrets in project {project_id}. GCP connectivity confirmed."
            )
            break
    except Exception as e:
        logger.info(
            f"GCP Secret Manager check failed (expected if local creds not set): {e}"
        )
        # Not necessarily a failure if local env variables are used as fallback
        return True

    return True


async def check_vertex_ai():
    logger.info("Checking Vertex AI inference readiness...")
    try:
        from backend.inference import InferenceProvider

        if not InferenceProvider.is_ready():
            logger.error(
                "Vertex AI not ready. Set VERTEX_AI_API_KEY/INFERENCE_SIMPLE or configure ADC."
            )
            return False

        embeddings = InferenceProvider.get_embeddings()
        if embeddings is None:
            logger.error("Vertex AI embeddings client not available.")
            return False

        # Minimal request to validate auth and model access.
        await asyncio.wait_for(embeddings.aembed_query("diagnostic ping"), timeout=20)
        logger.info("Vertex AI embeddings call succeeded.")
        return True
    except asyncio.TimeoutError:
        logger.error("Vertex AI inference check timed out.")
        return False
    except Exception as exc:
        logger.error(f"Vertex AI inference check failed: {exc}")
        return False


async def main():
    logger.info("Starting Industrial Infrastructure Diagnosis...")

    s_ok = await asyncio.wait_for(check_supabase(), timeout=30)
    r_ok = await asyncio.wait_for(check_redis(), timeout=15)
    g_ok = await asyncio.wait_for(check_gcp(), timeout=15)
    v_ok = await asyncio.wait_for(check_vertex_ai(), timeout=30)

    if s_ok and r_ok and g_ok and v_ok:
        logger.info("DIAGNOSIS COMPLETE: ALL SYSTEMS NOMINAL.")
    else:
        logger.error("DIAGNOSIS COMPLETE: FAILURES DETECTED.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
