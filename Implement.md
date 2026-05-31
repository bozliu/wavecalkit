# Implement

## Runbook

1. Treat `Plan.md` as the execution source of truth.
2. Complete one milestone at a time.
3. Keep diffs scoped to the current milestone.
4. Run the milestone validation commands immediately after implementation.
5. Fix validation failures before moving on.
6. Update `Documentation.md` continuously with status, decisions, and verification results.
7. If the user changes the goal or scope, update `Prompt.md`, `Plan.md`, and `Documentation.md` before continuing.

## Working Agreements

- Preserve unrelated user changes.
- Prefer non-destructive commands.
- Log blockers and repairs in `Documentation.md`.
- Keep the project in a runnable, reviewable state at every milestone boundary.

## Active Run

- Baseline commit: `ed98a16 chore: establish clean release repo boundary`.
- Python environment: `conda run -n dl python`.
- Implementation strategy: lead agent implements code; verifier and critic agents audit after a runnable slice exists.
