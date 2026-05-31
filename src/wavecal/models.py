from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AltimeterRecord:
    time: datetime
    lat: float | None
    lon: float | None
    swh_m: float
    swh_rms_m: float | None = None
    swh_numval: int | None = None
    pass_number: int | None = None
    cycle_number: int | None = None
    mission: str = "unknown"
    source_file: str = ""
    window_name: str | None = None


@dataclass(frozen=True)
class BuoyRecord:
    time: datetime
    station_id: str
    lat: float | None
    lon: float | None
    swh_m: float
    period_s: float | None = None
    direction_deg: float | None = None
    qc_flag: str | None = None


@dataclass(frozen=True)
class WindowSpec:
    name: str
    inner_km: float
    outer_km: float

    def contains(self, distance_km: float) -> bool:
        return self.inner_km <= distance_km < self.outer_km


@dataclass(frozen=True)
class CollocationPair:
    altimeter: AltimeterRecord
    buoy: BuoyRecord
    distance_km: float
    delta_time_minutes: float
    window_name: str


@dataclass(frozen=True)
class Metrics:
    window_name: str
    n: int
    r: float
    signed_bias_m: float
    mae_m: float
    rmse_m: float
    scatter_index: float
    slope: float
    intercept: float
    slope_ci95: float
    intercept_ci95: float
    model: str = "linear"
