"""
PSS Core Data Structures (v0.3)
===============================
Problem Specification System — 問題仕様書を構成する最小単位。

設計原則:
  - PSS は問題を「定義・構造化」するだけ
  - 推論・知識補完・Sub-Goal生成は一切行わない
  - Known / Unknown / Assumption を明確に分離する
  - 主入力は PLP Capsule
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4
import time


# ------------------------------------------------------------------
# Knowledge triad
# ------------------------------------------------------------------

@dataclass
class KnowledgeState:
    """
    Known / Unknown / Assumption の三つ組。
    LLM が勝手に補完しやすい「Assumption」を明示的に切り出す。
    """
    known: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    assumption: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "known": list(self.known),
            "unknown": list(self.unknown),
            "assumption": list(self.assumption),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeState":
        return cls(
            known=list(data.get("known") or []),
            unknown=list(data.get("unknown") or []),
            assumption=list(data.get("assumption") or []),
        )


# ------------------------------------------------------------------
# Core blocks
# ------------------------------------------------------------------

@dataclass
class CurrentState:
    """現在の観測可能な状態。解釈はしない。"""
    description: str = ""
    facts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "facts": dict(self.facts),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CurrentState":
        return cls(
            description=str(data.get("description", "")),
            facts=dict(data.get("facts") or {}),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class Goal:
    """望ましい到達状態。完全一致を強制しない。"""
    description: str = ""
    target: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "target": dict(self.target),
            "success_criteria": list(self.success_criteria),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        return cls(
            description=str(data.get("description", "")),
            target=dict(data.get("target") or {}),
            success_criteria=list(data.get("success_criteria") or []),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class Difference:
    """Current → Goal の差分。この差分を最小化するための仕様を生成する。"""
    description: str = ""
    gaps: List[str] = field(default_factory=list)
    excesses: List[str] = field(default_factory=list)
    quantitative: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "gaps": list(self.gaps),
            "excesses": list(self.excesses),
            "quantitative": dict(self.quantitative),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Difference":
        return cls(
            description=str(data.get("description", "")),
            gaps=list(data.get("gaps") or []),
            excesses=list(data.get("excesses") or []),
            quantitative={k: float(v) for k, v in (data.get("quantitative") or {}).items()},
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class ConstraintSpec:
    """絶対条件。推論器が守るべきハード制約を明示する。"""
    id: str = field(default_factory=lambda: str(uuid4()))
    statement: str = ""
    kind: str = "hard"
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "kind": self.kind,
            "priority": self.priority,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConstraintSpec":
        return cls(
            id=str(data.get("id", str(uuid4()))),
            statement=str(data.get("statement", "")),
            kind=str(data.get("kind", "hard")),
            priority=int(data.get("priority", 0)),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class SectionGate:
    """
    必須情報の確認器。
    不足を検出したら Missing Requirement として報告するだけ。
    Sub-Goal は生成しない。
    """
    name: str = ""
    required_fields: List[str] = field(default_factory=list)
    present_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, available: Sequence[str] | None = None) -> "SectionGate":
        if available is not None:
            present = [f for f in self.required_fields if f in available]
            missing = [f for f in self.required_fields if f not in available]
            return SectionGate(
                name=self.name,
                required_fields=list(self.required_fields),
                present_fields=present,
                missing_fields=missing,
                metadata=dict(self.metadata),
            )
        return self

    @property
    def is_complete(self) -> bool:
        return len(self.missing_fields) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "required_fields": list(self.required_fields),
            "present_fields": list(self.present_fields),
            "missing_fields": list(self.missing_fields),
            "is_complete": self.is_complete,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SectionGate":
        return cls(
            name=str(data.get("name", "")),
            required_fields=list(data.get("required_fields") or []),
            present_fields=list(data.get("present_fields") or []),
            missing_fields=list(data.get("missing_fields") or []),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class EvaluationAxis:
    """評価軸と重み。相対優先度として扱う。"""
    axes: Dict[str, float] = field(default_factory=dict)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axes": dict(self.axes),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationAxis":
        axes = {str(k): float(v) for k, v in (data.get("axes") or {}).items()}
        return cls(
            axes=axes,
            notes=str(data.get("notes", "")),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class Tolerance:
    """完全一致を要求しないための許容範囲。"""
    description: str = ""
    quantitative: Dict[str, float] = field(default_factory=dict)
    qualitative: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "quantitative": dict(self.quantitative),
            "qualitative": list(self.qualitative),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tolerance":
        return cls(
            description=str(data.get("description", "")),
            quantitative={k: float(v) for k, v in (data.get("quantitative") or {}).items()},
            qualitative=list(data.get("qualitative") or []),
            metadata=dict(data.get("metadata") or {}),
        )


# ------------------------------------------------------------------
# Aggregate
# ------------------------------------------------------------------

@dataclass
class Problem:
    """問題そのもの（タイトルと文脈）。"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    domain: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Problem":
        return cls(
            id=str(data.get("id", str(uuid4()))),
            title=str(data.get("title", "")),
            description=str(data.get("description", "")),
            domain=str(data.get("domain", "")),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class ProblemSpecification:
    """
    PSS が最終的に生成する「問題仕様書」。

    構成:
      Problem / Current / Goal / Difference /
      Constraint / SectionGate /
      Known / Unknown / Assumption /
      Evaluation / Tolerance
    """
    problem: Problem = field(default_factory=Problem)
    current_state: CurrentState = field(default_factory=CurrentState)
    goal: Goal = field(default_factory=Goal)
    difference: Difference = field(default_factory=Difference)
    constraints: List[ConstraintSpec] = field(default_factory=list)
    section_gate: Optional[SectionGate] = None
    knowledge: KnowledgeState = field(default_factory=KnowledgeState)
    evaluation_axis: EvaluationAxis = field(default_factory=EvaluationAxis)
    tolerance: Tolerance = field(default_factory=Tolerance)
    created_at: float = field(default_factory=time.time)
    schema: str = "pss.problem_specification/0.3"
    version: str = "0.3"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "created_at": self.created_at,
            "problem": self.problem.to_dict(),
            "current_state": self.current_state.to_dict(),
            "goal": self.goal.to_dict(),
            "difference": self.difference.to_dict(),
            "constraints": [c.to_dict() for c in self.constraints],
            "section_gate": self.section_gate.to_dict() if self.section_gate else None,
            "knowledge": self.knowledge.to_dict(),
            "evaluation_axis": self.evaluation_axis.to_dict(),
            "tolerance": self.tolerance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSpecification":
        sg = data.get("section_gate")
        return cls(
            problem=Problem.from_dict(data.get("problem") or {}),
            current_state=CurrentState.from_dict(data.get("current_state") or {}),
            goal=Goal.from_dict(data.get("goal") or {}),
            difference=Difference.from_dict(data.get("difference") or {}),
            constraints=[ConstraintSpec.from_dict(c) for c in (data.get("constraints") or [])],
            section_gate=SectionGate.from_dict(sg) if sg else None,
            knowledge=KnowledgeState.from_dict(data.get("knowledge") or {}),
            evaluation_axis=EvaluationAxis.from_dict(data.get("evaluation_axis") or {}),
            tolerance=Tolerance.from_dict(data.get("tolerance") or {}),
            created_at=float(data.get("created_at", time.time())),
            schema=str(data.get("schema", "pss.problem_specification/0.3")),
            version=str(data.get("version", "0.3")),
        )

    def summary(self) -> str:
        lines = [
            f"[PSS ProblemSpecification v{self.version}]",
            f"Title       : {self.problem.title}",
            f"Domain      : {self.problem.domain}",
            f"Goal        : {self.goal.description}",
            f"Difference  : {self.difference.description}",
            f"Constraints : {len(self.constraints)}",
        ]
        if self.section_gate:
            status = "COMPLETE" if self.section_gate.is_complete else f"MISSING {self.section_gate.missing_fields}"
            lines.append(f"SectionGate : {status}")
        if self.knowledge.known:
            lines.append(f"Known       : {len(self.knowledge.known)}")
        if self.knowledge.unknown:
            lines.append(f"Unknown     : {self.knowledge.unknown}")
        if self.knowledge.assumption:
            lines.append(f"Assumption  : {self.knowledge.assumption}")
        if self.evaluation_axis.axes:
            axes = ", ".join(f"{k}={v}" for k, v in self.evaluation_axis.axes.items())
            lines.append(f"Eval Axes   : {axes}")
        return "\n".join(lines)
