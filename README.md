# PSS — Problem Specification System (v0.6)

**PSS is a shared specification of thinking conditions** for Humans, Agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

---

## v0.6 Key Changes

- **PhaseState integrated** into ProblemSpecification → Capsule alone carries full state
- **Behavior** newly introduced: consolidates Role / Confidence / Interaction / Criticism into **executable rules**
- Knowledge separated into **Observation / Inference / Assumption / Unknown**
- From declarative labels toward **actionable behavior rules** (if_unknown → answer_unknown etc.)

---

## Structure (v0.6)

```
PSS Capsule / ProblemSpecification
├── Identity
├── Objective
├── Constraints
├── Scope
├── Knowledge          (Observation / Inference / Assumption / Unknown)
├── ThinkingProfile
├── Behavior           ← NEW (executable rules)
├── Output
├── Evaluation
└── PhaseState         ← integrated
```

### Behavior Rules (example)

```yaml
rules:
  if_unknown: answer_unknown
  if_assumption: mark_assumption
  if_scope_violation: stop
  if_missing_required: ask
  if_low_confidence: state_confidence
```

This turns policy declarations into concrete actions that Agents and LLMs can follow without ambiguity.

---

## Design Principle

PSS defines **how to think**, not **what to answer**.

The same specification can be shared by a human, an agent, or an LLM.

---

## Version

Current: **0.6**  
Schema: `pss.problem_specification/0.6`
