"""
PSS Core Data Structures (v0.5)
===============================
Problem Specification System — 思考条件を定義する共通仕様。

設計思想:
  PSS は「LLMを制御する仕様」ではなく、「思考条件を定義する仕様」である。
  人間 / Agent / LLM が同じ思考条件を共有できるようにする。

v0.5 の主な変更:
  - Identity / Objective / Constraints / Scope / Knowledge / Evaluation / Phase をコアとして強化
  - Thinking Profile / Agent Role / Output を正式追加
  - Audience / Confidence Policy / Interaction Policy / Criticism Level を拡張オプションとして用意
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4
import time


# =============================================================================
# Enums for controlled vocabularies
# =============================================================================

class ReasoningBias(str, Enum):
    BALANCED = "balanced"
    MATHEMATICAL = "mathematical"
    PHYSICAL = "physical"
    PHILOSOPHICAL = "philosophical"
    PSYCHOLOGICAL = "psychological"
    ENGINEERING = "engineering"
    SCIENTIFIC = "scientific"
    SYSTEMS = "systems"
    CREATIVE = "creative"
    CUSTOM = "custom"


class Depth(str, Enum):
    QUICK = "quick"
    NORMAL = "normal"
    DEEP = "deep"


class EvidencePolicy(str, Enum):
    OBSERVATION_FIRST = "observation_first"
    ALLOW_ASSUMPTION = "allow_assumption"
    STRICT_EVIDENCE = "strict_evidence"


class AgentRole(str, Enum):
    COLLABORATOR = "collaborator"   # 壁打ち
    REVIEWER = "reviewer"           # 評価
    CHALLENGER = "challenger"       # 反証
    SUPPORTER = "supporter"         # 支援
    TEACHER = "teacher"             # 教育
    ANALYST = "analyst"             # 分析
    MEDIATOR = "mediator"           # 中立整理
    CUSTOM = "custom"


class Audience(str, Enum):
    EXPERT = "expert"
    GENERAL_USER = "general_user"
    DEVELOPER = "developer"
    MANAGEMENT = "management"
    STUDENT = "student"
    CUSTOMER = "customer"
    CUSTOM = "custom"


class ConfidencePolicy(str, Enum):
    HIGH_ONLY = "high_only"
    MEDIUM_PLUS = "medium_plus"
    ALWAYS_ANSWER = "always_answer"
    UNKNOWN_PREFERRED = "unknown_preferred"


class InteractionPolicy(str, Enum):
    QUESTION_FIRST = "question_first"
    PROPOSAL_FIRST = "proposal_first"
    SUMMARY_FIRST = "summary_first"
    COMPARISON_FIRST = "comparison_first"
    CUSTOM = "custom"


class CriticismLevel(str, Enum):
    FRIENDLY = "0_friendly"
    NORMAL = "1_normal"
    STRICT_REVIEW = "2_strict_review"
    DEVILS_ADVOCATE = "3_devils_advocate"


class ConstraintKind(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    ASSUMPTION = "assumption"
    RISK = "risk"


# =============================================================================
# 1. Identity
# =============================================================================

@dataclass
class Identity:
    title: str = ""
    domain: str = ""
    version: str = "0.5"
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "domain": self.domain,
            "version": self.version,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Identity":
        return cls(
            id=str(data.get("id", str(uuid4()))),
            title=str(data.get("title", "")),
            domain=str(data.get("domain", "")),
            version=str(data.get("version", "0.5")),
            description=str(data.get("description", "")),
        )


# =============================================================================
# 2. Objective
# =============================================================================

@dataclass
class CurrentState:
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
class Objective:
    goal: Goal = field(default_factory=Goal)
    current_state: CurrentState = field(default_factory=CurrentState)
    difference: Difference = field(default_factory=Difference)
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal.to_dict(),
            "current_state": self.current_state.to_dict(),
            "difference": self.difference.to_dict(),
            "success_criteria": list(self.success_criteria or self.goal.success_criteria),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Objective":
        return cls(
            goal=Goal.from_dict(data.get("goal") or {}),
            current_state=CurrentState.from_dict(data.get("current_state") or {}),
            difference=Difference.from_dict(data.get("difference") or {}),
            success_criteria=list(data.get("success_criteria") or []),
        )


# =============================================================================
# 3. Constraints
# =============================================================================

@dataclass
class ConstraintSpec:
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
class Constraints:
    hard: List[ConstraintSpec] = field(default_factory=list)
    soft: List[ConstraintSpec] = field(default_factory=list)
    assumptions: List[ConstraintSpec] = field(default_factory=list)
    risks: List[ConstraintSpec] = field(default_factory=list)

    def all(self) -> List[ConstraintSpec]:
        return self.hard + self.soft + self.assumptions + self.risks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hard": [c.to_dict() for c in self.hard],
            "soft": [c.to_dict() for c in self.soft],
            "assumptions": [c.to_dict() for c in self.assumptions],
            "risks": [c.to_dict() for c in self.risks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Constraints":
        return cls(
            hard=[ConstraintSpec.from_dict(c) for c in (data.get("hard") or [])],
            soft=[ConstraintSpec.from_dict(c) for c in (data.get("soft") or [])],
            assumptions=[ConstraintSpec.from_dict(c) for c in (data.get("assumptions") or [])],
            risks=[ConstraintSpec.from_dict(c) for c in (data.get("risks") or [])],
        )


# =============================================================================
# 4. Scope
# =============================================================================

@dataclass
class Scope:
    in_scope: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    priority: List[str] = field(default_factory=list)
    allowed_changes: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "in_scope": list(self.in_scope),
            "out_of_scope": list(self.out_of_scope),
            "priority": list(self.priority),
            "allowed_changes": list(self.allowed_changes),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scope":
        return cls(
            in_scope=list(data.get("in_scope") or []),
            out_of_scope=list(data.get("out_of_scope") or []),
            priority=list(data.get("priority") or []),
            allowed_changes=list(data.get("allowed_changes") or []),
            notes=str(data.get("notes", "")),
        )


# =============================================================================
# 5. Knowledge
# =============================================================================

@dataclass
class KnowledgeState:
    known: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    assumption: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "known": list(self.known),
            "unknown": list(self.unknown),
            "missing": list(self.missing),
            "assumption": list(self.assumption),
            "references": list(self.references),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeState":
        return cls(
            known=list(data.get("known") or []),
            unknown=list(data.get("unknown") or []),
            missing=list(data.get("missing") or []),
            assumption=list(data.get("assumption") or []),
            references=list(data.get("references") or []),
        )


# =============================================================================
# 6. Thinking Profile (formal)
# =============================================================================

@dataclass
class ThinkingProfile:
    reasoning_bias: str = ReasoningBias.BALANCED.value
    depth: str = Depth.NORMAL.value
    evidence_policy: str = EvidencePolicy.OBSERVATION_FIRST.value
    custom_bias_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning_bias": self.reasoning_bias,
            "depth": self.depth,
            "evidence_policy": self.evidence_policy,
            "custom_bias_note": self.custom_bias_note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThinkingProfile":
        return cls(
            reasoning_bias=str(data.get("reasoning_bias", ReasoningBias.BALANCED.value)),
            depth=str(data.get("depth", Depth.NORMAL.value)),
            evidence_policy=str(data.get("evidence_policy", EvidencePolicy.OBSERVATION_FIRST.value)),
            custom_bias_note=str(data.get("custom_bias_note", "")),
        )


# =============================================================================
# 7. Agent Role (formal)
# =============================================================================

@dataclass
class AgentRoleSpec:
    role: str = AgentRole.COLLABORATOR.value
    custom_description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "custom_description": self.custom_description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRoleSpec":
        return cls(
            role=str(data.get("role", AgentRole.COLLABORATOR.value)),
            custom_description=str(data.get("custom_description", "")),
        )


# =============================================================================
# 8. Output
# =============================================================================

@dataclass
class OutputSpec:
    format: str = "markdown"
    style: str = "clear"
    length: str = "medium"
    language: str = "ja"
    required_sections: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format,
            "style": self.style,
            "length": self.length,
            "language": self.language,
            "required_sections": list(self.required_sections),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OutputSpec":
        return cls(
            format=str(data.get("format", "markdown")),
            style=str(data.get("style", "clear")),
            length=str(data.get("length", "medium")),
            language=str(data.get("language", "ja")),
            required_sections=list(data.get("required_sections") or []),
        )


# =============================================================================
# 9. Evaluation
# =============================================================================

@dataclass
class EvaluationAxis:
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


# =============================================================================
# Extension Options
# =============================================================================

@dataclass
class ExtensionOptions:
    audience: str = Audience.GENERAL_USER.value
    confidence_policy: str = ConfidencePolicy.MEDIUM_PLUS.value
    interaction_policy: str = InteractionPolicy.QUESTION_FIRST.value
    criticism_level: str = CriticismLevel.NORMAL.value
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audience": self.audience,
            "confidence_policy": self.confidence_policy,
            "interaction_policy": self.interaction_policy,
            "criticism_level": self.criticism_level,
            "custom": dict(self.custom),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtensionOptions":
        return cls(
            audience=str(data.get("audience", Audience.GENERAL_USER.value)),
            confidence_policy=str(data.get("confidence_policy", ConfidencePolicy.MEDIUM_PLUS.value)),
            interaction_policy=str(data.get("interaction_policy", InteractionPolicy.QUESTION_FIRST.value)),
            criticism_level=str(data.get("criticism_level", CriticismLevel.NORMAL.value)),
            custom=dict(data.get("custom") or {}),
        )


# =============================================================================
# Aggregate: ProblemSpecification (v0.5)
# =============================================================================

@dataclass
class ProblemSpecification:
    """
    PSS v0.5 が最終的に生成する「思考条件仕様書」。
    """
    identity: Identity = field(default_factory=Identity)
    objective: Objective = field(default_factory=Objective)
    constraints: Constraints = field(default_factory=Constraints)
    scope: Scope = field(default_factory=Scope)
    knowledge: KnowledgeState = field(default_factory=KnowledgeState)
    thinking_profile: ThinkingProfile = field(default_factory=ThinkingProfile)
    agent_role: AgentRoleSpec = field(default_factory=AgentRoleSpec)
    output: OutputSpec = field(default_factory=OutputSpec)
    evaluation: EvaluationAxis = field(default_factory=EvaluationAxis)
    extensions: ExtensionOptions = field(default_factory=ExtensionOptions)

    created_at: float = field(default_factory=time.time)
    schema: str = "pss.problem_specification/0.5"
    version: str = "0.5"

    @property
    def problem(self) -> Identity:
        return self.identity

    @property
    def goal(self) -> Goal:
        return self.objective.goal

    @property
    def current_state(self) -> CurrentState:
        return self.objective.current_state

    @property
    def difference(self) -> Difference:
        return self.objective.difference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "created_at": self.created_at,
            "identity": self.identity.to_dict(),
            "objective": self.objective.to_dict(),
            "constraints": self.constraints.to_dict(),
            "scope": self.scope.to_dict(),
            "knowledge": self.knowledge.to_dict(),
            "thinking_profile": self.thinking_profile.to_dict(),
            "agent_role": self.agent_role.to_dict(),
            "output": self.output.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "extensions": self.extensions.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProblemSpecification":
        if "identity" in data or "objective" in data:
            return cls(
                identity=Identity.from_dict(data.get("identity") or {}),
                objective=Objective.from_dict(data.get("objective") or {}),
                constraints=Constraints.from_dict(data.get("constraints") or {}),
                scope=Scope.from_dict(data.get("scope") or {}),
                knowledge=KnowledgeState.from_dict(data.get("knowledge") or {}),
                thinking_profile=ThinkingProfile.from_dict(data.get("thinking_profile") or {}),
                agent_role=AgentRoleSpec.from_dict(data.get("agent_role") or {}),
                output=OutputSpec.from_dict(data.get("output") or {}),
                evaluation=EvaluationAxis.from_dict(data.get("evaluation") or data.get("evaluation_axis") or {}),
                extensions=ExtensionOptions.from_dict(data.get("extensions") or {}),
                created_at=float(data.get("created_at", time.time())),
                schema=str(data.get("schema", "pss.problem_specification/0.5")),
                version=str(data.get("version", "0.5")),
            )
        return cls(
            identity=Identity(
                title=str((data.get("problem") or {}).get("title", "")),
                domain=str((data.get("problem") or {}).get("domain", "")),
                description=str((data.get("problem") or {}).get("description", "")),
            ),
            knowledge=KnowledgeState.from_dict(data.get("knowledge") or {}),
            evaluation=EvaluationAxis.from_dict(data.get("evaluation_axis") or {}),
            created_at=float(data.get("created_at", time.time())),
            schema=str(data.get("schema", "pss.problem_specification/0.5")),
            version=str(data.get("version", "0.5")),
        )

    def summary(self) -> str:
        lines = [
            f"[PSS ProblemSpecification v{self.version}]",
            f"Title       : {self.identity.title}",
            f"Domain      : {self.identity.domain}",
            f"Goal        : {self.objective.goal.description}",
            f"Difference  : {self.objective.difference.description}",
            f"Constraints : hard={len(self.constraints.hard)} soft={len(self.constraints.soft)} "
            f"assumptions={len(self.constraints.assumptions)} risks={len(self.constraints.risks)}",
            f"Role        : {self.agent_role.role}",
            f"Thinking    : bias={self.thinking_profile.reasoning_bias} depth={self.thinking_profile.depth}",
            f"Audience    : {self.extensions.audience}",
            f"Confidence  : {self.extensions.confidence_policy}",
        ]
        if self.knowledge.known:
            lines.append(f"Known       : {len(self.knowledge.known)}")
        if self.knowledge.unknown or self.knowledge.missing:
            lines.append(f"Unknown/Missing : {self.knowledge.unknown + self.knowledge.missing}")
        if self.knowledge.assumption:
            lines.append(f"Assumption  : {self.knowledge.assumption}")
        if self.evaluation.axes:
            axes = ", ".join(f"{k}={v}" for k, v in self.evaluation.axes.items())
            lines.append(f"Eval Axes   : {axes}")
        return "\n".join(lines)
