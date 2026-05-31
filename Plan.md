# Plan

## Summary

- Build WaveCalKit as a Python package and CLI for satellite-altimeter SWH versus buoy validation/correction, seeded by the Jason-3 SW Isle of Scilly case study.

## Architecture Notes

- Keep the public package separate from ignored raw archive files.
- Use dataclasses for records and metrics.
- Use true haversine distance windows instead of the legacy MATLAB latitude-index shortcut.
- Preserve legacy-parity equations through sanitized fixtures and golden tests.

## Milestones

### Milestone 1

- Goal: Establish safe repo and durable memory.
- Scope: `.gitignore`, Git baseline, `Prompt.md`, `Plan.md`, `Implement.md`, `Documentation.md`.
- Acceptance criteria: Git repo is independent and archive files are ignored.
- Validation commands: `git status --short --ignored`.

### Milestone 2

- Goal: Implement core package and CLI.
- Scope: models, adapters, geospatial windowing, collocation, metrics, figures, reports, example config/data.
- Acceptance criteria: `wavecal run` produces metrics, figures, report, and provenance.
- Validation commands: `conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly`.

### Milestone 3

- Goal: Validate and audit public-release quality.
- Scope: tests, docs, legacy manifest, subagent verification/critique, fixes.
- Acceptance criteria: tests pass and public claims stay conservative.
- Validation commands: `conda run -n dl python -m pytest`.

## Stop-And-Fix Rule

- If a validation step fails, repair the issue before starting the next milestone.
- If scope changes, update this file before continuing.

## Decision Notes

- Use `dl` conda env for all Python validation.
- Avoid mandatory `xarray`, `netCDF4`, and `xlrd` because they are not currently installed.
- Treat raw archive documents/data as local evidence, not public-release assets.
