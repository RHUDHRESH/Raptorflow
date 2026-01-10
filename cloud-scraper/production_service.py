"""
Production Scraper Service - Standalone service with production-grade features
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Core imports
import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Import production components
from production_scraper import ProductionScrapingStrategy, production_scraper

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(title="Production Scraper Service", version="3.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "3.0.0",
        "current_strategy": production_scraper.current_strategy.value,
    }


@app.post("/scrape/production")
async def scrape_production(request: Dict[str, Any]):
    """Production-grade scraping endpoint with advanced strategies"""
    url = request.get("url")
    user_id = request.get("user_id")
    legal_basis = request.get("legal_basis", "user_request")
    strategy = request.get("strategy", "conservative")

    if not url or not user_id:
        raise HTTPException(status_code=400, detail="URL and user_id are required")

    # Validate strategy
    try:
        scraping_strategy = ProductionScrapingStrategy(strategy.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Choose from: {[s.value for s in ProductionScrapingStrategy]}",
        )

    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    logger.info(
        "Production scraping request",
        url=url,
        user_id=user_id,
        strategy=scraping_strategy.value,
    )

    # Perform production-grade scraping
    result = await production_scraper.scrape_with_production_grade_handling(
        url, user_id, legal_basis, scraping_strategy
    )

    return JSONResponse(content=result)


@app.get("/production/analytics")
async def get_production_analytics(days: int = 7):
    """Get production analytics and performance metrics"""
    try:
        analytics = production_scraper.get_production_analytics(days)
        return analytics
    except Exception as e:
        logger.error("Production analytics failed", error=str(e))
        raise HTTPException(
            status_code=500, detail="Failed to retrieve production analytics"
        )


@app.post("/production/strategy")
async def update_production_strategy(request: Dict[str, Any]):
    """Update production scraping strategy"""
    strategy = request.get("strategy")

    if not strategy:
        raise HTTPException(status_code=400, detail="Strategy is required")

    try:
        new_strategy = ProductionScrapingStrategy(strategy.lower())
        old_strategy = production_scraper.current_strategy
        production_scraper.current_strategy = new_strategy

        logger.info("Production strategy updated", new_strategy=new_strategy.value)

        return {
            "status": "updated",
            "previous_strategy": old_strategy.value,
            "new_strategy": new_strategy.value,
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Choose from: {[s.value for s in ProductionScrapingStrategy]}",
        )


@app.get("/production/strategies")
async def get_production_strategies():
    """Get available production strategies"""
    descriptions = {
        ProductionScrapingStrategy.CONSERVATIVE: "Low risk, slow pace - ideal for sensitive sites",
        ProductionScrapingStrategy.BALANCED: "Moderate risk, good pace - balanced approach",
        ProductionScrapingStrategy.AGGRESSIVE: "High risk, fast pace - maximum speed",
        ProductionScrapingStrategy.ADAPTIVE: "AI-driven, dynamic adjustment - smart optimization",
    }

    return {
        "strategies": [
            {
                "name": strategy.value,
                "description": descriptions.get(strategy, "Unknown strategy"),
            }
            for strategy in ProductionScrapingStrategy
        ],
        "current_strategy": production_scraper.current_strategy.value,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
