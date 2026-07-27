# PSS — Problem Specification System

**PSS is a shared specification of thinking conditions** for humans, agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

It is not a prompt template.  
It is not an agent framework.  
It is a lightweight, model-independent library for writing, validating, and improving problem specifications.

**Current tracks**  
- **Package `pss/`**: **0.9.1** (API freeze candidate toward v1.0)  
- **Single-file**: **1.0.0-rc1** (conceptual reference)

See [ROADMAP.md](ROADMAP.md) · [DEPRECATIONS.md](DEPRECATIONS.md) · [RELEASE_NOTES_1.0-rc1.md](RELEASE_NOTES_1.0-rc1.md)

---

## Philosophy

PSS is **not** “magic words that make the LLM smarter.”

It **structures the problem** so the LLM can answer under clear conditions:

- what to achieve (**Mission**)
- what is known / unknown (**Knowledge** — Observation / Inference / Assumption / Unknown / Missing)
- how far to predict (**PredictionPolicy**)
- when to stop or ask (**Gate** — diagnosis only)
- what to value (**EvaluationCriteria**)

Less guessing load → more of the model’s capacity goes into the answer.

Full usage: **[docs/USAGE.md](docs/USAGE.md)**

---

## Architecture

![PSS Architecture](docs/architecture.svg)

See also: [docs/architecture.svg](docs/architecture.svg) · [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) · [docs/PSS_Detailed_Test_Results.md](docs/PSS_Detailed_Test_Results.md) · **[Behavioral tests](docs/tests/README.md)** · **[Usage](docs/USAGE.md)**

---

## Public API (package 0.9.1)

```python
from pss import (
    ProblemSpecification,
    ProblemBuilder,
    validate,
    plan_fixes,
    to_capsule,
    from_capsule,
    compile_for_generic,   # mode="balanced" | "strict"
    render_specification,
    Mission,
    PredictionPolicy,
    EvaluationCriteria,
    GateResult,
)
```

Single-file (copy-paste RC reference): [`pss_single.py`](pss_single.py)

```bash
python pss_single.py
```

---

## How to use (two patterns)

1. **Human writes structured input** → `ProblemBuilder`
2. **LLM converts natural language → PSS fields** (no guessing; unknowns → Unknown/Missing) → `ProblemBuilder`

PSS does **not** parse natural language. That step is human or a front-end LLM.

---

## Layers

| Layer            | Responsibility                              |
|------------------|---------------------------------------------|
| **Specification**| What is defined (data structures)           |
| **Builder**      | How to construct a specification            |
| **Adapter**      | How to present it to an LLM                 |
| **Validator**    | What is wrong or incomplete (diagnosis only)|
| **Fix Planner**  | How to fix it (plan only, no side effects)  |

Executor, CLI, and IDE integrations live **outside** the core.

**RC pillars:** Mission · ThinkingProfile · PredictionPolicy · EvaluationCriteria  
**Ops:** Phase · Gate (diagnosis only) · Behavior · Validator

---

## Behavioral tests

→ **[docs/tests/](docs/tests/README.md)**

| # | Case | Point |
|---|------|--------|
| 01 | Used car | Gate BLOCK / no premature car pick |
| 02 | Web release | Gate PASS / stay in scope |
| 03 | Stock forecast | Gate PASS, prediction refused |
| 04 | Code review | No scope violation |
| 05 | Model comparison | No assertion without evidence |

---

## Versioning & Dual-track

| Track | Version | Status | Notes |
|-------|---------|--------|-------|
| Package `pss/` | **0.9.1** | API freeze candidate | Mission + PredictionPolicy + Gate 追加済み |
| Single-file | 1.0.0-rc1 | Conceptual freeze | |
| Future | 1.0.0 | Target | 最終揃え |

**Sequential improvement** → [ROADMAP.md](ROADMAP.md) · [DEPRECATIONS.md](DEPRECATIONS.md)

---

## Design decisions

- **No Executor in core**
- **Behavior as executable rules**
- **Observation vs Inference** (strict separation)
- **Gate diagnoses only — never mutates the specification**
- **Not magic prompts — structure problems for full model capacity**

---

## License

Non-Commercial / Non-Military License
