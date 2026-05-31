# Python Reimplementation

WaveCalKit replaces the historical desktop plotting workflow with Python-native commands that can run locally, in CI, and in reproducible analyst pipelines.

## Task Map

| Historical task | Python implementation | Command or module |
|---|---|---|
| Read exported satellite SWH text files | Historical four-column TXT adapter plus normalized CSV/NetCDF readers | `wavecal ingest-altimeter --source legacy-txt|csv|netcdf` |
| Read buoy spreadsheets | Normalized CSV plus optional Excel adapter | `wavecal ingest-buoy --source csv|xls` |
| Match satellite and buoy observations | Haversine distance windows, exact/tolerance time matching, and aggregation | `wavecal collocate` |
| Compute correction equations | NumPy metrics and linear fit | `wavecal fit` |
| Produce scatter figures | Matplotlib static figures | `wavecal render-figures` |
| Produce workflow animation | Matplotlib `FuncAnimation` with GIF/MP4 writers | `wavecal animate` |
| Sweep a plotting variable | Optional `mpl-animator` static-script sweep | `mpl-animator scripts/render_workflow_animation.py --var frame --range "0,2*pi" --frames 60 --out outputs/scilly/mpl_animator.gif`, then `python render_workflow_animation_animated.py` |

## Visualization Modes

- 2D scatter correction plot: buoy SWH versus altimeter SWH with `y=x` and fitted correction lines.
- Polar plot: buoy wave direction when `direction_deg` exists.
- Subplot dashboard: `wavecal animate` renders map, correction fit, polar direction, and 3D distance-time-SWH views.
- GIF/MP4 output: default `wavecal animate` uses Matplotlib writers; optional `mpl-animator` is available for variable sweeps and writes a generated script that you run to create the media.
- Optional `mpl-animator` demo: keeps the sweep dashboard 2D-only so the generated script preserves all subplots consistently.

## Dependency Policy

Core WaveCalKit stays lightweight: `matplotlib`, `numpy`, and `PyYAML`.

Optional visualization extras install animation conveniences:

```bash
pip install ".[visual]"
```

Manim is not a v1 dependency. It is a strong open-source tool for explanatory math videos, but it brings a heavier rendering stack than this validation package needs. Use it later for marketing or education videos, not for the core analyst workflow.

## Release Boundary

Raw `.m`, Office, PDF, spreadsheet, KML/KMZ, and NetCDF archive files stay local and ignored. The public repo ships reproducible Python code, sanitized fixtures, generated visual assets, and instructions for users to normalize their own licensed data.
