# Historical Source Boundary

This repository was rebuilt from local historical wave-analysis material, but the public release intentionally ships only clean code, sanitized fixtures, and documentation.

## Findings Carried Into WaveCalKit

- Core data domain: satellite-altimeter 1 Hz Ku-band significant wave height compared with an in-situ wave buoy.
- Useful pass filters: `70`, `239`, and `248`.
- Useful distance windows: `0-25`, `25-50`, `50-75`, and `75-100 km`.
- Useful time matching modes: exact timestamps and configurable tolerance windows such as `30min`.
- Useful quality filters: missing values, SWH bounds, minimum valid waveform count, pass filters, optional source flags, buoy QC flags, and short-window spike checks.
- Useful metrics: sample count, correlation, signed bias, MAE, RMSE, scatter index, linear slope/intercept, confidence intervals, and provenance.
- Useful report assets: collocation table, metric table, scatter figures, method notes, and claim boundaries.

## Corrections Made In The Public Tool

- Distance windows are computed by geospatial distance rather than manual latitude-index slicing.
- Bias and MAE are separated so signed error is not confused with absolute error.
- Multiple satellite samples matched to one buoy observation can be aggregated by `nearest`, `mean`, or `median`.
- Wave-power screening is available only when period data is present and is labeled as decision support.
- Live provider download clients remain future adapters until authentication, licensing, and provider-specific QA fields are verified.

## Redistribution Boundary

Raw local documents, spreadsheets, NetCDF downloads, MATLAB files, KML/KMZ files, figures, and third-party PDFs are local evidence only. They are ignored by Git and are not redistributed by this MIT-licensed public repository.
