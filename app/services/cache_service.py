"""Caching service for Redis-based caching operations."""

import json
import logging
from typing import Optional, Any, Dict, List
from uuid import UUID

import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis-based caching service for application data.
    
    Provides async caching operations with automatic serialization/deserialization.
    Gracefully handles Redis unavailability (returns None, logs error).
    """

    def __init__(self):
        """Initialize cache service with Redis connection."""
        self._redis: Optional[redis.Redis] = None
        self._enabled = True

    async def _get_redis(self) -> Optional[redis.Redis]:
        """
        Get Redis connection, creating if needed.
        
        Returns:
            Redis client or None if unavailable
        """
        if self._redis is None:
            try:
                redis_url = settings.CELERY_BROKER_URL or "redis://localhost:6379/0"
                self._redis = redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=False,  # We'll handle encoding ourselves
                )
                # Test connection
                await self._redis.ping()
                logger.info("Redis cache connection established")
            except Exception as e:
                logger.warning(f"Redis cache unavailable: {str(e)}. Caching disabled.")
                self._enabled = False
                self._redis = None
        
        return self._redis if self._enabled else None

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data as dict or None if not found/unavailable
        """
        try:
            redis_client = await self._get_redis()
            if not redis_client:
                return None
            
            data = await redis_client.get(key)
            if data:
                return json.loads(data.decode("utf-8"))
            return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: int = 3600,
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Data to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            redis_client = await self._get_redis()
            if not redis_client:
                return False
            
            serialized = json.dumps(value, default=str)  # default=str handles UUID, datetime
            await redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            redis_client = await self._get_redis()
            if not redis_client:
                return False
            
            deleted = await redis_client.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {str(e)}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "dish:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            redis_client = await self._get_redis()
            if not redis_client:
                return 0
            
            keys = []
            async for key in redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete_pattern error for pattern '{pattern}': {str(e)}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            redis_client = await self._get_redis()
            if not redis_client:
                return False
            
            return await redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {str(e)}")
            return False

    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: int = 3600,
    ) -> Optional[Dict[str, Any]]:
        """
        Get from cache or fetch and cache.
        
        Args:
            key: Cache key
            fetch_func: Async function to fetch data if not cached
            ttl: Time to live in seconds
            
        Returns:
            Cached or fetched data
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Fetch and cache
        try:
            data = await fetch_func()
            if data:
                # Convert to dict if needed
                if hasattr(data, "dict"):
                    data_dict = data.dict()
                elif hasattr(data, "model_dump"):
                    data_dict = data.model_dump()
                elif isinstance(data, dict):
                    data_dict = data
                else:
                    # Try to serialize
                    data_dict = json.loads(json.dumps(data, default=str))
                
                await self.set(key, data_dict, ttl)
                return data_dict
        except Exception as e:
            logger.error(f"Cache get_or_set error for key '{key}': {str(e)}")
        
        return None

    async def invalidate_dish(self, dish_id: UUID):
        """Invalidate all cache entries for a dish."""
        await self.delete_pattern(f"dish:{dish_id}*")
        await self.delete_pattern("dish:list:*")
        await self.delete_pattern("dish:featured:*")
        await self.delete_pattern("dish:top-rated:*")

    async def invalidate_restaurant(self, restaurant_id: UUID):
        """Invalidate all cache entries for a restaurant."""
        await self.delete_pattern(f"restaurant:{restaurant_id}*")
        await self.delete_pattern("restaurant:list:*")
        await self.delete_pattern("dish:restaurant:{restaurant_id}*")

    async def invalidate_cuisine(self, cuisine_id: UUID):
        """Invalidate all cache entries for a cuisine."""
        await self.delete_pattern(f"cuisine:{cuisine_id}*")
        await self.delete_pattern("cuisine:list:*")
        await self.delete_pattern("dish:cuisine:{cuisine_id}*")

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Global cache service instance
_cache_service: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """Get or create global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

