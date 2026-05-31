from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from wavecal.models import CollocationPair, Metrics


def render_scatter_figures(
    pairs: list[CollocationPair],
    metrics: list[Metrics],
    out_dir: str | Path,
) -> list[Path]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    metric_by_window = {item.window_name: item for item in metrics}
    grouped: dict[str, list[CollocationPair]] = defaultdict(list)
    for pair in pairs:
        grouped[pair.window_name].append(pair)

    written: list[Path] = []
    for window_name, window_pairs in grouped.items():
        metric = metric_by_window[window_name]
        buoy = [pair.buoy.swh_m for pair in window_pairs]
        alt = [pair.altimeter.swh_m for pair in window_pairs]
        max_axis = max(max(buoy), max(alt), 1.0) * 1.08

        fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=120)
        ax.scatter(buoy, alt, marker="*", color="#cc1f1a", label="Collocated samples")
        ax.plot([0, max_axis], [0, max_axis], color="black", linewidth=1.0, label="y=x")
        fit_y = [metric.intercept, metric.slope * max_axis + metric.intercept]
        ax.plot([0, max_axis], fit_y, color="#225ea8", linewidth=1.2, label="Linear fit")
        ax.set_title(window_name)
        ax.set_xlabel("Buoy SWH / m")
        ax.set_ylabel("Altimeter SWH / m")
        ax.set_xlim(0, max_axis)
        ax.set_ylim(0, max_axis)
        ax.grid(True, alpha=0.22)
        ax.legend(loc="upper left", fontsize=8)
        text = (
            f"N = {metric.n}\n"
            f"R = {metric.r:.3f}\n"
            f"MAE = {metric.mae_m:.3f} m\n"
            f"RMSE = {metric.rmse_m:.3f} m\n"
            f"fit = {metric.slope:.2f}x + {metric.intercept:.2f}"
        )
        ax.text(
            0.98,
            0.04,
            text,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8,
            bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none"},
        )
        fig.tight_layout()
        file_path = out_path / f"{window_name}.png"
        fig.savefig(file_path)
        plt.close(fig)
        written.append(file_path)

    return written
