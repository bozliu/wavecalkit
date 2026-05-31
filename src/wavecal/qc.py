from __future__ import annotations

import math
from collections.abc import Iterable

from wavecal.models import AltimeterRecord, BuoyRecord


def filter_altimeter(
    records: Iterable[AltimeterRecord],
    *,
    min_swh_numval: int | None = None,
    min_swh_m: float | None = None,
    max_swh_m: float | None = None,
    allowed_passes: set[int] | None = None,
    reject_quality_flags: set[str] | None = None,
    reject_rain_flags: set[str] | None = None,
    reject_ice_flags: set[str] | None = None,
    reject_land_flags: set[str] | None = None,
) -> list[AltimeterRecord]:
    filtered: list[AltimeterRecord] = []
    for record in records:
        if not _finite(record.swh_m):
            continue
        if min_swh_numval is not None and record.swh_numval is not None:
            if record.swh_numval < min_swh_numval:
                continue
        if min_swh_m is not None and record.swh_m < min_swh_m:
            continue
        if max_swh_m is not None and record.swh_m > max_swh_m:
            continue
        if allowed_passes and record.pass_number is not None and record.pass_number not in allowed_passes:
            continue
        if _flag_rejected(record.quality_flag, reject_quality_flags):
            continue
        if _flag_rejected(record.rain_flag, reject_rain_flags):
            continue
        if _flag_rejected(record.ice_flag, reject_ice_flags):
            continue
        if _flag_rejected(record.land_flag, reject_land_flags):
            continue
        filtered.append(record)
    return filtered


def filter_buoy(
    records: Iterable[BuoyRecord],
    *,
    min_swh_m: float | None = None,
    max_swh_m: float | None = None,
    reject_qc_flags: set[str] | None = None,
    max_swh_jump_m: float | None = None,
    jump_window_hours: float = 2.0,
) -> list[BuoyRecord]:
    source_records = list(records)
    if max_swh_jump_m is not None:
        source_records = sorted(source_records, key=lambda item: (item.station_id, item.time))

    filtered: list[BuoyRecord] = []
    previous_by_station: dict[str, BuoyRecord] = {}
    for record in source_records:
        if not _finite(record.swh_m):
            continue
        if min_swh_m is not None and record.swh_m < min_swh_m:
            continue
        if max_swh_m is not None and record.swh_m > max_swh_m:
            continue
        if _flag_rejected(record.qc_flag, reject_qc_flags):
            continue
        previous = previous_by_station.get(record.station_id)
        if previous is not None and max_swh_jump_m is not None:
            delta_hours = abs((record.time - previous.time).total_seconds()) / 3600.0
            if delta_hours <= jump_window_hours:
                if abs(record.swh_m - previous.swh_m) > max_swh_jump_m:
                    continue
        filtered.append(record)
        previous_by_station[record.station_id] = record
    return filtered


def _finite(value: float) -> bool:
    return math.isfinite(value)


def _flag_rejected(value: str | None, rejected: set[str] | None) -> bool:
    if not value or not rejected:
        return False
    normalized = {item.strip().lower() for item in rejected}
    return value.strip().lower() in normalized
