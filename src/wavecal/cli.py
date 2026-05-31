from __future__ import annotations

import argparse
from pathlib import Path

from wavecal.adapters import (
    read_altimeter_csv,
    read_altimeter_netcdf,
    read_buoy_csv,
    read_buoy_xls,
    read_collocations_csv,
    read_legacy_txt,
    read_metrics_csv,
    write_altimeter_csv,
    write_buoy_csv,
    write_collocations_csv,
    write_metrics_csv,
)
from wavecal.collocation import collocate, parse_window_specs
from wavecal.metrics import compute_metrics_for_pairs
from wavecal.models import AltimeterRecord, BuoyRecord, CollocationPair
from wavecal.pipeline import run_pipeline
from wavecal.release_audit import audit_release, format_audit_result
from wavecal.reports import render_markdown_report
from wavecal.timeutil import parse_time


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wavecal")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run a configured validation pipeline.")
    run.add_argument("--config", required=True)
    run.add_argument("--out", required=True)

    ingest_alt = subparsers.add_parser("ingest-altimeter", help="Normalize altimeter input.")
    ingest_alt.add_argument("--source", choices=["csv", "legacy-txt", "netcdf", "copernicus"], required=True)
    ingest_alt.add_argument("--input", required=True)
    ingest_alt.add_argument("--out", required=True)
    ingest_alt.add_argument("--lat", type=float)
    ingest_alt.add_argument("--lon", type=float)
    ingest_alt.add_argument("--window-name")

    ingest_buoy = subparsers.add_parser("ingest-buoy", help="Normalize buoy input.")
    ingest_buoy.add_argument("--source", choices=["csv", "xls", "cefas", "ndbc"], required=True)
    ingest_buoy.add_argument("--input", required=True)
    ingest_buoy.add_argument("--out", required=True)

    coloc = subparsers.add_parser("collocate", help="Collocate normalized altimeter and buoy CSV.")
    coloc.add_argument("--altimeter-csv", required=True)
    coloc.add_argument("--buoy-csv", required=True)
    coloc.add_argument("--station-lat", type=float, required=True)
    coloc.add_argument("--station-lon", type=float, required=True)
    coloc.add_argument("--time-window", default="exact")
    coloc.add_argument("--space-windows", default="0-25,25-50,50-75,75-100")
    coloc.add_argument("--aggregation", choices=["nearest", "mean", "median"], default="nearest")
    coloc.add_argument("--out", required=True)

    fit = subparsers.add_parser("fit", help="Fit correction metrics from collocations.")
    fit.add_argument("--collocations", required=True)
    fit.add_argument("--out", required=True)

    report = subparsers.add_parser("report", help="Render a markdown report from metrics.")
    report.add_argument("--metrics", required=True)
    report.add_argument("--collocations", required=True)
    report.add_argument("--out", required=True)
    report.add_argument("--format", choices=["md"], default="md")

    audit = subparsers.add_parser("audit-release", help="Check tracked or archived files before public release.")
    audit.add_argument("--root", default=".")
    audit.add_argument("--mode", choices=["tracked", "archive"], default="tracked")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        outputs = run_pipeline(args.config, args.out)
        for name, path in outputs.items():
            print(f"{name}: {path}")
        return 0

    if args.command == "ingest-altimeter":
        if args.source == "csv":
            records = read_altimeter_csv(args.input)
        elif args.source == "legacy-txt":
            records = read_legacy_txt(args.input, lat=args.lat, lon=args.lon, window_name=args.window_name)
        elif args.source == "netcdf":
            records = read_altimeter_netcdf(args.input)
        else:
            raise NotImplementedError(
                "Copernicus live download is planned; normalize downloaded Copernicus files to CSV or NetCDF for v1."
            )
        write_altimeter_csv(records, args.out)
        print(f"wrote {len(records)} altimeter records to {args.out}")
        return 0

    if args.command == "ingest-buoy":
        if args.source == "csv":
            records = read_buoy_csv(args.input)
        elif args.source == "xls":
            records = read_buoy_xls(args.input)
        else:
            raise NotImplementedError(
                f"{args.source} live download is planned; normalize downloaded buoy data to CSV for v1."
            )
        write_buoy_csv(records, args.out)
        print(f"wrote {len(records)} buoy records to {args.out}")
        return 0

    if args.command == "collocate":
        windows = parse_window_specs(args.space_windows.split(","))
        pairs = collocate(
            read_altimeter_csv(args.altimeter_csv),
            read_buoy_csv(args.buoy_csv),
            station_lat=args.station_lat,
            station_lon=args.station_lon,
            windows=windows,
            time_window=args.time_window,
            aggregation=args.aggregation,
        )
        write_collocations_csv(pairs, args.out)
        print(f"wrote {len(pairs)} collocations to {args.out}")
        return 0

    if args.command == "fit":
        pairs = _pairs_from_rows(read_collocations_csv(args.collocations))
        metrics = compute_metrics_for_pairs(pairs)
        write_metrics_csv(metrics, args.out)
        print(f"wrote {len(metrics)} metric rows to {args.out}")
        return 0

    if args.command == "report":
        metrics = _metrics_from_rows(read_metrics_csv(args.metrics))
        pairs = _pairs_from_rows(read_collocations_csv(args.collocations))
        render_markdown_report(metrics=metrics, pairs=pairs, figure_paths=[], out_path=args.out)
        print(f"wrote report to {args.out}")
        return 0

    if args.command == "audit-release":
        result = audit_release(args.root, mode=args.mode)
        print(format_audit_result(result))
        return 0 if result.passed else 1

    parser.error(f"unsupported command {args.command}")
    return 2


def _pairs_from_rows(rows: list[dict[str, str]]) -> list[CollocationPair]:
    pairs: list[CollocationPair] = []
    for row in rows:
        alt = AltimeterRecord(
            time=parse_time(row["time_altimeter"]),
            lat=None,
            lon=None,
            swh_m=float(row["altimeter_swh_m"]),
            mission=row.get("mission") or "unknown",
            source_file=row.get("source_file") or "",
            window_name=row["window_name"],
        )
        buoy = BuoyRecord(
            time=parse_time(row["time_buoy"]),
            station_id=row.get("station_id") or "unknown",
            lat=None,
            lon=None,
            swh_m=float(row["buoy_swh_m"]),
            period_s=_optional_float(row.get("buoy_period_s")),
        )
        pairs.append(
            CollocationPair(
                altimeter=alt,
                buoy=buoy,
                distance_km=float(row["distance_km"]),
                delta_time_minutes=float(row["delta_time_minutes"]),
                window_name=row["window_name"],
                aggregation=row.get("aggregation") or "nearest",
                matched_altimeter_count=int(row.get("matched_altimeter_count") or 1),
            )
        )
    return pairs


def _metrics_from_rows(rows: list[dict[str, str]]):
    from wavecal.models import Metrics

    metrics = []
    for row in rows:
        metrics.append(
            Metrics(
                window_name=row["window_name"],
                n=int(row["n"]),
                r=float(row["r"]),
                signed_bias_m=float(row["signed_bias_m"]),
                mae_m=float(row["mae_m"]),
                rmse_m=float(row["rmse_m"]),
                scatter_index=float(row["scatter_index"]),
                slope=float(row["slope"]),
                intercept=float(row["intercept"]),
                slope_ci95=float(row["slope_ci95"]),
                intercept_ci95=float(row["intercept_ci95"]),
                model=row.get("model") or "linear",
                mean_buoy_wave_power_kw_per_m=_optional_float(
                    row.get("mean_buoy_wave_power_kw_per_m")
                ),
            )
        )
    return metrics


def _optional_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
