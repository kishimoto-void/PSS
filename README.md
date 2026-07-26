# PSS — Problem Specification System

**PSS is a shared specification of thinking conditions** for humans, agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

It is not a prompt template.  
It is not an agent framework.  
It is a lightweight, model-independent library for writing, validating, and improving problem specifications.

**Current version: 0.9.0** (API freeze toward v1.0)

---

## Architecture

![PSS Architecture](docs/architecture.svg)

See also: [docs/architecture.svg](docs/architecture.svg) · [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)

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

---

## Deprecations (v0.9)

| Symbol | Status | Replacement | Removal target |
|--------|--------|-------------|----------------|
| `ProblemBuilder.agent_role(...)` | Deprecated | `.behavior(role=..., role_description=...)` | v2.0 |
| Old dict keys (`known`, `agent_role`, `extensions`, `evidence_policy`) | Accepted in `from_dict` for compatibility | New keys (`observation`, `behavior`, `evidence_level`) | v2.0 |

Deprecated symbols continue to work in v0.9 and the entire v1.x series.

---

## Versioning Policy

PSS follows **Semantic Versioning**:

- **v0.9** — API freeze candidate (current)
- **v1.x** — Public API compatibility is maintained. Deprecated symbols remain available.
- **v2.0** — May remove deprecated symbols and make intentional breaking changes.

---

## Design Decisions

- **No Executor in core** — Keeps PSS a specification library.
- **Behavior as executable rules** — Reduces model-to-model variance.
- **Observation vs Inference** — Makes “I don’t know” and “I am assuming” explicit.
- **Validator / Fix Planner never mutate the specification** — Pure diagnosis and planning.

---

## Relationship with PLP

PSS works standalone.  
When systems need structured exchange, a PSS specification can ride inside a PLP Capsule without changing the thinking conditions.

---

## Status

- Version: **0.9.0**
- Schema: `pss.problem_specification/0.9`
- Tests: 17 passed
- Public API is considered stable for the upcoming v1.0 release.

Roadmap sketch:
- **v1.0** — Official stable release (same surface as 0.9)
- **v1.1+** — More examples, documentation polish
- **v2.0** — Remove deprecated APIs

---

## License

Non-Commercial / Non-Military License
