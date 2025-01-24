from typing import Optional

from pydantic import BaseModel


class NavigationPoint(BaseModel):
    lat: float = 0
    lon: float = 0
    bearing: Optional[float] = 0
