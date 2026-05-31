from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
from typing import Iterable

from wavecal.models import AltimeterRecord, BuoyRecord, CollocationPair, Metrics
from wavecal.timeutil import format_time, parse_time
from wavecal.wave import deep_water_wave_power_kw_per_m


def _float_or_none(value: object) -> float | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    return float(text)


def _int_or_none(value: object) -> int | None:
    parsed = _float_or_none(value)
    return None if parsed is None else int(parsed)


def _text_or_none(value: object) -> str | None:
    text = "" if value is None else str(value).strip()
    return text or None


def read_altimeter_csv(path: str | Path) -> list[AltimeterRecord]:
    records: list[AltimeterRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append(
                AltimeterRecord(
                    time=parse_time(row["time"]),
                    lat=_float_or_none(row.get("lat")),
                    lon=_float_or_none(row.get("lon")),
                    swh_m=float(row["swh_m"]),
                    swh_rms_m=_float_or_none(row.get("swh_rms_m")),
                    swh_numval=_int_or_none(row.get("swh_numval")),
                    pass_number=_int_or_none(row.get("pass_number")),
                    cycle_number=_int_or_none(row.get("cycle_number")),
                    mission=row.get("mission") or "unknown",
                    source_file=row.get("source_file") or str(path),
                    window_name=row.get("window_name") or None,
                    quality_flag=_text_or_none(row.get("quality_flag")),
                    rain_flag=_text_or_none(row.get("rain_flag")),
                    ice_flag=_text_or_none(row.get("ice_flag")),
                    land_flag=_text_or_none(row.get("land_flag")),
                )
            )
    return records


def read_buoy_csv(path: str | Path) -> list[BuoyRecord]:
    records: list[BuoyRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append(
                BuoyRecord(
                    time=parse_time(row["time"]),
                    station_id=row.get("station_id") or "unknown",
                    lat=_float_or_none(row.get("lat")),
                    lon=_float_or_none(row.get("lon")),
                    swh_m=float(row["swh_m"]),
                    period_s=_float_or_none(row.get("period_s")),
                    direction_deg=_float_or_none(row.get("direction_deg")),
                    qc_flag=row.get("qc_flag") or None,
                )
            )
    return records


def read_altimeter_netcdf(path: str | Path, *, mission: str = "unknown") -> list[AltimeterRecord]:
    """Read a user-supplied NetCDF file with common altimeter SWH fields.

    This adapter intentionally stays small: users can normalize richer products
    to CSV when provider-specific fields differ.
    """
    if importlib.util.find_spec("xarray") is None:
        raise ImportError("NetCDF support requires optional dependency: pip install '.[netcdf]'")
    import xarray as xr

    source = Path(path)
    with xr.open_dataset(source) as dataset:
        lat = dataset["lat"].values
        lon = dataset["lon"].values
        time = dataset["time"].values
        swh = dataset["swh_ku"].values if "swh_ku" in dataset else dataset["swh"].values
        swh_rms = dataset["swh_rms_ku"].values if "swh_rms_ku" in dataset else [None] * len(swh)
        swh_numval = (
            dataset["swh_numval_ku"].values if "swh_numval_ku" in dataset else [None] * len(swh)
        )
        pass_number = _dataset_value(dataset, "pass_number")
        cycle_number = _dataset_value(dataset, "cycle_number")
        return [
            AltimeterRecord(
                time=parse_time(time[index]),
                lat=float(lat[index]),
                lon=float(lon[index]),
                swh_m=float(swh[index]),
                swh_rms_m=None if swh_rms[index] is None else float(swh_rms[index]),
                swh_numval=None if swh_numval[index] is None else int(swh_numval[index]),
                pass_number=pass_number,
                cycle_number=cycle_number,
                mission=mission,
                source_file=str(source),
                quality_flag=_dataset_optional_text(dataset, "quality_flag", index),
                rain_flag=_dataset_optional_text(dataset, "rain_flag", index),
                ice_flag=_dataset_optional_text(dataset, "ice_flag", index),
                land_flag=_dataset_optional_text(dataset, "land_flag", index),
            )
            for index in range(len(swh))
        ]


def read_buoy_xls(path: str | Path, *, sheet_name: str | int = 0) -> list[BuoyRecord]:
    """Read a normalized Excel workbook with the same columns as buoy CSV."""
    if importlib.util.find_spec("xlrd") is None:
        raise ImportError("XLS support requires optional dependency: pip install '.[excel]'")
    import pandas as pd

    frame = pd.read_excel(path, sheet_name=sheet_name)
    required = {"time", "station_id", "swh_m"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"normalized buoy workbook missing columns: {missing}")
    return [
        BuoyRecord(
            time=parse_time(row["time"]),
            station_id=str(row["station_id"]),
            lat=_float_or_none(row.get("lat")),
            lon=_float_or_none(row.get("lon")),
            swh_m=float(row["swh_m"]),
            period_s=_float_or_none(row.get("period_s")),
            direction_deg=_float_or_none(row.get("direction_deg")),
            qc_flag=None if row.get("qc_flag") is None else str(row.get("qc_flag")),
        )
        for _, row in frame.iterrows()
    ]


def read_legacy_txt(
    path: str | Path,
    *,
    lat: float | None = None,
    lon: float | None = None,
    mission: str = "Jason-3",
    window_name: str | None = None,
) -> list[AltimeterRecord]:
    """Read legacy MATLAB parameter TXT files with stale 15-column headers.

    The active MATLAB code wrote four columns despite declaring a 15-column
    header: `swh_ku`, `swh_rms_ku`, `swh_numval_ku`, and `time`.
    """
    records: list[AltimeterRecord] = []
    source = Path(path)
    with source.open(encoding="utf-8", errors="replace") as handle:
        next(handle, None)
        for line in handle:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            records.append(
                AltimeterRecord(
                    time=parse_time(parts[3]),
                    lat=lat,
                    lon=lon,
                    swh_m=float(parts[0]),
                    swh_rms_m=float(parts[1]),
                    swh_numval=int(float(parts[2])),
                    mission=mission,
                    source_file=str(source),
                    window_name=window_name,
                )
            )
    return records


def _dataset_value(dataset, name: str) -> int | None:
    if name in dataset.attrs:
        return int(dataset.attrs[name])
    if name in dataset:
        values = dataset[name].values
        if getattr(values, "shape", ()) == ():
            return int(values)
        if len(values):
            return int(values[0])
    return None


def _dataset_optional_text(dataset, name: str, index: int) -> str | None:
    if name not in dataset:
        return None
    values = dataset[name].values
    try:
        value = values[index]
    except TypeError:
        value = values
    return _text_or_none(value)


def write_altimeter_csv(records: Iterable[AltimeterRecord], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "time",
        "lat",
        "lon",
        "swh_m",
        "swh_rms_m",
        "swh_numval",
        "pass_number",
        "cycle_number",
        "mission",
        "source_file",
        "window_name",
        "quality_flag",
        "rain_flag",
        "ice_flag",
        "land_flag",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "time": format_time(record.time),
                    "lat": record.lat if record.lat is not None else "",
                    "lon": record.lon if record.lon is not None else "",
                    "swh_m": record.swh_m,
                    "swh_rms_m": record.swh_rms_m if record.swh_rms_m is not None else "",
                    "swh_numval": record.swh_numval if record.swh_numval is not None else "",
                    "pass_number": record.pass_number if record.pass_number is not None else "",
                    "cycle_number": record.cycle_number if record.cycle_number is not None else "",
                    "mission": record.mission,
                    "source_file": record.source_file,
                    "window_name": record.window_name or "",
                    "quality_flag": record.quality_flag or "",
                    "rain_flag": record.rain_flag or "",
                    "ice_flag": record.ice_flag or "",
                    "land_flag": record.land_flag or "",
                }
            )


def write_buoy_csv(records: Iterable[BuoyRecord], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["time", "station_id", "lat", "lon", "swh_m", "period_s", "direction_deg", "qc_flag"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "time": format_time(record.time),
                    "station_id": record.station_id,
                    "lat": record.lat if record.lat is not None else "",
                    "lon": record.lon if record.lon is not None else "",
                    "swh_m": record.swh_m,
                    "period_s": record.period_s if record.period_s is not None else "",
                    "direction_deg": record.direction_deg if record.direction_deg is not None else "",
                    "qc_flag": record.qc_flag or "",
                }
            )


def write_collocations_csv(pairs: Iterable[CollocationPair], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "window_name",
        "time_altimeter",
        "time_buoy",
        "delta_time_minutes",
        "distance_km",
        "altimeter_swh_m",
        "buoy_swh_m",
        "mission",
        "station_id",
        "source_file",
        "aggregation",
        "matched_altimeter_count",
        "buoy_period_s",
        "buoy_wave_power_kw_per_m",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for pair in pairs:
            writer.writerow(
                {
                    "window_name": pair.window_name,
                    "time_altimeter": format_time(pair.altimeter.time),
                    "time_buoy": format_time(pair.buoy.time),
                    "delta_time_minutes": f"{pair.delta_time_minutes:.6f}",
                    "distance_km": f"{pair.distance_km:.6f}",
                    "altimeter_swh_m": f"{pair.altimeter.swh_m:.6f}",
                    "buoy_swh_m": f"{pair.buoy.swh_m:.6f}",
                    "mission": pair.altimeter.mission,
                    "station_id": pair.buoy.station_id,
                    "source_file": pair.altimeter.source_file,
                    "aggregation": pair.aggregation,
                    "matched_altimeter_count": pair.matched_altimeter_count,
                    "buoy_period_s": _format_optional_float(pair.buoy.period_s),
                    "buoy_wave_power_kw_per_m": _format_optional_float(
                        deep_water_wave_power_kw_per_m(pair.buoy.swh_m, pair.buoy.period_s)
                    ),
                }
            )


def _format_optional_float(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def read_collocations_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_metrics_csv(metrics: Iterable[Metrics], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(Metrics.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in metrics:
            writer.writerow({field: getattr(item, field) for field in fields})


def read_metrics_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
