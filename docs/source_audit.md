# Source Audit

This audit captures functional requirements extracted from local historical Word/PDF source material without redistributing or naming those private files.

## Requirements Confirmed

- Read satellite-altimeter SWH records with time, latitude, longitude, mission/pass metadata, waveform-count quality fields, and optional provider flags.
- Read buoy SWH observations with station metadata, wave period, direction, and QC flags.
- Convert Jason-style time values to UTC and support normalized ISO timestamps.
- Match observations by configurable time windows, including exact timestamps and tolerance windows such as `30min`.
- Assign spatial windows by true geospatial distance: `0-25`, `25-50`, `50-75`, and `75-100 km`.
- Support pass filters for historical Jason-3 pass IDs `70`, `239`, and `248`.
- Apply QC for missing values, SWH bounds, minimum waveform count, source flags, buoy QC flags, and short-window buoy spikes.
- Produce collocation tables, per-window metrics, regression fits, confidence intervals, scatter figures, a markdown report, and provenance.
- Include optional wave-resource screening values when buoy period data is available.

## Implemented In This Release

- Python package and CLI with no MATLAB or Octave dependency.
- Normalized CSV adapters plus optional NetCDF and Excel readers.
- Haversine spatial matching and exact/tolerance time matching.
- Collocation aggregation by `nearest`, `mean`, or `median`.
- Metrics for `n`, `r`, signed bias, MAE, RMSE, scatter index, linear fit, and approximate 95% confidence intervals.
- Wave-power screening columns in collocation/metric/report outputs when period data exists.
- Public release audit command for raw-file and sensitive-term checks.

## Explicitly Out Of Scope For v1

- Certified forecasting, navigation safety, or buoy replacement.
- Live Copernicus Marine, Cefas WaveNet, or NOAA NDBC download clients.
- Wind-speed/U10 validation.
- Bankable wave-energy yield assessment.
- Global correction coefficients without multi-site holdout validation.
