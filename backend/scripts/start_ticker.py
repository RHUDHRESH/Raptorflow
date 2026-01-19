"""
Ticker Entry Point - Absolute Infinity
======================================

Starts the background ticker service for RaptorFlow.
Ensures that fluid rescheduling and task roll-over are active.
"""

import asyncio
import logging
import sys
import os

# Add root directory to path
sys.path.append(os.getcwd())

from backend.ticker import ticker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ticker_starter")

async def main():
    logger.info("⚡ Starting Absolute Infinity Strategic Ticker...")
    try:
        await ticker.start_ticker()
    except Exception as e:
        logger.error(f"🔥 Critical Ticker Failure: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Ticker stopped by user.")