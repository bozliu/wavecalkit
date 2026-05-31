from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.figure import Figure

from wavecal.models import CollocationPair, Metrics
from wavecal.pipeline import analyze_config


def render_workflow_animation(
    config_path: str | Path,
    out_path: str | Path,
    *,
    frames: int = 24,
    fps: int = 8,
    fmt: str | None = None,
) -> Path:
    """Render the Python-native validation workflow as GIF or MP4."""
    if frames < 2:
        raise ValueError("frames must be at least 2")
    analysis = analyze_config(config_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = (fmt or out_path.suffix.lstrip(".") or "gif").lower()
    if fmt not in {"gif", "mp4"}:
        raise ValueError("format must be gif or mp4")

    fig = _new_workflow_figure()

    def update(index: int):
        for axis in fig.axes:
            axis.clear()
        phase = index / (frames - 1)
        draw_workflow_figure(
            pairs=analysis.pairs,
            metrics=analysis.metrics,
            station=analysis.config["station"],
            phase=phase,
            fig=fig,
        )
        return []

    update(0)
    animation = FuncAnimation(fig, update, frames=frames, interval=1000 / fps, blit=False)
    if fmt == "gif":
        animation.save(out_path, writer=PillowWriter(fps=fps))
    else:
        animation.save(out_path, writer=FFMpegWriter(fps=fps))
    plt.close(fig)
    return out_path


def workflow_figure_from_config(config_path: str | Path, *, phase: float = 0.0) -> Figure:
    analysis = analyze_config(config_path)
    fig = _new_workflow_figure()
    draw_workflow_figure(
        pairs=analysis.pairs,
        metrics=analysis.metrics,
        station=analysis.config["station"],
        phase=phase,
        fig=fig,
    )
    return fig


def draw_workflow_figure(
    *,
    pairs: list[CollocationPair],
    metrics: list[Metrics],
    station: dict,
    phase: float,
    fig: Figure,
) -> Figure:
    phase = max(0.0, min(float(phase), 1.0))
    visible_count = max(1, math.ceil(len(pairs) * phase))
    visible_pairs = pairs[:visible_count]
    metric_by_window = {item.window_name: item for item in metrics}

    fig.suptitle("WaveCalKit Python-native validation workflow", fontsize=14, weight="bold")
    ax_map, ax_scatter, ax_polar, ax_3d = fig.axes
    _draw_map(ax_map, visible_pairs, station)
    _draw_scatter(ax_scatter, visible_pairs, metric_by_window)
    _draw_polar(ax_polar, visible_pairs)
    _draw_3d(ax_3d, visible_pairs)
    fig.text(0.985, 0.015, f"frame phase {phase:.2f}", ha="right", va="bottom", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    return fig


def _new_workflow_figure() -> Figure:
    fig = plt.figure(figsize=(10.4, 6.2), dpi=110)
    fig.add_subplot(2, 2, 1)
    fig.add_subplot(2, 2, 2)
    fig.add_subplot(2, 2, 3, projection="polar")
    fig.add_subplot(2, 2, 4, projection="3d")
    return fig


def _draw_map(ax, pairs: list[CollocationPair], station: dict) -> None:
    station_lon = float(station["lon"])
    station_lat = float(station["lat"])
    lons = [pair.altimeter.lon for pair in pairs if pair.altimeter.lon is not None]
    lats = [pair.altimeter.lat for pair in pairs if pair.altimeter.lat is not None]
    ax.scatter([station_lon], [station_lat], marker="^", s=120, color="#d9534f", label="buoy")
    if lons and lats:
        ax.plot(lons, lats, color="#2a7187", alpha=0.45, linewidth=1.0)
        ax.scatter(lons, lats, s=28, color="#176f53", edgecolor="white", linewidth=0.4)
    ax.set_title("geospatial collocation")
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.grid(True, alpha=0.22)
    ax.legend(loc="best", fontsize=7)


def _draw_scatter(ax, pairs: list[CollocationPair], metrics: dict[str, Metrics]) -> None:
    colors = ["#176f53", "#2a7187", "#c4820e", "#b53a3a", "#6b5ca5"]
    windows = sorted({pair.window_name for pair in pairs}, key=_window_sort_key)
    max_axis = 1.0
    for index, window in enumerate(windows):
        window_pairs = [pair for pair in pairs if pair.window_name == window]
        buoy = [pair.buoy.swh_m for pair in window_pairs]
        alt = [pair.altimeter.swh_m for pair in window_pairs]
        if not buoy:
            continue
        max_axis = max(max_axis, max(buoy), max(alt))
        ax.scatter(
            buoy,
            alt,
            s=24,
            color=colors[index % len(colors)],
            alpha=0.82,
            label=window,
        )
    max_axis *= 1.08
    ax.plot([0, max_axis], [0, max_axis], color="black", linewidth=0.9, label="y=x")
    for index, metric in enumerate(metrics.values()):
        fit_y = [metric.intercept, metric.slope * max_axis + metric.intercept]
        ax.plot([0, max_axis], fit_y, color=colors[index % len(colors)], linewidth=1.0, alpha=0.6)
    ax.set_title("2D correction fit")
    ax.set_xlabel("buoy SWH / m")
    ax.set_ylabel("altimeter SWH / m")
    ax.set_xlim(0, max_axis)
    ax.set_ylim(0, max_axis)
    ax.grid(True, alpha=0.22)
    ax.legend(loc="upper left", fontsize=6)


def _draw_polar(ax, pairs: list[CollocationPair]) -> None:
    directional = [pair for pair in pairs if pair.buoy.direction_deg is not None]
    ax.set_title("polar direction", pad=16)
    if not directional:
        ax.text(0.5, 0.5, "direction data optional", transform=ax.transAxes, ha="center")
        return
    theta = np.deg2rad([pair.buoy.direction_deg for pair in directional])
    radius = [pair.buoy.swh_m for pair in directional]
    ax.scatter(theta, radius, s=22, color="#2a7187", alpha=0.8)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)


def _draw_3d(ax, pairs: list[CollocationPair]) -> None:
    if not pairs:
        return
    delta = [pair.delta_time_minutes for pair in pairs]
    distance = [max(pair.distance_km, 0.0) for pair in pairs]
    swh = [pair.altimeter.swh_m for pair in pairs]
    ax.scatter(delta, distance, swh, s=18, color="#176f53", alpha=0.8)
    ax.set_title("3D distance-time-SWH")
    ax.set_xlabel("delta min")
    ax.set_ylabel("distance km")
    ax.set_zlabel("SWH m")


def _window_sort_key(name: str) -> tuple[float, str]:
    try:
        return (float(name.split("-", 1)[0]), name)
    except ValueError:
        return (999999.0, name)
