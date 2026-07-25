# PSS — Problem Specification System (v0.7)

**PSS is a shared specification of thinking conditions** for Humans, Agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

---

## Lifecycle (now complete)

```
Builder          →  write specification
Validator        →  diagnose (PASS / WARN / ERROR)
Fix Planner      →  produce Fix Plan (no side effects)
Executor         →  human / LLM / IDE / CI applies the plan
```

Validator never modifies the specification.  
Fix Planner only produces a plan.  
Execution is left to the caller.

---

## Layers

1. **Specification** — what is defined (Identity, Objective, Knowledge, Behavior, Phase…)
2. **Builder** — constructs the specification
3. **Adapter** — turns it into LLM-readable form
4. **Validator** — diagnoses quality (independent of Specification)
5. **Fix Planner** — turns Findings into an ordered, executable plan

---

## Example

```python
from pss import ProblemBuilder, validate, plan_fixes

spec = ProblemBuilder().identity(title="").goal(description="").build()
report = validate(spec)
plan = plan_fixes(report)

print(report.summary())
print(plan.summary())
```

---

## Version

Current: **0.7**  
Core schema: `pss.problem_specification/0.6`  
Validator + Planner: 0.7
