from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from wavecal.adapters import (
    read_altimeter_csv,
    read_altimeter_netcdf,
    read_buoy_csv,
    read_buoy_xls,
    read_legacy_txt,
    write_collocations_csv,
    write_metrics_csv,
)
from wavecal.collocation import collocate, parse_window_specs
from wavecal.figures import render_scatter_figures
from wavecal.metrics import compute_metrics_for_pairs
from wavecal.qc import filter_altimeter, filter_buoy
from wavecal.reports import render_markdown_report, write_provenance


@dataclass(frozen=True)
class AnalysisResult:
    config: dict[str, Any]
    config_path: Path
    altimeter: list
    buoy: list
    pairs: list
    metrics: list


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"config {path} did not contain a mapping")
    return loaded


def analyze_config(config_path: str | Path) -> AnalysisResult:
    config_path = Path(config_path)
    config = load_config(config_path)
    config = dict(config)

    altimeter_cfg = _resolve_source_config(config_path, config["altimeter"])
    buoy_cfg = _resolve_source_config(config_path, config["buoy"])
    config["altimeter"] = altimeter_cfg
    config["buoy"] = buoy_cfg
    station = config["station"]
    windows = parse_window_specs(config["windows"])

    altimeter = _read_altimeter(altimeter_cfg)
    buoy = read_buoy_from_config(buoy_cfg)
    qc_cfg = config.get("quality", {})
    altimeter = filter_altimeter(
        altimeter,
        min_swh_numval=qc_cfg.get("min_swh_numval"),
        min_swh_m=qc_cfg.get("min_swh_m"),
        max_swh_m=qc_cfg.get("max_swh_m"),
        allowed_passes=set(qc_cfg.get("allowed_passes", [])) or None,
        reject_quality_flags=set(qc_cfg.get("reject_altimeter_quality_flags", [])) or None,
        reject_rain_flags=set(qc_cfg.get("reject_rain_flags", [])) or None,
        reject_ice_flags=set(qc_cfg.get("reject_ice_flags", [])) or None,
        reject_land_flags=set(qc_cfg.get("reject_land_flags", [])) or None,
    )
    buoy = filter_buoy(
        buoy,
        min_swh_m=qc_cfg.get("min_swh_m"),
        max_swh_m=qc_cfg.get("max_swh_m"),
        reject_qc_flags=set(qc_cfg.get("reject_buoy_qc_flags", [])) or None,
        max_swh_jump_m=qc_cfg.get("max_buoy_swh_jump_m"),
        jump_window_hours=float(qc_cfg.get("buoy_jump_window_hours", 2.0)),
    )
    collocation_cfg = config.get("collocation", {})
    pairs = collocate(
        altimeter,
        buoy,
        station_lat=float(station["lat"]),
        station_lon=float(station["lon"]),
        windows=windows,
        time_window=collocation_cfg.get("time_window", "exact"),
        aggregation=collocation_cfg.get("aggregation", "nearest"),
    )
    metrics = compute_metrics_for_pairs(pairs, model=config.get("fit", {}).get("model", "linear"))
    return AnalysisResult(
        config=config,
        config_path=config_path,
        altimeter=altimeter,
        buoy=buoy,
        pairs=pairs,
        metrics=metrics,
    )


def _resolve_source_config(config_path: Path, source_config: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(source_config)
    raw_path = resolved.get("path")
    if raw_path:
        path = Path(raw_path)
        if not path.is_absolute():
            candidates = [
                Path.cwd() / path,
                config_path.parent / path,
                config_path.parent.parent / path,
            ]
            for candidate in candidates:
                if candidate.exists():
                    resolved["path"] = str(candidate.resolve())
                    break
            else:
                resolved["path"] = str((config_path.parent / path).resolve())
    return resolved


def run_pipeline(config_path: str | Path, out_dir: str | Path) -> dict[str, Path]:
    config_path = Path(config_path)
    analysis = analyze_config(config_path)
    config = analysis.config
    root = Path(out_dir)
    table_dir = root / "tables"
    figure_dir = root / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    altimeter_cfg = config["altimeter"]
    buoy_cfg = config["buoy"]
    collocation_cfg = config.get("collocation", {})

    collocations_path = table_dir / "collocations.csv"
    metrics_path = table_dir / "metrics.csv"
    write_collocations_csv(analysis.pairs, collocations_path)
    write_metrics_csv(analysis.metrics, metrics_path)
    figure_paths = render_scatter_figures(analysis.pairs, analysis.metrics, figure_dir)
    report_path = render_markdown_report(
        metrics=analysis.metrics,
        pairs=analysis.pairs,
        figure_paths=figure_paths,
        out_path=root / "report.md",
        title=config.get("report", {}).get("title", "WaveCalKit SWH Validation Report"),
        data_sources=config.get("data_sources", []),
    )
    provenance_path = write_provenance(
        out_path=root / "provenance.json",
        config_path=config_path,
        inputs={"altimeter": altimeter_cfg["path"], "buoy": buoy_cfg["path"]},
        metrics=analysis.metrics,
        notes=[
            "Public sample data is sanitized and not a commercial validation dataset.",
            "Distance windows use haversine distance.",
            f"Collocation aggregation mode: {collocation_cfg.get('aggregation', 'nearest')}.",
        ],
    )
    return {
        "collocations": collocations_path,
        "metrics": metrics_path,
        "report": report_path,
        "provenance": provenance_path,
        "figures_dir": figure_dir,
    }


def _read_altimeter(config: dict[str, Any]):
    source = config.get("source", "csv")
    if source == "csv":
        return read_altimeter_csv(config["path"])
    if source == "legacy-txt":
        return read_legacy_txt(
            config["path"],
            lat=config.get("lat"),
            lon=config.get("lon"),
            mission=config.get("mission", "Jason-3"),
            window_name=config.get("window_name"),
        )
    if source == "netcdf":
        return read_altimeter_netcdf(config["path"], mission=config.get("mission", "unknown"))
    if source == "copernicus":
        raise NotImplementedError(
            "Copernicus live download is planned; normalize downloaded Copernicus files to CSV or NetCDF for v1."
        )
    raise ValueError(f"unsupported altimeter source: {source}")


def read_buoy_from_config(config: dict[str, Any]):
    source = config.get("source", "csv")
    if source == "csv":
        return read_buoy_csv(config["path"])
    if source == "xls":
        return read_buoy_xls(config["path"], sheet_name=config.get("sheet_name", 0))
    if source in {"cefas", "ndbc"}:
        raise NotImplementedError(
            f"{source} live download is planned; normalize downloaded buoy data to CSV for v1."
        )
    raise ValueError(f"unsupported buoy source: {source}")
