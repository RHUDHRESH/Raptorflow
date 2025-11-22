# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.

    Initializes:
    - Redis connections (cache and queue)
    - Master Orchestrator with domain supervisors
    - Agent hierarchy
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode")
    logger.info("Initializing Redis connections...")

    try:
        # Initialize Redis connections
        await redis_cache.connect()
        logger.info("✓ Redis cache connection established")
    except Exception as e:
        logger.error(f"✗ Redis cache connection failed: {e}")

    try:
        await redis_queue.connect()
        logger.info("✓ Redis queue connection established")
    except Exception as e:
        logger.error(f"✗ Redis queue connection failed: {e}")

    # Initialize Master Orchestrator and domain supervisors
    logger.info("Initializing Master Orchestrator and supervisors...")
    try:
        from backend.agents.supervisor import master_orchestrator

        # TODO: In future iterations, register actual domain supervisor instances:
        # from backend.agents.onboarding.supervisor import onboarding_supervisor
        # from backend.agents.research.supervisor import research_supervisor
        # etc.
        # master_orchestrator.register_agent("onboarding", onboarding_supervisor)
        # master_orchestrator.register_agent("research", research_supervisor)
        # ...

        # Store orchestrator in app state for access in endpoints
        app.state.master_orchestrator = master_orchestrator

        logger.info("✓ Master Orchestrator initialized")
        logger.info(f"  Available supervisors: {list(master_orchestrator.supervisor_metadata.keys())}")
    except Exception as e:
        logger.error(f"✗ Master Orchestrator initialization failed: {e}")
        # Non-fatal: app can still start, but orchestration won't work

    logger.info(f"✓ {settings.APP_NAME} startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await redis_cache.disconnect()
    await redis_queue.disconnect()
    logger.info("✓ Cleanup complete")
