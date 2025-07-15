from fastapi import APIRouter
from services.navigator import Navigator
from services.navigator.schemas.navigation_point import NavigationPoint
from services.navigator.schemas.location_calculation_request import LocationCalculationRequest


router = APIRouter(tags=["Navigator"])


@router.post("/navigate")
async def calculate_location(request: LocationCalculationRequest) -> NavigationPoint:
    navigator = Navigator()
    intersection = navigator.calculate_navigation_point(request.point1, request.point2)

    return intersection
