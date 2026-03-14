"""API v1 router."""

from fastapi import APIRouter

from meridian_api.api.v1.predictions import router as predictions_router

router = APIRouter()
router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
