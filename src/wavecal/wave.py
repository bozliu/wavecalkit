from __future__ import annotations

import math

WATER_DENSITY_KG_M3 = 1025.0
GRAVITY_M_S2 = 9.80665


def deep_water_wave_power_kw_per_m(
    swh_m: float | None,
    energy_period_s: float | None,
) -> float | None:
    """Estimate deep-water wave power from significant wave height and period.

    This is a screening calculation for analyst reports. It is not a substitute
    for site-specific spectral modelling or certified yield assessment.
    """
    if swh_m is None or energy_period_s is None:
        return None
    if not math.isfinite(swh_m) or not math.isfinite(energy_period_s):
        return None
    if swh_m < 0.0 or energy_period_s <= 0.0:
        return None
    watts_per_m = WATER_DENSITY_KG_M3 * GRAVITY_M_S2**2 * swh_m**2 * energy_period_s
    watts_per_m /= 64.0 * math.pi
    return watts_per_m / 1000.0
