"""
Health check endpoints for monitoring service status.

Includes IP-based rate limiting to prevent abuse.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.redis import redis_client
from app.core.ip_rate_limit import ip_rate_limit_dep
from app.core.logging import get_logger
from app.database import supabase

logger = get_logger(__name__)

router = APIRouter(
    tags=["Health"],
    dependencies=[Depends(ip_rate_limit_dep)],
)


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns service status and version information.
    """
    return {"status": "healthy", "service": "statishub-api", "version": "1.0.0"}


@router.get("/health/redis")
async def health_check_redis():
    """
    Check Redis connection health.

    Returns:
        dict: Redis connection status

    Raises:
        HTTPException: If Redis is unavailable
    """
    try:
        redis_client.ping()
        return {"status": "healthy", "service": "redis", "message": "Redis connection OK"}
    except Exception as e:
        # Log full error internally but return generic message
        logger.error(f"Redis health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Redis service unavailable")


@router.get("/health/database")
async def health_check_database():
    """
    Check Supabase database connection health.

    Returns:
        dict: Database connection status

    Raises:
        HTTPException: If database is unavailable
    """
    try:
        # Simple query to test connection
        result = supabase.table("organization_information").select("taxcode").limit(1).execute()
        return {"status": "healthy", "service": "supabase", "message": "Database connection OK"}
    except Exception as e:
        # Log full error internally but return generic message
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
