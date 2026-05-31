from __future__ import annotations

from collections.abc import Iterable

from wavecal.models import AltimeterRecord, BuoyRecord


def filter_altimeter(
    records: Iterable[AltimeterRecord],
    *,
    min_swh_numval: int | None = None,
    min_swh_m: float | None = None,
    max_swh_m: float | None = None,
    allowed_passes: set[int] | None = None,
) -> list[AltimeterRecord]:
    filtered: list[AltimeterRecord] = []
    for record in records:
        if min_swh_numval is not None and record.swh_numval is not None:
            if record.swh_numval < min_swh_numval:
                continue
        if min_swh_m is not None and record.swh_m < min_swh_m:
            continue
        if max_swh_m is not None and record.swh_m > max_swh_m:
            continue
        if allowed_passes and record.pass_number is not None and record.pass_number not in allowed_passes:
            continue
        filtered.append(record)
    return filtered


def filter_buoy(
    records: Iterable[BuoyRecord],
    *,
    min_swh_m: float | None = None,
    max_swh_m: float | None = None,
    reject_qc_flags: set[str] | None = None,
) -> list[BuoyRecord]:
    filtered: list[BuoyRecord] = []
    reject_qc_flags = reject_qc_flags or set()
    for record in records:
        if min_swh_m is not None and record.swh_m < min_swh_m:
            continue
        if max_swh_m is not None and record.swh_m > max_swh_m:
            continue
        if record.qc_flag and record.qc_flag in reject_qc_flags:
            continue
        filtered.append(record)
    return filtered
