# PSS — Problem Specification System (v0.7)

**PSS is a shared specification of thinking conditions** for Humans, Agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

---

## v0.7: Validator

PSS now includes a **diagnostic Validator**.

It does not simply say Yes/No. It produces a structured report:

```
Validation Report

PASS / WARN / ERROR

Coverage
---------
Scope      PASS
Phase      PASS
Knowledge  WARN
Behavior   PASS
Output     PASS

Warnings
--------
Knowledge:
- inference exists without observation
  → Suggestion: ...
```

### Independent Validators

- IdentityValidator
- ObjectiveValidator
- ScopeValidator
- PhaseValidator
- BehaviorValidator
- KnowledgeValidator
- ConstraintValidator
- OutputValidator

`CompositeValidator` aggregates them into one report.

This makes PSS ready for CI and for human-readable diagnosis.

---

## Structure (v0.6 + v0.7)

```
PSS Capsule / ProblemSpecification
├── Identity
├── Objective
├── Constraints
├── Scope
├── Knowledge          (Observation / Inference / Assumption / Unknown)
├── ThinkingProfile
├── Behavior           (executable rules)
├── Output
├── Evaluation
└── PhaseState

+ Validator (diagnostic)
```

---

## Design Principle

PSS defines **how to think**, not **what to answer**.

With the Validator, PSS now supports the cycle:

**Write → Validate → Improve**

---

## Version

Current: **0.7**  
Schema: `pss.problem_specification/0.6` (core) + Validator 0.7
