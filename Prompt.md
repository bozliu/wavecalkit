# Prompt

## Project

- Name: WaveCalKit
- Root: `/Users/bozliu/Movies/论文&辅导/2019/6. 埃克塞特_Exeter`
- Primary owner: Codex

## Goal

- Primary objective: Turn the Exeter Jason-3-vs-buoy thesis archive into a clean, MATLAB-free Python public release toolkit.
- Intended audience or user: B2B metocean analysts, offshore renewable developers, coastal engineers, ports, and due-diligence teams.

## Deliverables

- Python package and CLI named `wavecal`.
- Reproducible Scilly case-study example with sanitized data, generated metrics, figures, report, and provenance.
- Public-facing docs with conservative commercial positioning.
- Durable memory updates for the active implementation.

## Non-Goals

- Do not ship raw private thesis/archive files or third-party data.
- Do not claim certified forecasting, navigation safety, buoy replacement, or bankable wave-energy yield.
- Do not require MATLAB, Octave, or GPU compute for v1.

## Constraints

- Runtime: `conda run -n dl python ...`.
- Dependencies: keep v1 runnable with installed `dl` stack; make NetCDF/XLS optional extras.
- Safety: initialize independent Git repo and baseline before edits.
- Scope: v1 should be a public-release seed with honest limits, not a finished commercial SaaS.

## Done When

- [ ] `conda run -n dl python -m pytest` succeeds.
- [ ] `conda run -n dl python -m wavecal.cli run --config examples/scilly_jason3.yml --out outputs/scilly` succeeds.
- [ ] Report, figures, metrics, and provenance are generated.
- [ ] Public docs state B2B value and conservative claim boundaries.

## Fixed Assumptions

- Product positioning is B2B decision-support and audit reporting.
- The old archive remains local and ignored; public release uses sanitized fixtures plus a legacy manifest.
