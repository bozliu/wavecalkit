from __future__ import annotations

import json
from pathlib import Path

from wavecal.models import CollocationPair, Metrics


def render_markdown_report(
    *,
    metrics: list[Metrics],
    pairs: list[CollocationPair],
    figure_paths: list[Path],
    out_path: str | Path,
    title: str = "WaveCalKit SWH Validation Report",
    data_sources: list[str] | None = None,
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    source_lines = "\n".join(f"- {source}" for source in (data_sources or []))
    metric_rows = "\n".join(
        "| {name} | {n} | {r:.3f} | {bias:.3f} | {mae:.3f} | {rmse:.3f} | {si:.3f} | {slope:.3f} +/- {slope_ci:.3f} | {intercept:.3f} +/- {intercept_ci:.3f} |".format(
            name=item.window_name,
            n=item.n,
            r=item.r,
            bias=item.signed_bias_m,
            mae=item.mae_m,
            rmse=item.rmse_m,
            si=item.scatter_index,
            slope=item.slope,
            intercept=item.intercept,
            slope_ci=item.slope_ci95,
            intercept_ci=item.intercept_ci95,
        )
        for item in metrics
    )
    figure_lines = "\n".join(f"- `{path}`" for path in figure_paths)
    text = f"""# {title}

## Summary

This report validates satellite-altimeter significant wave height against buoy observations using configurable time and distance windows. It is decision-support evidence for metocean screening and audit reporting, not certified forecasting, navigation safety software, or a replacement for buoy networks.

## Data Sources

{source_lines or "- Not specified."}

## Metrics

The bundled sample is deliberately tiny and sanitized for reproducibility tests. Perfect-looking values such as `R = 1.000` must not be read as field-grade accuracy.

| Window | N | R | Signed Bias m | MAE m | RMSE m | Scatter Index | Slope +/- 95% CI | Intercept +/- 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{metric_rows}

## Figures

{figure_lines}

## Method Notes

- Collocation pairs: {len(pairs)}
- Regression form: `altimeter_swh = slope * buoy_swh + intercept`
- `signed_bias_m` is the mean of `altimeter - buoy`; `mae_m` preserves the legacy thesis-style absolute bias.
- Distance windows are assigned with haversine distance, avoiding the legacy MATLAB latitude-index shortcut.

## Claim Boundary

This output is suitable for reproducibility checks, early site screening, and analyst review. Stronger claims require multi-site validation, source-specific quality flags, licensing review, and independent holdout testing.
"""
    out_path.write_text(text, encoding="utf-8")
    return out_path


def write_provenance(
    *,
    out_path: str | Path,
    config_path: str | Path | None,
    inputs: dict[str, str],
    metrics: list[Metrics],
    notes: list[str] | None = None,
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "tool": "WaveCalKit",
        "version": "0.1.0",
        "config_path": str(config_path) if config_path else None,
        "inputs": inputs,
        "metric_windows": [item.window_name for item in metrics],
        "notes": notes or [],
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out_path
