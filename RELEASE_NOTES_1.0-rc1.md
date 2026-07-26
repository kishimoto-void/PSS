# PSS Single-File 1.0.0-rc1 — Release Notes

**Date**: 2026-07-26  
**Scope**: `pss_single.py` (conceptual freeze toward v1.0)  
**Package (`pss/`)**: remains **0.9.0** until ported

---

## What this RC freezes

Four core pillars:

1. **Mission** — what to achieve (Main / Sub, with priority)
2. **ThinkingProfile** — how to think (stance / perspective)
3. **PredictionPolicy** — how far prediction is allowed
4. **EvaluationCriteria** — what to value and how much (name + weight)

Operational layer (not core pillars):

- Phase / SectionGate / Behavior / Validator

External (minimal in single-file):

- Adapter (`render_specification` / `compile_for_generic`)

---

## Design rules locked in RC

| Rule | Meaning |
|------|--------|
| Gate is diagnosis only | `evaluate_gate()` never mutates the specification |
| PSS is not an executor | No auto phase advance, no LLM calls inside core |
| Not magic prompts | Structure the problem so the LLM can answer at full capacity |
| Knowledge discipline | Observation / Inference / Assumption / Unknown / Missing stay distinct |
| Prediction ≠ Gate | Gate decides phase progress; PredictionPolicy decides whether to assert |

---

## Schema

- `schema`: `pss.problem_specification/1.0`
- `version`: `1.0.0-rc1`

---

## Behavioral tests

See [docs/tests/](docs/tests/README.md):

| # | Case | Expectation |
|---|------|-------------|
| 01 | Used car | Gate BLOCK / no premature recommendation |
| 02 | Web release | Gate PASS / stay in scope |
| 03 | Stock forecast | Gate PASS, prediction refused |
| 04 | Code review | No scope violation |
| 05 | Model comparison | No assertion without evidence |

---

## Usage

- Human structured input **or** LLM formats natural language → PSS fields (no guessing)
- Guide: [docs/USAGE.md](docs/USAGE.md)

---

## Path to 1.0.0

- [ ] Port Mission / Gate / PredictionPolicy / EvaluationCriteria into package `pss/` if desired
- [ ] Keep public API surface stable
- [ ] Tag `v1.0.0` when package + single-file align (or document dual-track clearly)

Until then, **single-file is the RC reference implementation**.
