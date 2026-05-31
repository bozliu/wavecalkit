"""Static Matplotlib dashboard for `mpl-animator` variable sweeps.

The installed `mpl-animator` 0.1.x CLI writes an animated Python script first.
Run the emitted script to create the GIF/MP4:

    mpl-animator scripts/render_workflow_animation.py \
      --var frame --range "0,2*pi" --frames 60 \
      --out outputs/scilly/mpl_animator.gif
    python render_workflow_animation_animated.py
"""

import math
import os

import matplotlib.pyplot as plt
import numpy as np

from wavecal.pipeline import analyze_config


frame = 0.0
config_path = os.environ.get("WAVECAL_ANIMATION_CONFIG", "examples/scilly_jason3.yml")
analysis = analyze_config(config_path)
pairs = analysis.pairs
station = analysis.config["station"]

phase = frame / (2.0 * math.pi) if frame > 1.0 else frame
phase = max(0.0, min(float(phase), 1.0))
visible_count = max(1, math.ceil(len(pairs) * phase))
visible_pairs = pairs[:visible_count]

fig = plt.figure(figsize=(10.4, 6.2), dpi=110)
ax_map = fig.add_subplot(2, 2, 1)
ax_scatter = fig.add_subplot(2, 2, 2)
ax_polar = fig.add_subplot(2, 2, 3, projection="polar")
ax_depth = fig.add_subplot(2, 2, 4)
fig.suptitle("WaveCalKit Python-native validation workflow", fontsize=14, weight="bold")

station_lon = float(station["lon"])
station_lat = float(station["lat"])
lons = [pair.altimeter.lon for pair in visible_pairs if pair.altimeter.lon is not None]
lats = [pair.altimeter.lat for pair in visible_pairs if pair.altimeter.lat is not None]
ax_map.scatter([station_lon], [station_lat], marker="^", s=120, color="#d9534f", label="buoy")
if lons and lats:
    ax_map.plot(lons, lats, color="#2a7187", alpha=0.45, linewidth=1.0)
    ax_map.scatter(lons, lats, s=28, color="#176f53", edgecolor="white", linewidth=0.4)
ax_map.set_title("geospatial collocation")
ax_map.set_xlabel("longitude")
ax_map.set_ylabel("latitude")
ax_map.grid(True, alpha=0.22)
ax_map.legend(loc="best", fontsize=7)

windows = sorted({pair.window_name for pair in visible_pairs})
colors = ["#176f53", "#2a7187", "#c4820e", "#b53a3a", "#6b5ca5"]
max_axis = 1.0
for index, window in enumerate(windows):
    window_pairs = [pair for pair in visible_pairs if pair.window_name == window]
    buoy = [pair.buoy.swh_m for pair in window_pairs]
    altimeter = [pair.altimeter.swh_m for pair in window_pairs]
    if buoy:
        max_axis = max(max_axis, max(buoy), max(altimeter))
        ax_scatter.scatter(
            buoy,
            altimeter,
            s=24,
            color=colors[index % len(colors)],
            alpha=0.82,
            label=window,
        )
max_axis *= 1.08
ax_scatter.plot([0, max_axis], [0, max_axis], color="black", linewidth=0.9, label="y=x")
for index, metric in enumerate(analysis.metrics):
    fit_y = [metric.intercept, metric.slope * max_axis + metric.intercept]
    ax_scatter.plot([0, max_axis], fit_y, color=colors[index % len(colors)], linewidth=1.0, alpha=0.6)
ax_scatter.set_title("2D correction fit")
ax_scatter.set_xlabel("buoy SWH / m")
ax_scatter.set_ylabel("altimeter SWH / m")
ax_scatter.set_xlim(0, max_axis)
ax_scatter.set_ylim(0, max_axis)
ax_scatter.grid(True, alpha=0.22)
ax_scatter.legend(loc="upper left", fontsize=6)

directional_pairs = [pair for pair in visible_pairs if pair.buoy.direction_deg is not None]
ax_polar.set_title("polar direction", pad=16)
if directional_pairs:
    theta = np.deg2rad([pair.buoy.direction_deg for pair in directional_pairs])
    radius = [pair.buoy.swh_m for pair in directional_pairs]
    ax_polar.scatter(theta, radius, s=22, color="#2a7187", alpha=0.8)
ax_polar.set_theta_zero_location("N")
ax_polar.set_theta_direction(-1)

delta = [pair.delta_time_minutes for pair in visible_pairs]
distance = [max(pair.distance_km, 0.0) for pair in visible_pairs]
swh = [pair.altimeter.swh_m for pair in visible_pairs]
if delta:
    sizes = [28 + value * 18 for value in swh]
    ax_depth.scatter(delta, distance, c=swh, s=sizes, cmap="viridis", alpha=0.82)
ax_depth.set_title("distance-time-SWH")
ax_depth.set_xlabel("delta min")
ax_depth.set_ylabel("distance km")
ax_depth.grid(True, alpha=0.22)
ax_depth.text(
    0.98,
    0.04,
    "color + size = SWH",
    transform=ax_depth.transAxes,
    ha="right",
    va="bottom",
    fontsize=7,
    color="#49646b",
)

fig.text(0.985, 0.015, f"frame phase {phase:.2f}", ha="right", va="bottom", fontsize=7)
fig.tight_layout(rect=(0, 0.03, 1, 0.94))
