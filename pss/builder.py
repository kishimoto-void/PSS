"""
PSS ProblemBuilder (v0.3)
=========================
段階的に ProblemSpecification を構築する便利インターフェース。
主入力経路は Capsule だが、手動組み立て用に残す。
推論・Sub-Goal生成・知識補完は一切行わない。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from .core import (
    Problem,
    CurrentState,
    Goal,
    Difference,
    ConstraintSpec,
    SectionGate,
    EvaluationAxis,
    Tolerance,
    KnowledgeState,
    ProblemSpecification,
)


class ProblemBuilder:
    """Fluent interface で問題仕様書を組み立てる。"""

    def __init__(self) -> None:
        self._problem = Problem()
        self._current = CurrentState()
        self._goal = Goal()
        self._difference = Difference()
        self._constraints: List[ConstraintSpec] = []
        self._section_gate: Optional[SectionGate] = None
        self._knowledge = KnowledgeState()
        self._eval_axis = EvaluationAxis()
        self._tolerance = Tolerance()

    def title(self, title: str) -> "ProblemBuilder":
        self._problem.title = title
        return self

    def description(self, desc: str) -> "ProblemBuilder":
        self._problem.description = desc
        return self

    def domain(self, domain: str) -> "ProblemBuilder":
        self._problem.domain = domain
        return self

    def current_state(
        self,
        description: str = "",
        facts: Optional[Dict[str, Any]] = None,
    ) -> "ProblemBuilder":
        self._current = CurrentState(
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
        self._goal = Goal(
            description=description,
            target=dict(target or {}),
            success_criteria=list(success_criteria or []),
        )
        return self

    def difference(
        self,
        description: str = "",
        gaps: Optional[Sequence[str]] = None,
        excesses: Optional[Sequence[str]] = None,
        quantitative: Optional[Dict[str, float]] = None,
    ) -> "ProblemBuilder":
        self._difference = Difference(
            description=description,
            gaps=list(gaps or []),
            excesses=list(excesses or []),
            quantitative=dict(quantitative or {}),
        )
        return self

    def add_constraint(
        self,
        statement: str,
        kind: str = "hard",
        priority: int = 0,
        **metadata: Any,
    ) -> "ProblemBuilder":
        self._constraints.append(
            ConstraintSpec(
                statement=statement,
                kind=kind,
                priority=priority,
                metadata=dict(metadata),
            )
        )
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

    def section_gate(
        self,
        name: str,
        required_fields: Sequence[str],
        available_fields: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        gate = SectionGate(
            name=name,
            required_fields=list(required_fields),
        )
        if available_fields is not None:
            gate = gate.evaluate(available_fields)
        else:
            gate.missing_fields = list(required_fields)
        self._section_gate = gate
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

    def knowledge(
        self,
        known: Optional[Sequence[str]] = None,
        unknown: Optional[Sequence[str]] = None,
        assumption: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        if known is not None:
            self._knowledge.known = list(known)
        if unknown is not None:
            self._knowledge.unknown = list(unknown)
        if assumption is not None:
            self._knowledge.assumption = list(assumption)
        return self

    def evaluation_axis(
        self,
        axes: Dict[str, float],
        notes: str = "",
    ) -> "ProblemBuilder":
        self._eval_axis = EvaluationAxis(axes=dict(axes), notes=notes)
        return self

    def tolerance(
        self,
        description: str = "",
        quantitative: Optional[Dict[str, float]] = None,
        qualitative: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        self._tolerance = Tolerance(
            description=description,
            quantitative=dict(quantitative or {}),
            qualitative=list(qualitative or []),
        )
        return self

    def build(self) -> ProblemSpecification:
        knowledge = KnowledgeState(
            known=list(self._knowledge.known),
            unknown=list(self._knowledge.unknown),
            assumption=list(self._knowledge.assumption),
        )
        if self._section_gate and not self._section_gate.is_complete:
            for m in self._section_gate.missing_fields:
                if m not in knowledge.unknown:
                    knowledge.unknown.append(m)

        return ProblemSpecification(
            problem=self._problem,
            current_state=self._current,
            goal=self._goal,
            difference=self._difference,
            constraints=list(self._constraints),
            section_gate=self._section_gate,
            knowledge=knowledge,
            evaluation_axis=self._eval_axis,
            tolerance=self._tolerance,
        )
