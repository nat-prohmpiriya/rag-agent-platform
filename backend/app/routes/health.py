from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """
    Readiness check endpoint.
    Can be extended to check database, external services, etc.
    """
    # TODO: Add database connection check
    # TODO: Add LiteLLM connection check
    return {"status": "ready"}
