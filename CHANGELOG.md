# Changelog

All notable changes to PSS are documented here.
Format loosely follows Keep a Changelog.

## [0.9.1] - 2026-07-27 (improve/sequential-v1)

### Added
- **Mission / SubMission** (RC pillar) — coexists with Objective
- **PredictionPolicy** — minimum_evidence / when_uncertain / allow_forward_looking
- **EvaluationCriteria** — preferred over EvaluationAxis
- **Gate** (`diagnose_gate` / `run_gate`) — diagnosis only, never mutates specification
- Builder methods: `.main_mission()`, `.add_sub_mission()`, `.prediction_policy()`, `.evaluation_criteria()`
- Adapter modes: `compile_for_generic(..., mode="balanced"|"strict")`
- `DEPRECATIONS.md` — clear migration path to v1.0 / v2.0
- Updated test suite with Gate mutation checks and behavioral cases

### Changed
- Public `__all__` tightened toward v1.0 freeze candidate
- README / ROADMAP / USAGE aligned with dual-track + RC pillars
- Version string set to `0.9.1`

### Deprecated (still functional)
- `ProblemBuilder.agent_role(...)` → prefer `.behavior(...)`
- Heavy exclusive use of `EvaluationAxis` → prefer `EvaluationCriteria`

### Design invariants kept
- Gate / Validator / Planner remain side-effect free
- Observation / Inference / Assumption / Unknown / Missing separation preserved
- No Executor in core

## [0.9.0] - previous
- Baseline package with Objective / Behavior / Knowledge / Phase / Validator / Planner

## [1.0.0-rc1] (single-file)
- Conceptual reference implementing Mission / PredictionPolicy / Gate / EvaluationCriteria
