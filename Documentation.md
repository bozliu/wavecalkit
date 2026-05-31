# Documentation

## Status

- Current milestone: Completed local public-release seed.
- Completed milestones: Milestone 1 baseline repository boundary; Milestone 2 package, CLI, fixtures, docs, and sample outputs.
- Next milestone: Optional remote publish/CI watch.
- Last updated: 2026-05-31.

## Decisions

- Decision: Ignore private/archive thesis files in Git.
  Why: The public release should be clean, reproducible, and safe to publish without raw third-party or personal archive material.
- Decision: Make NetCDF and XLS adapters optional extras.
  Why: The `dl` environment currently has `numpy`, `matplotlib`, `yaml`, `pandas`, and `pytest`, but not `xarray`, `netCDF4`, or `xlrd`.

## Validation Log

- Command: `git init && git add .gitignore && git commit -m "chore: establish clean release repo boundary"`
  Result: Passed, baseline commit `ed98a16`.
  Follow-up: Continue with package implementation.
- Command: `conda run -n dl python -m pytest`
  Result: Passed, `11 passed`.
  Follow-up: Addressed float-exact test assertions and reran successfully.
- Command: `conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly`
  Result: Passed; generated collocations, metrics, four figures, report, and provenance.
  Follow-up: Critic requested stronger caveats around tiny sanitized metrics and licensing.
- Command: verifier and critic subagents
  Result: Returned concrete findings; both agents were closed.
  Follow-up: Added CI columns/caveats, stronger licensing language, public packaging guidance, and this status update.
- Command: `conda run -n dl python -m wavecal --help`
  Result: Passed; CLI exposes `run`, `ingest-altimeter`, `ingest-buoy`, `collocate`, `fit`, and `report`.
  Follow-up: Public files staged for release commit.
- Command: `git check-ignore -v 'Done.docx' '格式要求.pdf' 'outputs/scilly/report.md' '.omx/metrics.json'`
  Result: Passed; private documents, generated outputs, and OmX state are ignored.
  Follow-up: Release must be made from Git-tracked files, not by zipping the whole working directory.

## How To Run Or Demo

- Setup: `conda run -n dl python -m pytest`
- Main command: `conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly`
- Smoke test: inspect `outputs/scilly/report.md` and generated figures.

## Known Issues

- Raw NetCDF files are not present in the archive.
- Legacy `.xls` reading requires optional `xlrd`, not installed in `dl`.
- Generated `outputs/` are intentionally ignored; users regenerate them via the CLI.
- Remote GitHub CI has not been run in this local implementation turn.

## Follow-Ups

- Add live Copernicus/Cefas/NDBC adapters once credentials/licensing and API shapes are confirmed.
- Add multi-site validation before making stronger commercial accuracy claims.
