"""
PSS ProblemBuilder (v0.5)
=========================
段階的に ProblemSpecification を構築する Fluent Interface。
v0.5: Identity / Objective / Constraints / Scope / Knowledge /
      ThinkingProfile / AgentRole / Output / Extensions を正式サポート。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from .core import (
    Identity,
    Objective,
    CurrentState,
    Goal,
    Difference,
    Constraints,
    ConstraintSpec,
    Scope,
    KnowledgeState,
    ThinkingProfile,
    AgentRoleSpec,
    OutputSpec,
    EvaluationAxis,
    ExtensionOptions,
    ProblemSpecification,
    ReasoningBias,
    Depth,
    EvidencePolicy,
    AgentRole,
    Audience,
    ConfidencePolicy,
    InteractionPolicy,
    CriticismLevel,
)


class ProblemBuilder:
    """Fluent interface で思考条件仕様書を組み立てる。"""

    def __init__(self) -> None:
        self._identity = Identity()
        self._objective = Objective()
        self._constraints = Constraints()
        self._scope = Scope()
        self._knowledge = KnowledgeState()
        self._thinking = ThinkingProfile()
        self._agent_role = AgentRoleSpec()
        self._output = OutputSpec()
        self._evaluation = EvaluationAxis()
        self._extensions = ExtensionOptions()

    # ------------------------------------------------------------------
    # 1. Identity
    # ------------------------------------------------------------------
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
        if title:
            self._identity.title = title
        if domain:
            self._identity.domain = domain
        if description:
            self._identity.description = description
        return self

    # ------------------------------------------------------------------
    # 2. Objective
    # ------------------------------------------------------------------
    def current_state(
        self,
        description: str = "",
        facts: Optional[Dict[str, Any]] = None,
    ) -> "ProblemBuilder":
        self._objective.current_state = CurrentState(
            description=description,
            facts=dict(facts or {}),
        )
        return self

    def goal(
        self,
        description: str = "",
        target: Optional[Dict[str, Any]] = None,
        success_criteria: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        self._objective.goal = Goal(
            description=description,
            target=dict(target or {}),
            success_criteria=list(success_criteria or []),
        )
        if success_criteria:
            self._objective.success_criteria = list(success_criteria)
        return self

    def difference(
        self,
        description: str = "",
        gaps: Optional[Sequence[str]] = None,
        excesses: Optional[Sequence[str]] = None,
        quantitative: Optional[Dict[str, float]] = None,
    ) -> "ProblemBuilder":
        self._objective.difference = Difference(
            description=description,
            gaps=list(gaps or []),
            excesses=list(excesses or []),
            quantitative=dict(quantitative or {}),
        )
        return self

    # ------------------------------------------------------------------
    # 3. Constraints
    # ------------------------------------------------------------------
    def add_constraint(
        self,
        statement: str,
        kind: str = "hard",
        priority: int = 0,
        **metadata: Any,
    ) -> "ProblemBuilder":
        c = ConstraintSpec(statement=statement, kind=kind, priority=priority, metadata=dict(metadata))
        if kind == "hard":
            self._constraints.hard.append(c)
        elif kind == "soft":
            self._constraints.soft.append(c)
        elif kind == "assumption":
            self._constraints.assumptions.append(c)
        elif kind == "risk":
            self._constraints.risks.append(c)
        else:
            self._constraints.hard.append(c)
        return self

    def add_default_safety_constraints(self) -> "ProblemBuilder":
        defaults = [
            ("推測しない。不明な点は不明と明示する。", 10),
            ("不可能なことは不可能と言う。", 10),
            ("制約違反を隠さない。", 10),
            ("不足情報を明示する。", 9),
        ]
        for stmt, pri in defaults:
            self.add_constraint(stmt, kind="hard", priority=pri)
        return self

    def hard_constraint(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="hard", priority=priority)

    def soft_constraint(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="soft", priority=priority)

    def risk(self, statement: str, priority: int = 0) -> "ProblemBuilder":
        return self.add_constraint(statement, kind="risk", priority=priority)

    # ------------------------------------------------------------------
    # 4. Scope
    # ------------------------------------------------------------------
    def scope(
        self,
        in_scope: Optional[Sequence[str]] = None,
        out_of_scope: Optional[Sequence[str]] = None,
        priority: Optional[Sequence[str]] = None,
        allowed_changes: Optional[Sequence[str]] = None,
        notes: str = "",
    ) -> "ProblemBuilder":
        if in_scope is not None:
            self._scope.in_scope = list(in_scope)
        if out_of_scope is not None:
            self._scope.out_of_scope = list(out_of_scope)
        if priority is not None:
            self._scope.priority = list(priority)
        if allowed_changes is not None:
            self._scope.allowed_changes = list(allowed_changes)
        if notes:
            self._scope.notes = notes
        return self

    # ------------------------------------------------------------------
    # 5. Knowledge
    # ------------------------------------------------------------------
    def knowledge(
        self,
        known: Optional[Sequence[str]] = None,
        unknown: Optional[Sequence[str]] = None,
        missing: Optional[Sequence[str]] = None,
        assumption: Optional[Sequence[str]] = None,
        references: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        if known is not None:
            self._knowledge.known = list(known)
        if unknown is not None:
            self._knowledge.unknown = list(unknown)
        if missing is not None:
            self._knowledge.missing = list(missing)
        if assumption is not None:
            self._knowledge.assumption = list(assumption)
        if references is not None:
            self._knowledge.references = list(references)
        return self

    def known(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.known = list(items)
        return self

    def unknown(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.unknown = list(items)
        return self

    def assumption(self, items: Sequence[str]) -> "ProblemBuilder":
        self._knowledge.assumption = list(items)
        return self

    # ------------------------------------------------------------------
    # 6. Thinking Profile
    # ------------------------------------------------------------------
    def thinking_profile(
        self,
        reasoning_bias: str = "balanced",
        depth: str = "normal",
        evidence_policy: str = "observation_first",
        custom_bias_note: str = "",
    ) -> "ProblemBuilder":
        self._thinking = ThinkingProfile(
            reasoning_bias=reasoning_bias,
            depth=depth,
            evidence_policy=evidence_policy,
            custom_bias_note=custom_bias_note,
        )
        return self

    # ------------------------------------------------------------------
    # 7. Agent Role
    # ------------------------------------------------------------------
    def agent_role(self, role: str = "collaborator", custom_description: str = "") -> "ProblemBuilder":
        self._agent_role = AgentRoleSpec(role=role, custom_description=custom_description)
        return self

    # ------------------------------------------------------------------
    # 8. Output
    # ------------------------------------------------------------------
    def output(
        self,
        format: str = "markdown",
        style: str = "clear",
        length: str = "medium",
        language: str = "ja",
        required_sections: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        self._output = OutputSpec(
            format=format,
            style=style,
            length=length,
            language=language,
            required_sections=list(required_sections or []),
        )
        return self

    # ------------------------------------------------------------------
    # 9. Evaluation
    # ------------------------------------------------------------------
    def evaluation_axis(
        self,
        axes: Dict[str, float],
        notes: str = "",
    ) -> "ProblemBuilder":
        self._evaluation = EvaluationAxis(axes=dict(axes), notes=notes)
        return self

    # ------------------------------------------------------------------
    # 10. Extensions
    # ------------------------------------------------------------------
    def extensions(
        self,
        audience: str = "general_user",
        confidence_policy: str = "medium_plus",
        interaction_policy: str = "question_first",
        criticism_level: str = "1_normal",
        **custom: Any,
    ) -> "ProblemBuilder":
        self._extensions = ExtensionOptions(
            audience=audience,
            confidence_policy=confidence_policy,
            interaction_policy=interaction_policy,
            criticism_level=criticism_level,
            custom=dict(custom),
        )
        return self

    def audience(self, value: str) -> "ProblemBuilder":
        self._extensions.audience = value
        return self

    def confidence_policy(self, value: str) -> "ProblemBuilder":
        self._extensions.confidence_policy = value
        return self

    def interaction_policy(self, value: str) -> "ProblemBuilder":
        self._extensions.interaction_policy = value
        return self

    def criticism_level(self, value: str) -> "ProblemBuilder":
        self._extensions.criticism_level = value
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self) -> ProblemSpecification:
        # merge missing into unknown for safety
        knowledge = KnowledgeState(
            known=list(self._knowledge.known),
            unknown=list(self._knowledge.unknown),
            missing=list(self._knowledge.missing),
            assumption=list(self._knowledge.assumption),
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
            agent_role=self._agent_role,
            output=self._output,
            evaluation=self._evaluation,
            extensions=self._extensions,
        )
