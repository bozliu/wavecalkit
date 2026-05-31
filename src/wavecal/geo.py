from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0088


def west_longitude_to_360(lon_west_degrees: float) -> float:
    """Convert a west-longitude magnitude to a 0-360 east-positive value."""
    return (360.0 - abs(lon_west_degrees)) % 360.0


def normalize_longitude_180(lon: float) -> float:
    """Normalize longitude into [-180, 180)."""
    normalized = ((lon + 180.0) % 360.0) - 180.0
    if normalized == -180.0:
        return 180.0
    return normalized


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    lon1 = normalize_longitude_180(lon1)
    lon2 = normalize_longitude_180(lon2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_KM * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
