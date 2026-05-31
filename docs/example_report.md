# Example WaveCalKit Report Shape

This example shows the shape of a generated report from the sanitized fixture. Regenerate the full local bundle with:

```bash
conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly
```

## Outputs

| Artifact | Purpose |
|---|---|
| `tables/collocations.csv` | Matched satellite/buoy observations with time delta, distance, aggregation, and wave-power screening columns |
| `tables/metrics.csv` | Per-window validation metrics and correction fits |
| `figures/*.png` | Scatter plots with `y=x` and fitted correction lines |
| `report.md` | Markdown method summary and claim boundary |
| `provenance.json` | Config, inputs, metric windows, and method notes |

## Sample Metrics

| Window | N | R | Signed Bias m | MAE m | RMSE m | Scatter Index | Fit |
|---|---:|---:|---:|---:|---:|---:|---|
| 0-25 km | 8 | 1.000 | -0.135 | 0.145 | 0.177 | 0.064 | `0.90x + 0.14` |
| 25-50 km | 8 | 1.000 | -0.257 | 0.267 | 0.323 | 0.117 | `0.83x + 0.21` |
| 50-75 km | 8 | 1.000 | -0.215 | 0.223 | 0.268 | 0.098 | `0.86x + 0.17` |
| 75-100 km | 8 | 1.000 | -0.195 | 0.195 | 0.226 | 0.082 | `0.90x + 0.08` |

## Claim Boundary

The fixture validates the workflow and reproducibility contract. Commercial accuracy claims require real licensed data, source-specific quality flags, multi-site validation, and independent holdout testing.
