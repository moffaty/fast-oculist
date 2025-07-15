from fastapi import APIRouter

from api.endpoint.navigator import navigator


router = APIRouter()
router.include_router(navigator.router)
