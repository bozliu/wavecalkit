from __future__ import annotations

from collections.abc import Iterable

from wavecal.geo import haversine_km
from wavecal.models import AltimeterRecord, BuoyRecord, CollocationPair, WindowSpec
from wavecal.timeutil import parse_time_window


def parse_window_specs(items: Iterable[str]) -> list[WindowSpec]:
    specs: list[WindowSpec] = []
    for item in items:
        name = item.strip().replace("_", "-").replace("km", "")
        inner_text, outer_text = name.split("-", 1)
        inner = float(inner_text)
        outer = float(outer_text)
        specs.append(WindowSpec(name=f"{inner_text}-{outer_text}km", inner_km=inner, outer_km=outer))
    return specs


def assign_window(distance_km: float, specs: Iterable[WindowSpec]) -> str | None:
    for spec in specs:
        if spec.contains(distance_km):
            return spec.name
    return None


def collocate(
    altimeter: Iterable[AltimeterRecord],
    buoys: Iterable[BuoyRecord],
    *,
    station_lat: float,
    station_lon: float,
    windows: list[WindowSpec],
    time_window: str = "exact",
) -> list[CollocationPair]:
    tolerance_minutes = parse_time_window(time_window)
    buoy_records = sorted(list(buoys), key=lambda item: item.time)
    pairs: list[CollocationPair] = []

    for alt in altimeter:
        if alt.lat is None or alt.lon is None:
            if alt.window_name is None:
                continue
            distance_km = -1.0
            window_name = alt.window_name
        else:
            distance_km = haversine_km(station_lat, station_lon, alt.lat, alt.lon)
            window_name = alt.window_name or assign_window(distance_km, windows)
            if window_name is None:
                continue

        nearest: tuple[float, BuoyRecord] | None = None
        for buoy in buoy_records:
            delta_minutes = abs((alt.time - buoy.time).total_seconds()) / 60.0
            if tolerance_minutes == 0.0 and delta_minutes != 0.0:
                continue
            if tolerance_minutes > 0.0 and delta_minutes > tolerance_minutes:
                continue
            if nearest is None or delta_minutes < nearest[0]:
                nearest = (delta_minutes, buoy)

        if nearest is None:
            continue
        pairs.append(
            CollocationPair(
                altimeter=alt,
                buoy=nearest[1],
                distance_km=distance_km,
                delta_time_minutes=nearest[0],
                window_name=window_name,
            )
        )

    return pairs
