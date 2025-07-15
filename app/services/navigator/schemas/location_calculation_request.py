from pydantic import BaseModel
from services.navigator.schemas import NavigationPoint


class LocationCalculationRequest(BaseModel):
    point1: NavigationPoint
    point2: NavigationPoint
