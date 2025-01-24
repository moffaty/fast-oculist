from fastapi import APIRouter

from api.endpoint.index import router as index_router
from api.endpoint.navigator.router import router as navigator_router


router = APIRouter()
router.include_router(index_router)
router.include_router(navigator_router)
