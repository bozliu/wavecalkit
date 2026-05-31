from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "wavecalkit_hero.gif"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [_render_frame(index) for index in range(24)]
    imageio.mimsave(OUT, frames, duration=0.11, loop=0)
    print(OUT)


def _render_frame(index: int):
    progress = index / 23
    fig = plt.figure(figsize=(9.6, 5.4), dpi=110)
    fig.patch.set_facecolor("#f7faf8")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    _title(ax)
    _map_panel(ax, progress)
    _pipeline(ax, progress)
    _metrics_panel(ax, progress)
    _report_panel(ax, progress)

    fig.canvas.draw()
    frame = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return frame


def _title(ax):
    ax.text(6, 55, "WaveCalKit", fontsize=23, weight="bold", color="#122c34")
    ax.text(
        6,
        51.6,
        "Satellite-vs-buoy wave-height validation with QC, correction fits, and audit-ready reports",
        fontsize=9.5,
        color="#49646b",
    )


def _map_panel(ax, progress: float):
    ax.add_patch(Rectangle((5, 9), 29, 39, facecolor="#e8f3ee", edgecolor="#9fb8ad", lw=1.2))
    ax.text(7, 45.2, "1. Collocate observations", fontsize=10.5, weight="bold", color="#16343b")
    ax.plot([9, 29], [16, 42], color="#2a7187", lw=1.8, alpha=0.85)
    ax.scatter([16], [24], s=130, marker="^", color="#d9534f", edgecolor="white", lw=0.8)
    ax.text(17.7, 23.2, "buoy", fontsize=8, color="#16343b")
    for radius, alpha in [(6, 0.14), (12, 0.10), (18, 0.07)]:
        ax.add_patch(Circle((16, 24), radius, fill=False, edgecolor="#2a7187", lw=1.2, alpha=alpha + 0.25))
    sample_count = max(1, int(12 * min(progress * 2.0, 1.0)))
    xs = np.linspace(9, 29, 12)[:sample_count]
    ys = np.linspace(16, 42, 12)[:sample_count]
    ax.scatter(xs, ys, s=28, color="#176f53", edgecolor="white", lw=0.5, zorder=3)
    ax.text(7, 11.6, "true distance windows + time tolerance", fontsize=8, color="#49646b")


def _pipeline(ax, progress: float):
    labels = ["CSV/NetCDF", "QC", "collocate", "fit", "report"]
    x0 = 39
    for i, label in enumerate(labels):
        x = x0 + i * 11.5
        active = progress >= i / (len(labels) - 1)
        color = "#176f53" if active else "#d5dfdc"
        ax.add_patch(Rectangle((x, 38), 8.8, 5.2, facecolor=color, edgecolor="none"))
        ax.text(x + 4.4, 40.6, label, fontsize=8.5, ha="center", va="center", color="white" if active else "#60757b")
        if i < len(labels) - 1:
            ax.add_patch(FancyArrowPatch((x + 9.1, 40.6), (x + 11.0, 40.6), arrowstyle="-|>", mutation_scale=10, color="#60757b", lw=1))
    ax.text(39, 45.2, "2. Reproducible validation pipeline", fontsize=10.5, weight="bold", color="#16343b")


def _metrics_panel(ax, progress: float):
    ax.add_patch(Rectangle((39, 13), 27, 19, facecolor="white", edgecolor="#b8c9c4", lw=1.0))
    ax.text(41, 29.2, "3. Correction metrics", fontsize=10.5, weight="bold", color="#16343b")
    rows = [
        ("0-25 km", "R 1.00", "fit 0.90x+0.14"),
        ("25-50 km", "R 1.00", "fit 0.83x+0.21"),
        ("50-75 km", "R 1.00", "fit 0.86x+0.17"),
        ("75-100 km", "R 1.00", "fit 0.90x+0.08"),
    ]
    visible = max(1, int(4 * min(max((progress - 0.25) * 1.8, 0), 1)))
    for idx, row in enumerate(rows[:visible]):
        y = 25.4 - idx * 3.5
        ax.text(41, y, row[0], fontsize=8.4, color="#16343b")
        ax.text(50, y, row[1], fontsize=8.4, color="#176f53")
        ax.text(56.5, y, row[2], fontsize=8.4, color="#49646b")


def _report_panel(ax, progress: float):
    ax.add_patch(Rectangle((70, 13), 24, 19, facecolor="#fffaf0", edgecolor="#d6b46d", lw=1.0))
    ax.text(72, 29.2, "4. Audit-ready bundle", fontsize=10.5, weight="bold", color="#16343b")
    items = ["metrics.csv", "collocations.csv", "figures", "report.md", "provenance.json"]
    visible = max(1, int(len(items) * min(max((progress - 0.45) * 1.9, 0), 1)))
    for idx, item in enumerate(items[:visible]):
        y = 25.5 - idx * 3.0
        ax.add_patch(Rectangle((72, y - 0.9), 2, 1.6, facecolor="#2a7187", edgecolor="none"))
        ax.text(75, y, item, fontsize=8.7, va="center", color="#16343b")
    ax.text(72, 10.4, "decision support, not certified forecasting", fontsize=8, color="#6b5c37")


if __name__ == "__main__":
    main()
