# PSS v0.9 Release Notes

**Status**: API freeze candidate toward v1.0  
**Schema**: `pss.problem_specification/0.9`

---

## What v0.9 aims for

v0.9 is not “feature complete”.  
It is the first release that **promises a stable public API and design principles**.

From this point:

- The eight public symbols below are considered stable for the upcoming v1.x series.
- Deprecated symbols continue to work through v1.x and are scheduled for removal in v2.0.
- New major features will prefer satellite packages over core growth.

---

## Public API

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

---

## Design principles locked in

1. PSS defines **thinking conditions**, not answers.
2. Behavior is expressed as **executable rules** (`if_unknown`, `if_assumption`, …).
3. Knowledge separates **Observation / Inference / Assumption / Unknown**.
4. Validator and Fix Planner **never mutate** the specification.
5. Executor / CLI / IDE tools stay **outside** the core library.

---

## Deprecated in v0.9

| Item | Replacement | Removal |
|------|-------------|--------|
| `ProblemBuilder.agent_role(...)` | `.behavior(role=..., role_description=...)` | v2.0 |
| Dict keys `known`, `agent_role`, `extensions`, `evidence_policy` | `observation`, `behavior`, `evidence_level` | v2.0 |

---

## Versioning

- **v0.9** — current (API freeze)
- **v1.x** — compatibility maintained; deprecations still available
- **v2.0** — may remove deprecated APIs

---

## Roadmap sketch

- **v1.0** — Official stable tag (same surface as 0.9)
- **v1.1+** — Examples, docs polish, additional tests
- **v2.0** — Legacy removal

---

## Tests

17 tests covering Builder, Serialization, Validator, Fix Planner, Adapter, and edge cases — all passing at the time of this release.
