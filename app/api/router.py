from fastapi import APIRouter

from api.endpoint.navigator.router import router as navigator_router


router = APIRouter()
router.include_router(navigator_router)
