# WaveCalKit

WaveCalKit is a MATLAB-free Python toolkit for validating satellite-altimeter significant wave height (SWH) against buoy observations and producing reproducible analyst reports with an explicit audit trail.

The seed case study recreates the useful part of an Exeter MSc thesis archive: Jason-3 1 Hz Ku-band SWH compared with the SW Isle of Scilly WaveNet buoy across distance windows of `0-25`, `25-50`, `50-75`, and `75-100 km`.

## Who It Is For

WaveCalKit is aimed at B2B metocean practitioners: offshore renewable developers, coastal engineering teams, ports, marine insurers, and due-diligence consultants who need reproducible evidence about whether satellite wave-height data is credible for an early site-screening or reporting workflow.

It is not certified navigation software, an operational forecast system, or a replacement for buoy networks.

## Quick Start

Use the `dl` conda environment on this Mac:

```bash
conda run -n dl python -m pytest
conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly
```

The run writes:

- `outputs/scilly/tables/collocations.csv`
- `outputs/scilly/tables/metrics.csv`
- `outputs/scilly/figures/*.png`
- `outputs/scilly/report.md`
- `outputs/scilly/provenance.json`

## CLI

```bash
wavecal run --config examples/scilly_jason3.yml --out outputs/scilly
wavecal ingest-altimeter --source csv --input examples/data/scilly_altimeter_sample.csv --out outputs/altimeter.csv
wavecal ingest-buoy --source csv --input examples/data/scilly_buoy_sample.csv --out outputs/buoy.csv
wavecal collocate --altimeter-csv outputs/altimeter.csv --buoy-csv outputs/buoy.csv --station-lat 49.816667 --station-lon -6.545167 --out outputs/collocations.csv
wavecal fit --collocations outputs/collocations.csv --out outputs/metrics.csv
wavecal report --metrics outputs/metrics.csv --collocations outputs/collocations.csv --out outputs/report.md
```

## Data Adapters

Current v1 supports normalized CSV, legacy 4-column MATLAB TXT outputs, optional normalized `.xls` buoy workbooks, and optional user-supplied NetCDF altimeter files. Live Copernicus, Cefas, and NOAA downloads are documented adapter targets, but v1 asks users to normalize downloaded data to CSV/NetCDF until source-specific licensing and authentication flows are wired in.

```bash
pip install ".[excel,netcdf]"
```

The public repo intentionally excludes raw thesis documents, old Excel files, and third-party archives. See `archive/legacy_manifest.md` for the evidence map.

When publishing or packaging this project, use tracked Git files or a GitHub-generated source archive. Do not zip the whole working directory, because the ignored local thesis archive still coexists beside the public-release code.

## Scientific Boundaries

WaveCalKit reports correlation, signed bias, mean absolute error, RMSE, scatter index, linear correction slope/intercept, and approximate confidence intervals. The sample data is sanitized and small; perfect-looking sample metrics are fixtures for reproducibility and testing, not commercial validation evidence.

All external data remains subject to its own terms. AVISO+/CNES, Copernicus Marine, Cefas/WaveNet, NOAA, thesis files, and any downloaded NetCDF/Excel/PDF assets are not redistributed by this MIT-licensed repo.
