from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable

import numpy as np

from wavecal.models import CollocationPair, Metrics
from wavecal.wave import deep_water_wave_power_kw_per_m


def linear_fit(buoy_swh: np.ndarray, altimeter_swh: np.ndarray) -> tuple[float, float]:
    if len(buoy_swh) < 2:
        return 0.0, float(altimeter_swh[0]) if len(altimeter_swh) else 0.0
    slope, intercept = np.polyfit(buoy_swh, altimeter_swh, 1)
    return float(slope), float(intercept)


def _confidence_intervals(
    x: np.ndarray,
    y: np.ndarray,
    slope: float,
    intercept: float,
) -> tuple[float, float]:
    n = len(x)
    if n < 3:
        return 0.0, 0.0
    residuals = y - (slope * x + intercept)
    s_err = math.sqrt(float(np.sum(residuals**2)) / (n - 2))
    x_mean = float(np.mean(x))
    ssx = float(np.sum((x - x_mean) ** 2))
    if ssx == 0.0:
        return 0.0, 0.0
    slope_se = s_err / math.sqrt(ssx)
    intercept_se = s_err * math.sqrt((1.0 / n) + (x_mean**2 / ssx))
    return 1.96 * slope_se, 1.96 * intercept_se


def compute_metrics_for_pairs(
    pairs: Iterable[CollocationPair],
    *,
    model: str = "linear",
) -> list[Metrics]:
    grouped: dict[str, list[CollocationPair]] = defaultdict(list)
    for pair in pairs:
        grouped[pair.window_name].append(pair)

    results: list[Metrics] = []
    for window_name in sorted(grouped, key=_window_sort_key):
        window_pairs = grouped[window_name]
        alt = np.array([pair.altimeter.swh_m for pair in window_pairs], dtype=float)
        buoy = np.array([pair.buoy.swh_m for pair in window_pairs], dtype=float)
        diff = alt - buoy
        n = len(window_pairs)
        r = float(np.corrcoef(buoy, alt)[0, 1]) if n > 1 else 0.0
        signed_bias = float(np.mean(diff)) if n else 0.0
        mae = float(np.mean(np.abs(diff))) if n else 0.0
        rmse = float(math.sqrt(float(np.mean(diff**2)))) if n else 0.0
        scatter_index = rmse / float(np.mean(buoy)) if n and float(np.mean(buoy)) != 0.0 else 0.0
        slope, intercept = linear_fit(buoy, alt)
        slope_ci95, intercept_ci95 = _confidence_intervals(buoy, alt, slope, intercept)
        wave_power_values = [
            value
            for value in (
                deep_water_wave_power_kw_per_m(pair.buoy.swh_m, pair.buoy.period_s)
                for pair in window_pairs
            )
            if value is not None
        ]
        results.append(
            Metrics(
                window_name=window_name,
                n=n,
                r=r,
                signed_bias_m=signed_bias,
                mae_m=mae,
                rmse_m=rmse,
                scatter_index=scatter_index,
                slope=slope,
                intercept=intercept,
                slope_ci95=slope_ci95,
                intercept_ci95=intercept_ci95,
                model=model,
                mean_buoy_wave_power_kw_per_m=(
                    float(np.mean(wave_power_values)) if wave_power_values else None
                ),
            )
        )
    return results


def _window_sort_key(name: str) -> tuple[float, str]:
    try:
        return (float(name.split("-", 1)[0]), name)
    except ValueError:
        return (999999.0, name)
