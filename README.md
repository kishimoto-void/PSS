# PSS — Problem Specification System

**PSS is a shared specification of thinking conditions** for humans, agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

It is not a prompt template.  
It is not an agent framework.  
It is a lightweight, model-independent library for writing, validating, and improving problem specifications.

**Current version: 0.9.0** (API freeze toward v1.0) · single-file RC: **1.0.0-rc1**

---

## Architecture

![PSS Architecture](docs/architecture.svg)

See also: [docs/architecture.svg](docs/architecture.svg) · [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) · [docs/PSS_Detailed_Test_Results.md](docs/PSS_Detailed_Test_Results.md) · **[Behavioral tests](docs/tests/README.md)** · **[Usage](docs/USAGE.md)**

---

## Public API (frozen toward v1.0)

```python
from pss import (
    ProblemSpecification,
    ProblemBuilder,
    validate,
    plan_fixes,
    to_capsule,
    from_capsule,
    compile_for_generic,
    render_specification,
)
```

These eight symbols form the **official public surface**.  
Other imports remain available for advanced use but are not part of the frozen contract.

---

## Core Principle

```text
PSS does not solve problems.
PSS defines problems.
PSS produces a Problem Specification.
Primary I/O can be a PLP Capsule (optional).
Phase transitions and behavior rules are owned by the program, not the LLM.
```

---

## How to use (two patterns)

1. **Human writes structured input** → `ProblemBuilder`
2. **LLM converts natural language → PSS fields** (no guessing; unknowns go to Unknown/Missing) → `ProblemBuilder`

PSS does **not** parse natural language. That step is human or a front-end LLM.

Full guide: **[docs/USAGE.md](docs/USAGE.md)**

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

---

## Basic Usage

```python
from pss import ProblemBuilder, validate, plan_fixes, compile_for_generic

spec = (
    ProblemBuilder()
    .identity(title="進捗報告資料の作成", domain="business.document")
    .goal(description="会議で使える完成度の高い資料を提出する")
    .knowledge(
        observation=["会議は来週火曜", "Wordで提出"],
        unknown=["正式な出力フォーマット"],
    )
    .behavior(
        role="collaborator",
        if_unknown="answer_unknown",
        if_assumption="mark_assumption",
    )
    .phase(phase="1_clarify")
    .build()
)

report = validate(spec)
if report.overall.value != "PASS":
    print(plan_fixes(report).summary())

prompt = compile_for_generic(spec)
```

Single-file edition (copy-paste): [`pss_single.py`](pss_single.py)

---

## Behavioral tests

→ **[docs/tests/](docs/tests/README.md)**

| # | ケース | 要点 |
|---|--------|------|
| 01 | 中古車購入 | Gate BLOCK / 車種を勝手に勧めない |
| 02 | Webリリース | Gate PASS / Scope内のみ |
| 03 | 株価予測 | Gate PASS だが予測拒否 |
| 04 | コードレビュー | Scope逸脱しない |
| 05 | 性能比較 | 根拠なしで断定しない |

---

## Deprecations (v0.9)

| Symbol | Status | Replacement | Removal target |
|--------|--------|-------------|----------------|
| `ProblemBuilder.agent_role(...)` | Deprecated | `.behavior(role=..., role_description=...)` | v2.0 |
| Old dict keys (`known`, `agent_role`, `extensions`, `evidence_policy`) | Accepted in `from_dict` | New keys (`observation`, `behavior`, `evidence_level`) | v2.0 |

---

## Versioning Policy

- **v0.9** — package API freeze candidate
- **v1.0.0-rc1** — single-file conceptual freeze
- **v1.x** — compatibility maintained
- **v2.0** — may remove deprecated symbols

---

## Design Decisions

- **No Executor in core**
- **Behavior as executable rules**
- **Observation vs Inference**
- **Gate diagnoses only — never mutates the specification**

---

## Status

- Package: **0.9.0**
- Single-file RC: **1.0.0-rc1**
- Usage: [docs/USAGE.md](docs/USAGE.md)
- Behavioral tests: [docs/tests](docs/tests/README.md)

---

## License

Non-Commercial / Non-Military License
