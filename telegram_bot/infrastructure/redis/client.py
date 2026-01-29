import logging
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from core.config import settings

logger = logging.getLogger()

pool = ConnectionPool.from_url(str(settings.redis.dsn))
redis = Redis(connection_pool=pool)

async def check_redis():
	try:
		await redis.ping()
		logger.info("⚡️ Redis connected")
	except Exception as e:
		logger.info("Redis connection failed")
		raise e
