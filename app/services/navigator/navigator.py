import math
from typing import Any

from pyproj import CRS, Transformer

from .schemas import NavigationPoint


class Navigator:
    def __init__(self) -> None:
        self.wgs84 = CRS.from_epsg(4326)
        self.utm = CRS.from_epsg(32636)
        self.to_utm = Transformer.from_crs(self.wgs84, self.utm, always_xy=True)
        self.to_wgs84 = Transformer.from_crs(self.utm, self.wgs84, always_xy=True)

    def calculate_navigation_point(self, point1: NavigationPoint, point2: NavigationPoint) -> NavigationPoint:
        """
        Calculate navigation point using bearings from optical navigation cameras.

        Args:
            point1: First reference navigation point with camera bearing
            point2: Second reference navigation point with camera bearing

        Returns:
            Calculated NavigationPoint with precise geospatial coordinates
        """
        # Convert points to UTM
        x1, y1 = self.__convert_to_utm(point1)
        x2, y2 = self.__convert_to_utm(point2)

        # Calculate distance between points
        distance = self.__calculate_distance(x1, y1, x2, y2)

        # Calculate average bearing
        avg_bearing = self.__calculate_average_bearing(point1, point2)

        # Calculate new point coordinates
        new_x, new_y = self.__project_new_point(x1, y1, distance, avg_bearing)

        # Convert back to WGS84
        new_lon, new_lat = self.to_wgs84.transform(new_x, new_y)

        return NavigationPoint(lat=new_lat, lon=new_lon, bearing=math.degrees(avg_bearing))

    def __convert_to_utm(self, point: NavigationPoint) -> tuple:
        """Convert WGS84 coordinates to UTM coordinates."""
        utm_coord: tuple[Any, Any] = self.to_utm.transform(point.lon, point.lat)
        return utm_coord

    def __calculate_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def __calculate_average_bearing(self, point1: NavigationPoint, point2: NavigationPoint) -> float:
        """Calculate average bearing from two navigation points."""
        bearing1 = point1.bearing or 0
        bearing2 = point2.bearing or 0
        return math.radians((bearing1 + bearing2) / 2)

    def __project_new_point(self, x1: float, y1: float, distance: float, bearing: float) -> tuple:
        """Calculate new point coordinates based on distance and bearing."""
        new_x = x1 + distance * math.cos(bearing)
        new_y = y1 + distance * math.sin(bearing)
        return new_x, new_y
