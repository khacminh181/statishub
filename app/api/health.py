"""
Health check endpoints for monitoring service status.
"""
from fastapi import APIRouter, HTTPException
from app.core.redis import redis_client
from app.database import supabase
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "service": "statishub-api",
        "version": "1.0.0"
    }


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
        return {
            "status": "healthy",
            "service": "redis",
            "message": "Redis connection OK"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Redis unavailable: {str(e)}"
        )


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
        return {
            "status": "healthy",
            "service": "supabase",
            "message": "Database connection OK"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )
