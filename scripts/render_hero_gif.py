from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import imageio.v2 as imageio
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

from wavecal.pipeline import analyze_config


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "wavecalkit_hero.gif"
CONFIG = ROOT / "examples" / "scilly_jason3.yml"

INK = "#132c35"
MUTED = "#5f7377"
GRID = "#cddbd6"
PAPER = "#fbfdfb"
OCEAN = "#e8f4f1"
TEAL = "#247487"
GREEN = "#177052"
CORAL = "#cc4c45"
GOLD = "#c28717"
VIOLET = "#6b5ca5"


@dataclass(frozen=True)
class HeroData:
    station_lon: float
    station_lat: float
    lons: list[float]
    lats: list[float]
    buoy_swh: list[float]
    alt_swh: list[float]
    distances: list[float]
    directions: list[float]
    metric_rows: list[tuple[str, str, str, str]]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = _load_case()
    frames = [_render_frame(index, data) for index in range(30)]
    imageio.mimsave(OUT, frames, duration=0.09, loop=0)
    print(OUT)


def _load_case() -> HeroData:
    analysis = analyze_config(CONFIG)
    pairs = analysis.pairs
    station = analysis.config["station"]
    metric_rows = []
    for metric in analysis.metrics[:4]:
        metric_rows.append(
            (
                metric.window_name,
                str(metric.n),
                f"{metric.signed_bias_m:+.2f}",
                f"{metric.slope:.2f}x+{metric.intercept:.2f}",
            )
        )
    return HeroData(
        station_lon=float(station["lon"]),
        station_lat=float(station["lat"]),
        lons=[pair.altimeter.lon for pair in pairs],
        lats=[pair.altimeter.lat for pair in pairs],
        buoy_swh=[pair.buoy.swh_m for pair in pairs],
        alt_swh=[pair.altimeter.swh_m for pair in pairs],
        distances=[pair.distance_km for pair in pairs],
        directions=[
            pair.buoy.direction_deg if pair.buoy.direction_deg is not None else 0.0
            for pair in pairs
        ],
        metric_rows=metric_rows,
    )


def _render_frame(index: int, data: HeroData):
    progress = _ease(index / 29)
    fig = plt.figure(figsize=(10.56, 5.94), dpi=100)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56.25)
    ax.axis("off")

    _draw_title(ax)
    _draw_pipeline(ax, progress)
    _draw_map(ax, progress, data)
    _draw_scatter(ax, progress, data)
    _draw_metrics(ax, progress, data)
    _draw_report(ax, progress)

    fig.canvas.draw()
    frame = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return frame


def _draw_title(ax):
    ax.text(5.0, 52.4, "WaveCalKit", fontsize=25, weight="bold", color=INK)
    ax.text(
        5.2,
        49.6,
        "Turn satellite and buoy observations into traceable validation reports",
        fontsize=10.6,
        color=MUTED,
    )
    ax.text(
        71.5,
        52.0,
        "B2B metocean evidence",
        fontsize=9.2,
        weight="bold",
        color=INK,
        ha="left",
    )
    ax.add_patch(Rectangle((71.4, 49.4), 22.6, 1.2, facecolor=GREEN, edgecolor="none", alpha=0.18))
    ax.text(72.0, 49.7, "decision support, reproducible, auditable", fontsize=7.7, color=GREEN)


def _draw_pipeline(ax, progress: float):
    labels = ["ingest", "QC", "collocate", "fit", "report"]
    x0 = 36.0
    y = 45.5
    for i, label in enumerate(labels):
        x = x0 + i * 10.8
        active = progress >= i / (len(labels) - 1)
        ax.add_patch(
            Rectangle(
                (x, y),
                8.2,
                3.9,
                facecolor=GREEN if active else "#dbe7e2",
                edgecolor="none",
            )
        )
        ax.text(
            x + 4.1,
            y + 1.95,
            label,
            fontsize=8.0,
            ha="center",
            va="center",
            color="white" if active else MUTED,
            weight="bold" if active else "normal",
        )
        if i < len(labels) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 8.7, y + 1.95),
                    (x + 10.3, y + 1.95),
                    arrowstyle="-|>",
                    mutation_scale=9,
                    color=TEAL,
                    lw=1.0,
                    alpha=0.55,
                )
            )
    dot_x = x0 + min(progress, 1.0) * 43.2
    ax.add_patch(Circle((dot_x, y + 5.3), 0.45, facecolor=GOLD, edgecolor="white", lw=0.8))


def _draw_map(ax, progress: float, data: HeroData):
    x, y, w, h = 5, 9, 30, 34
    _panel(ax, x, y, w, h, "1  geospatial + time match")
    ax.add_patch(Rectangle((x + 1.1, y + 2.0), w - 2.2, h - 5.9, facecolor=OCEAN, edgecolor=GRID, lw=0.8))
    land = Polygon(
        [
            (x + 1.2, y + 30.0),
            (x + 9.2, y + 29.1),
            (x + 13.6, y + 25.1),
            (x + 9.0, y + 21.5),
            (x + 2.2, y + 22.6),
        ],
        closed=True,
        facecolor="#d6dfc9",
        edgecolor="#b9c6ad",
        lw=0.8,
    )
    ax.add_patch(land)
    bx, by = x + 12.4, y + 13.6
    for radius, alpha in [(5.8, 0.42), (10.2, 0.28), (14.0, 0.18)]:
        ax.add_patch(Circle((bx, by), radius, fill=False, edgecolor=TEAL, lw=1.0, alpha=alpha))
    ax.scatter([bx], [by], marker="^", s=145, color=CORAL, edgecolor="white", lw=0.8, zorder=5)
    ax.text(bx + 1.5, by - 0.3, "buoy", fontsize=7.2, color=INK)

    track = _normalise_track(data, x + 3.6, y + 4.2, w - 6.0, h - 10.0)
    visible = max(2, int(len(track) * min(progress * 1.8, 1.0)))
    xs, ys = zip(*track[:visible])
    ax.plot(xs, ys, color=TEAL, lw=1.5, alpha=0.58)
    ax.scatter(xs, ys, s=30, color=GREEN, edgecolor="white", lw=0.45, zorder=4)
    pulse = 0.7 + 0.8 * abs(np.sin(progress * np.pi * 4))
    ax.add_patch(Circle((bx, by), 2.4 * pulse, fill=False, edgecolor=GOLD, lw=1.5, alpha=0.42))
    ax.text(x + 2.1, y + 2.8, "haversine windows + time tolerance", fontsize=7.4, color=MUTED)


def _draw_scatter(ax, progress: float, data: HeroData):
    x, y, w, h = 38, 20, 27, 23
    _panel(ax, x, y, w, h, "2  correction fit")
    px0, py0 = x + 4.0, y + 4.0
    pw, ph = w - 7.0, h - 8.0
    ax.plot([px0, px0], [py0, py0 + ph], color=GRID, lw=1)
    ax.plot([px0, px0 + pw], [py0, py0], color=GRID, lw=1)
    max_swh = max(data.buoy_swh + data.alt_swh) * 1.08
    ax.plot([px0, px0 + pw], [py0, py0 + ph], color=INK, lw=0.8, alpha=0.55)
    visible = max(1, int(len(data.buoy_swh) * min(max((progress - 0.18) * 1.6, 0), 1)))
    colors = [GREEN, TEAL, GOLD, CORAL]
    for idx in range(visible):
        sx = px0 + data.buoy_swh[idx] / max_swh * pw
        sy = py0 + data.alt_swh[idx] / max_swh * ph
        ax.scatter([sx], [sy], s=26, color=colors[idx % 4], edgecolor="white", lw=0.4, zorder=5)
    if progress > 0.5:
        ax.plot([px0, px0 + pw], [py0 + 0.7, py0 + ph - 0.4], color=CORAL, lw=1.5, alpha=0.85)
        ax.text(px0 + 1.0, py0 + ph - 2.2, "fit", fontsize=7.4, color=CORAL, weight="bold")
    ax.text(px0 + pw - 2.2, py0 - 2.2, "buoy", fontsize=7.0, color=MUTED)
    ax.text(px0 - 3.0, py0 + ph - 0.4, "sat", fontsize=7.0, color=MUTED, rotation=90)


def _draw_metrics(ax, progress: float, data: HeroData):
    x, y, w, h = 68, 20, 26, 23
    _panel(ax, x, y, w, h, "3  metrics table")
    headers = ["window", "n", "bias", "fit"]
    cols = [x + 2.0, x + 10.4, x + 14.0, x + 19.2]
    for label, cx in zip(headers, cols):
        ax.text(cx, y + h - 5.1, label, fontsize=7.3, color=MUTED, weight="bold")
    visible = max(1, int(len(data.metric_rows) * min(max((progress - 0.34) * 1.7, 0), 1)))
    for idx, row in enumerate(data.metric_rows[:visible]):
        yy = y + h - 8.3 - idx * 3.2
        ax.add_patch(Rectangle((x + 1.5, yy - 1.0), w - 3.0, 2.3, facecolor="#f6faf8", edgecolor="none"))
        for value, cx in zip(row, cols):
            ax.text(cx, yy, value, fontsize=7.5, color=INK if value != row[2] else GREEN)
    ax.text(x + 2.0, y + 2.6, "RMSE, MAE, CI, scatter index", fontsize=7.3, color=TEAL)


def _draw_report(ax, progress: float):
    x, y, w, h = 38, 6, 56, 10
    _panel(ax, x, y, w, h, "4  audit-ready outputs")
    items = [
        ("collocations.csv", GREEN),
        ("metrics.csv", TEAL),
        ("figures", GOLD),
        ("report.md", VIOLET),
        ("provenance.json", CORAL),
    ]
    visible = max(1, int(len(items) * min(max((progress - 0.55) * 1.8, 0), 1)))
    for idx, (label, color) in enumerate(items[:visible]):
        xx = x + 2.0 + idx * 10.6
        ax.add_patch(Rectangle((xx, y + 2.0), 8.5, 2.6, facecolor=color, edgecolor="none", alpha=0.92))
        ax.text(xx + 4.25, y + 3.3, label, fontsize=6.5, color="white", ha="center", va="center")
    ax.text(x + 2.0, y + 6.7, "Regenerate the same evidence bundle from one config", fontsize=7.7, color=MUTED)


def _panel(ax, x: float, y: float, w: float, h: float, title: str):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="white", edgecolor="#bed0ca", lw=1.0))
    ax.add_patch(Rectangle((x, y + h - 4.0), w, 4.0, facecolor="#f2f7f5", edgecolor="none"))
    ax.text(x + 1.6, y + h - 2.55, title, fontsize=8.6, weight="bold", color=INK)


def _normalise_track(data: HeroData, x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    min_lon = min(data.lons + [data.station_lon])
    max_lon = max(data.lons + [data.station_lon])
    min_lat = min(data.lats + [data.station_lat])
    max_lat = max(data.lats + [data.station_lat])
    lon_span = max(max_lon - min_lon, 0.001)
    lat_span = max(max_lat - min_lat, 0.001)
    points = []
    for lon, lat in zip(data.lons, data.lats):
        points.append((x + (lon - min_lon) / lon_span * w, y + (lat - min_lat) / lat_span * h))
    return points


def _ease(t: float) -> float:
    return 3 * t**2 - 2 * t**3


if __name__ == "__main__":
    main()
