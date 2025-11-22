"""
Twitter/X Agent - Posts tweets and threads using Twitter API v2.
Handles character limits, threads, and media attachments.
"""

import structlog
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from backend.services.social.twitter import twitter_service
from backend.models.content import ContentVariant
from backend.utils.correlation import get_correlation_id
from backend.utils.queue import redis_queue

logger = structlog.get_logger(__name__)


class TwitterAgent:
    """
    Publishes content to Twitter/X.
    Handles 280-char limit, threads, and rate limiting.
    """
    
    def __init__(self):
        self.twitter = twitter_service
        self.char_limit = 280
    
    async def format_tweet(self, variant: ContentVariant) -> str:
        """
        Formats content for Twitter's 280-character limit.
        """
        content = variant.content
        
        # Truncate if needed
        if len(content) > self.char_limit:
            content = content[:277] + "..."
            logger.warning("Tweet truncated", original_length=len(variant.content))
        
        return content
    
    async def split_into_thread(self, content: str) -> List[str]:
        """
        Splits long content into a Twitter thread.
        """
        if len(content) <= self.char_limit:
            return [content]
        
        # Split by paragraphs or sentences
        paragraphs = content.split("\n\n")
        tweets = []
        current_tweet = ""
        
        for para in paragraphs:
            if len(current_tweet) + len(para) + 2 <= self.char_limit - 10:  # Leave room for numbering
                current_tweet += para + "\n\n"
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = para + "\n\n"
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Add numbering
        if len(tweets) > 1:
            numbered_tweets = [f"{i+1}/{len(tweets)}\n\n{tweet}" for i, tweet in enumerate(tweets)]
            return numbered_tweets
        
        return tweets
    
    async def post_to_twitter(
        self,
        variant: ContentVariant,
        workspace_id: UUID,
        account_id: Optional[str] = None,
        as_thread: bool = False,
        schedule_time: Optional[datetime] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Posts content to Twitter.
        
        Args:
            variant: Content to post
            workspace_id: User's workspace
            account_id: Twitter account ID
            as_thread: Whether to post as thread if too long
            schedule_time: Optional scheduled post time
            
        Returns:
            Dict with tweet_id(s), status, url(s)
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Posting to Twitter", as_thread=as_thread, scheduled=schedule_time is not None, correlation_id=correlation_id)
        
        # Determine if threading is needed
        content = variant.content
        tweets = [content] if len(content) <= self.char_limit else (await self.split_into_thread(content) if as_thread else [await self.format_tweet(variant)])
        
        # If scheduled, queue the task
        if schedule_time and schedule_time > datetime.utcnow():
            await redis_queue.enqueue(
                task_name="publish_twitter",
                payload={
                    "tweets": tweets,
                    "workspace_id": str(workspace_id),
                    "account_id": account_id,
                    "schedule_time": schedule_time.isoformat()
                },
                priority="medium"
            )
            logger.info("Twitter post scheduled", schedule_time=schedule_time, tweets=len(tweets), correlation_id=correlation_id)
            return {
                "status": "scheduled",
                "schedule_time": schedule_time.isoformat(),
                "tweet_count": len(tweets),
                "message": "Tweet(s) queued for publishing"
            }
        
        # Post immediately
        try:
            if len(tweets) == 1:
                # Single tweet
                result = await self.twitter.create_tweet(
                    text=tweets[0],
                    workspace_id=workspace_id,
                    account_id=account_id
                )
                
                logger.info("Tweet published", tweet_id=result.get("id"), correlation_id=correlation_id)
                return {
                    "status": "published",
                    "tweet_id": result.get("id"),
                    "url": result.get("url"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Thread
                result = await self.twitter.create_thread(
                    tweets=tweets,
                    workspace_id=workspace_id,
                    account_id=account_id
                )
                
                logger.info("Thread published", tweet_count=len(tweets), correlation_id=correlation_id)
                return {
                    "status": "published",
                    "tweet_ids": result.get("ids", []),
                    "thread_url": result.get("thread_url"),
                    "tweet_count": len(tweets),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error("Failed to post to Twitter", error=str(e), correlation_id=correlation_id)
            return {
                "status": "failed",
                "error": str(e)
            }


twitter_agent = TwitterAgent()

