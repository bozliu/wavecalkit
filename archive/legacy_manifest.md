# Legacy Archive Manifest

The original Exeter folder is kept locally for evidence, but ignored by Git so the public release stays clean and safe to publish.

## Local Evidence

- `Done.docx`: final dissertation draft with title, objectives, results, caveats, and appendices.
- `Method_Result&Discussion_Conclusion_Final.docx`: focused method/result/conclusion text.
- `格式要求.pdf`: Exeter dissertation formatting requirements.
- Long `*ddl/` archive folder: MATLAB source, WPS/Excel data, figures, draft docs, and reference material.
- `*/Matlab new_figure_20190827/new_figure_20190827/source code_20190827/p_1hz.m`: MATLAB NetCDF extraction workflow.
- `*/Matlab new_figure_20190827/new_figure_20190827/source code_20190827/plot_Hs.m`: MATLAB exact-time collocation, metrics, and scatter plotting workflow.
- `*/Matlab new_figure_20190827/new_figure_20190827/data/parameter_*.txt`: legacy four-column SWH outputs with stale 15-column headers.

## Findings Carried Into WaveCalKit

- Legacy data sources: Jason-3 1 Hz Ku-band GDR data from AVISO+/CNES and SW Isle of Scilly WaveNet buoy data.
- Legacy passes: `70`, `239`, and `248`.
- Legacy windows: `0-25`, `25-50`, `50-75`, and `75-100 km`.
- Legacy metrics: sample count, correlation, absolute bias, RMSE/RMS, linear slope, and intercept.
- Historical thesis reproduction targets, not recommended universal correction coefficients:
  - `0-25km`: `Hs(Jason-3) = 0.90 * Hs(Buoy) + 0.14`
  - `25-50km`: `Hs(Jason-3) = 0.83 * Hs(Buoy) + 0.21`
  - `50-75km`: `Hs(Jason-3) = 0.86 * Hs(Buoy) + 0.17`
  - `75-100km`: `Hs(Jason-3) = 0.90 * Hs(Buoy) + 0.08`

## Known Legacy Issues

- Raw NetCDF files are not present in this local folder.
- MATLAB paths are hard-coded to a Windows desktop.
- The legacy TXT header declares 15 columns while the active output writes only 4 fields.
- The MATLAB extractor computes longitude filters but loops over latitude index ranges only.
- Existing "Bias" is mean absolute error, not signed bias.
- The thesis itself warns that two years of lightly filtered data is not industrial-grade validation.

## Redistribution Boundary

AVISO+/CNES, Copernicus Marine, Cefas/WaveNet, NOAA, thesis files, and any downloaded NetCDF/Excel/PDF assets remain subject to their own licenses and terms. They are local evidence only and are not redistributed by the MIT-licensed public repo.
