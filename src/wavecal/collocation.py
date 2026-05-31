from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from statistics import mean, median

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
    aggregation: str = "nearest",
) -> list[CollocationPair]:
    if aggregation not in {"nearest", "mean", "median"}:
        raise ValueError("aggregation must be one of: nearest, mean, median")
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

    return aggregate_collocations(pairs, aggregation)


def aggregate_collocations(
    pairs: Iterable[CollocationPair],
    aggregation: str = "nearest",
) -> list[CollocationPair]:
    if aggregation not in {"nearest", "mean", "median"}:
        raise ValueError("aggregation must be one of: nearest, mean, median")

    grouped: dict[tuple[str, object, str], list[CollocationPair]] = {}
    for pair in pairs:
        key = (pair.buoy.station_id, pair.buoy.time, pair.window_name)
        grouped.setdefault(key, []).append(pair)

    aggregated: list[CollocationPair] = []
    for key in sorted(grouped, key=lambda item: (str(item[2]), item[1], item[0])):
        group = grouped[key]
        if len(group) == 1:
            aggregated.append(
                replace(group[0], aggregation=aggregation, matched_altimeter_count=1)
            )
            continue

        nearest = min(group, key=lambda item: (item.delta_time_minutes, max(item.distance_km, 0.0)))
        if aggregation == "nearest":
            aggregated.append(
                replace(nearest, aggregation="nearest", matched_altimeter_count=len(group))
            )
            continue

        reducer = mean if aggregation == "mean" else median
        altimeter = replace(
            nearest.altimeter,
            swh_m=float(reducer([pair.altimeter.swh_m for pair in group])),
            lat=_reduce_optional([pair.altimeter.lat for pair in group], reducer),
            lon=_reduce_optional([pair.altimeter.lon for pair in group], reducer),
            swh_rms_m=_reduce_optional([pair.altimeter.swh_rms_m for pair in group], reducer),
            swh_numval=_reduce_optional_int([pair.altimeter.swh_numval for pair in group], reducer),
            source_file=f"aggregated:{len(group)}",
        )
        aggregated.append(
            replace(
                nearest,
                altimeter=altimeter,
                distance_km=float(reducer([pair.distance_km for pair in group])),
                delta_time_minutes=float(reducer([pair.delta_time_minutes for pair in group])),
                aggregation=aggregation,
                matched_altimeter_count=len(group),
            )
        )

    return aggregated


def _reduce_optional(values: list[float | None], reducer) -> float | None:
    present = [value for value in values if value is not None]
    return None if not present else float(reducer(present))


def _reduce_optional_int(values: list[int | None], reducer) -> int | None:
    present = [value for value in values if value is not None]
    return None if not present else int(round(float(reducer(present))))
