# PSS 0.9.1 Release Notes

**Date**: 2026-07-27  
**Branch**: `improve/sequential-v1`  
**Status**: API freeze candidate toward 1.0.0

## Summary

Sequential improvements (Steps 1–5) have been applied to the package track.
The package now carries the main RC 1.0-rc1 pillars while remaining backward-compatible with the previous 0.9 API.

## Key Additions

| Feature | Description |
|---------|-------------|
| **Mission / SubMission** | Primary goal + optional sub-goals (coexists with Objective) |
| **PredictionPolicy** | Controls how far the model may assert / predict |
| **EvaluationCriteria** | Preferred evaluation structure |
| **Gate (diagnosis-only)** | `diagnose_gate()` / `run_gate()` — never mutates the specification |
| **Adapter modes** | `mode="balanced"` (default, concise) / `mode="strict"` (detailed) |
| **DEPRECATIONS.md** | Clear migration guidance |

## Compatibility

- Existing code using `Objective`, `EvaluationAxis`, and `agent_role()` continues to work.
- New code is encouraged to use `Mission` + `PredictionPolicy` + `EvaluationCriteria` + `behavior()`.
- Breaking removals are deferred to **v2.0**.

## Design Invariants (unchanged)

1. Gate / Validator / Planner are **diagnosis / plan only**.
2. Observation / Inference / Assumption / Unknown / Missing remain strictly separated.
3. No Executor lives in the core package.
4. The specification is the shared thinking condition for humans, agents, and LLMs.

## Files of interest

- `ROADMAP.md` — sequential plan
- `DEPRECATIONS.md` — what will change later
- `CHANGELOG.md` — detailed change list
- `pss/adapter.py` — balanced / strict rendering
- `pss/test_pss.py` — updated suite including Gate mutation checks

## Next

- Review & merge PR
- Tag `v0.9.1` (or proceed directly toward `v1.0.0` after final alignment with single-file)
- Optional: further polish of single-file `pss_single.py` for full parity

## How to try

```bash
git checkout improve/sequential-v1
PYTHONPATH=. python -m pytest pss/test_pss.py -v
```
