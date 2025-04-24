from fastapi import APIRouter

from api.endpoint.camera.camera import router as camera_router
from api.endpoint.navigator.router import router as navigator_router


router = APIRouter()
router.include_router(navigator_router)
router.include_router(camera_router)
