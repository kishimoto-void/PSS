# PSS — Problem Specification System (v0.5)

**PSS is not a prompt template.**  
**PSS is a shared specification of thinking conditions** for Humans, Agents, and LLMs.

> PSS does not solve problems.  
> PSS defines the conditions under which problems are thought about.

---

## Core Philosophy

PSS defines **how to think**, not **what to answer**.

- Goal, Constraints, Role, Thinking Profile, Scope, Knowledge  
  → the same conditions can be shared by a human, an agent, or an LLM.

This makes PSS a long-lived, model-independent framework for problem solving.

---

## Structure (v0.5)

```
1. Identity
2. Objective          (Goal / Current State / Difference / Success Criteria)
3. Constraints        (Hard / Soft / Assumptions / Risks)
4. Scope              (In / Out / Priority / Allowed Changes)
5. Knowledge          (Known / Unknown / Missing / Assumption / References)
6. Thinking Profile   (Reasoning Bias / Depth / Evidence Policy)
7. Agent Role         (Collaborator / Reviewer / Challenger / ...)
8. Output             (Format / Style / Length / Language / Required Sections)
9. Evaluation         (Accuracy / Safety / Clarity / ...)
10. Phase             (Clarify → Confirm → Answer + Cycle State)

+ Extension Options
  - Audience
  - Confidence Policy
  - Interaction Policy
  - Criticism Level
```

---

## Which should I use?

### Use PSS if...
- You want a lightweight, shared thinking-condition framework.
- You are using a single LLM or a small number of agents.
- You want humans and agents to work under the same conditions.
- You want to integrate quickly.

PSS works as a standalone framework and does not require PLP.

### Use PLP if...
- You need long-term maintainability and standardized transport.
- Multiple agents or runtimes exchange structured information.
- You want Capsules and interoperable components.

PLP provides the common architecture and transport that PSS (and other specifications) can ride on.

---

## Relationship

```
PSS
 └── Standalone Thinking-Condition Framework

PLP
 ├── Capsule
 ├── Protocol
 ├── Core
 ├── PSS
 ├── PGRA
 └── Future Specifications
```

When interoperability becomes important, a PSS specification can be transported inside a PLP Capsule without changing the thinking conditions themselves.

---

## Version

Current: **0.5**  
Schema: `pss.problem_specification/0.5`
