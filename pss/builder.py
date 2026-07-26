"""
PSS ProblemBuilder (v0.9)
=========================
Fluent Interface for building thinking-condition specifications.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from .core import (
    Identity, Objective, CurrentState, Goal, Difference,
    Constraints, ConstraintSpec, Scope, KnowledgeState,
    ThinkingProfile, Behavior, BehaviorRules, OutputSpec,
    EvaluationAxis, PhaseState, ProblemSpecification,
)


class ProblemBuilder:
    def __init__(self) -> None:
        self._identity = Identity()
        self._objective = Objective()
        self._constraints = Constraints()
        self._scope = Scope()
        self._knowledge = KnowledgeState()
        self._thinking = ThinkingProfile()
        self._behavior = Behavior()
        self._output = OutputSpec()
        self._evaluation = EvaluationAxis()
        self._phase = PhaseState()

    # Identity
    def title(self, title: str) -> "ProblemBuilder":
        self._identity.title = title
        return self

    def domain(self, domain: str) -> "ProblemBuilder":
        self._identity.domain = domain
        return self

    def description(self, desc: str) -> "ProblemBuilder":
        self._identity.description = desc
        return self

    def identity(self, title: str = "", domain: str = "", description: str = "") -> "ProblemBuilder":
        if title: self._identity.title = title
        if domain: self._identity.domain = domain
        if description: self._identity.description = description
        return self

    # Objective
    def current_state(self, description: str = "", facts: Optional[Dict[str, Any]] = None) -> "ProblemBuilder":
        self._objective.current_state = CurrentState(description=description, facts=dict(facts or {}))
        return self

    def goal(self, description: str = "", target: Optional[Dict[str, Any]] = None, success_criteria: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        self._objective.goal = Goal(description=description, target=dict(target or {}), success_criteria=list(success_criteria or []))
        if success_criteria:
            self._objective.success_criteria = list(success_criteria)
        return self

    def difference(self, description: str = "", gaps: Optional[Sequence[str]] = None, excesses: Optional[Sequence[str]] = None, quantitative: Optional[Dict[str, float]] = None) -> "ProblemBuilder":
        self._objective.difference = Difference(description=description, gaps=list(gaps or []), excesses=list(excesses or []), quantitative=dict(quantitative or {}))
        return self

    # Constraints
    def add_constraint(self, statement: str, kind: str = "hard", priority: int = 0, **metadata: Any) -> "ProblemBuilder":
        c = ConstraintSpec(statement=statement, kind=kind, priority=priority, metadata=dict(metadata))
        if kind == "hard": self._constraints.hard.append(c)
        elif kind == "soft": self._constraints.soft.append(c)
        elif kind == "assumption": self._constraints.assumptions.append(c)
        elif kind == "risk": self._constraints.risks.append(c)
        else: self._constraints.hard.append(c)
        return self

    def add_default_safety_constraints(self) -> "ProblemBuilder":
        for stmt, pri in [
            ("推測しない。不明な点は不明と明示する。", 10),
            ("不可能なことは不可能と言う。", 10),
            ("制約違反を隠さない。", 10),
            ("不足情報を明示する。", 9),
        ]:
            self.add_constraint(stmt, kind="hard", priority=pri)
        return self

    def hard_constraint(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="hard", priority=priority)

    def soft_constraint(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="soft", priority=priority)

    def risk(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="risk", priority=priority)

    # Scope
    def scope(self, in_scope: Optional[Sequence[str]] = None, out_of_scope: Optional[Sequence[str]] = None, priority: Optional[Sequence[str]] = None, allowed_changes: Optional[Sequence[str]] = None, notes: str = "") -> "ProblemBuilder":
        if in_scope is not None: self._scope.in_scope = list(in_scope)
        if out_of_scope is not None: self._scope.out_of_scope = list(out_of_scope)
        if priority is not None: self._scope.priority = list(priority)
        if allowed_changes is not None: self._scope.allowed_changes = list(allowed_changes)
        if notes: self._scope.notes = notes
        return self

    # Knowledge
    def knowledge(self, observation: Optional[Sequence[str]] = None, inference: Optional[Sequence[str]] = None, assumption: Optional[Sequence[str]] = None, unknown: Optional[Sequence[str]] = None, missing: Optional[Sequence[str]] = None, references: Optional[Sequence[str]] = None, known: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        if known is not None:
            self._knowledge.observation = list(known)
        if observation is not None: self._knowledge.observation = list(observation)
        if inference is not None: self._knowledge.inference = list(inference)
        if assumption is not None: self._knowledge.assumption = list(assumption)
        if unknown is not None: self._knowledge.unknown = list(unknown)
        if missing is not None: self._knowledge.missing = list(missing)
        if references is not None: self._knowledge.references = list(references)
        return self

    def known(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.observation = list(items)
        return self

    def unknown(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.unknown = list(items)
        return self

    def assumption(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.assumption = list(items)
        return self

    # Thinking
    def thinking_profile(self, reasoning_bias: str = "balanced", depth: str = "normal", evidence_level: str = "observation_first", custom_bias_note: str = "") -> "ProblemBuilder":
        self._thinking = ThinkingProfile(reasoning_bias=reasoning_bias, depth=depth, evidence_level=evidence_level, custom_bias_note=custom_bias_note)
        return self

    # Behavior
    def behavior(
        self,
        role: str = "collaborator",
        role_description: str = "",
        confidence_policy: str = "medium_plus",
        interaction_policy: str = "question_first",
        criticism_level: str = "1_normal",
        question_first: bool = True,
        proposal_level: str = "normal",
        challenge_probability: str = "medium",
        if_unknown: str = "answer_unknown",
        if_assumption: str = "mark_assumption",
        if_scope_violation: str = "stop",
        if_missing_required: str = "ask",
        if_low_confidence: str = "state_confidence",
    ) -> "ProblemBuilder":
        self._behavior = Behavior(
            role=role,
            role_description=role_description,
            confidence_policy=confidence_policy,
            interaction_policy=interaction_policy,
            criticism_level=criticism_level,
            question_first=question_first,
            proposal_level=proposal_level,
            challenge_probability=challenge_probability,
            rules=BehaviorRules(
                if_unknown=if_unknown,
                if_assumption=if_assumption,
                if_scope_violation=if_scope_violation,
                if_missing_required=if_missing_required,
                if_low_confidence=if_low_confidence,
            ),
        )
        return self

    def agent_role(self, role: str = "collaborator", custom_description: str = "") -> "ProblemBuilder":
        """Deprecated: use .behavior(role=..., role_description=...) instead.
        Kept for compatibility in v0.9 / v1.x. Planned removal in v2.0.
        """
        self._behavior.role = role
        self._behavior.role_description = custom_description
        return self

    # Output
    def output(self, format: str = "markdown", style: str = "clear", length: str = "medium", language: str = "ja", required_sections: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        self._output = OutputSpec(format=format, style=style, length=length, language=language, required_sections=list(required_sections or []))
        return self

    # Evaluation
    def evaluation_axis(self, axes: Dict[str, float], notes: str = "") -> "ProblemBuilder":
        self._evaluation = EvaluationAxis(axes=dict(axes), notes=notes)
        return self

    # Phase
    def phase(self, phase: str = "1_clarify", cycle: int = 1, scope: str = "", scope_agreed: bool = False) -> "ProblemBuilder":
        self._phase = PhaseState(phase=phase, cycle=cycle, scope=scope, scope_agreed=scope_agreed)
        return self

    def build(self) -> ProblemSpecification:
        knowledge = KnowledgeState(
            observation=list(self._knowledge.observation),
            inference=list(self._knowledge.inference),
            assumption=list(self._knowledge.assumption),
            unknown=list(self._knowledge.unknown),
            missing=list(self._knowledge.missing),
            references=list(self._knowledge.references),
        )
        for m in knowledge.missing:
            if m not in knowledge.unknown:
                knowledge.unknown.append(m)

        return ProblemSpecification(
            identity=self._identity,
            objective=self._objective,
            constraints=self._constraints,
            scope=self._scope,
            knowledge=knowledge,
            thinking_profile=self._thinking,
            behavior=self._behavior,
            output=self._output,
            evaluation=self._evaluation,
            phase_state=self._phase,
        )
