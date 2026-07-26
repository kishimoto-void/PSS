#!/usr/bin/env python3
"""
PSS Single-File Edition (v0.9)
==============================
コピーしてそのまま実行できる単一ファイル版。

  python pss_single.py

依存: 標準ライブラリのみ
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4
import time
import json


class Phase(str, Enum):
    CLARIFY = "1_clarify"
    CONFIRM = "2_confirm"
    ANSWER = "3_answer"


class Severity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class Identity:
    title: str = ""
    domain: str = ""
    version: str = "0.9"
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "title": self.title, "domain": self.domain,
                "version": self.version, "description": self.description}


@dataclass
class Goal:
    description: str = ""
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.description, "success_criteria": list(self.success_criteria)}


@dataclass
class CurrentState:
    description: str = ""
    facts: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.description, "facts": dict(self.facts)}


@dataclass
class Difference:
    description: str = ""
    gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.description, "gaps": list(self.gaps)}


@dataclass
class Objective:
    goal: Goal = field(default_factory=Goal)
    current_state: CurrentState = field(default_factory=CurrentState)
    difference: Difference = field(default_factory=Difference)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal.to_dict(),
            "current_state": self.current_state.to_dict(),
            "difference": self.difference.to_dict(),
        }


@dataclass
class ConstraintSpec:
    statement: str = ""
    kind: str = "hard"
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {"statement": self.statement, "kind": self.kind, "priority": self.priority}


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


@dataclass
class Scope:
    in_scope: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    priority: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "in_scope": list(self.in_scope),
            "out_of_scope": list(self.out_of_scope),
            "priority": list(self.priority),
        }


@dataclass
class KnowledgeState:
    observation: List[str] = field(default_factory=list)
    inference: List[str] = field(default_factory=list)
    assumption: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation": list(self.observation),
            "inference": list(self.inference),
            "assumption": list(self.assumption),
            "unknown": list(self.unknown),
            "missing": list(self.missing),
        }


@dataclass
class ThinkingProfile:
    reasoning_bias: str = "balanced"
    depth: str = "normal"
    evidence_level: str = "observation_first"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reasoning_bias": self.reasoning_bias,
            "depth": self.depth,
            "evidence_level": self.evidence_level,
        }


@dataclass
class BehaviorRules:
    if_unknown: str = "answer_unknown"
    if_assumption: str = "mark_assumption"
    if_scope_violation: str = "stop"
    if_missing_required: str = "ask"
    if_low_confidence: str = "state_confidence"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "if_unknown": self.if_unknown,
            "if_assumption": self.if_assumption,
            "if_scope_violation": self.if_scope_violation,
            "if_missing_required": self.if_missing_required,
            "if_low_confidence": self.if_low_confidence,
        }


@dataclass
class Behavior:
    role: str = "collaborator"
    role_description: str = ""
    confidence_policy: str = "medium_plus"
    interaction_policy: str = "question_first"
    criticism_level: str = "1_normal"
    rules: BehaviorRules = field(default_factory=BehaviorRules)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "role_description": self.role_description,
            "confidence_policy": self.confidence_policy,
            "interaction_policy": self.interaction_policy,
            "criticism_level": self.criticism_level,
            "rules": self.rules.to_dict(),
        }


@dataclass
class OutputSpec:
    format: str = "markdown"
    style: str = "clear"
    length: str = "medium"
    language: str = "ja"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format,
            "style": self.style,
            "length": self.length,
            "language": self.language,
        }


@dataclass
class EvaluationAxis:
    axes: Dict[str, float] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"axes": dict(self.axes), "notes": self.notes}


@dataclass
class PhaseState:
    phase: str = Phase.CLARIFY.value
    cycle: int = 1
    scope: str = ""
    scope_agreed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "cycle": self.cycle,
            "scope": self.scope,
            "scope_agreed": self.scope_agreed,
        }


@dataclass
class ProblemSpecification:
    identity: Identity = field(default_factory=Identity)
    objective: Objective = field(default_factory=Objective)
    constraints: Constraints = field(default_factory=Constraints)
    scope: Scope = field(default_factory=Scope)
    knowledge: KnowledgeState = field(default_factory=KnowledgeState)
    thinking_profile: ThinkingProfile = field(default_factory=ThinkingProfile)
    behavior: Behavior = field(default_factory=Behavior)
    output: OutputSpec = field(default_factory=OutputSpec)
    evaluation: EvaluationAxis = field(default_factory=EvaluationAxis)
    phase_state: PhaseState = field(default_factory=PhaseState)
    created_at: float = field(default_factory=time.time)
    schema: str = "pss.problem_specification/0.9"
    version: str = "0.9"

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
            "behavior": self.behavior.to_dict(),
            "output": self.output.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "phase_state": self.phase_state.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def summary(self) -> str:
        lines = [
            f"[PSS ProblemSpecification v{self.version}]",
            f"Title       : {self.identity.title}",
            f"Domain      : {self.identity.domain}",
            f"Goal        : {self.objective.goal.description}",
            f"Phase       : {self.phase_state.phase} (cycle {self.phase_state.cycle})",
            f"Role        : {self.behavior.role}",
            f"Criticism   : {self.behavior.criticism_level}",
            f"if_unknown  : {self.behavior.rules.if_unknown}",
            f"Evidence    : {self.thinking_profile.evidence_level}",
        ]
        if self.knowledge.observation:
            lines.append(f"Observation : {len(self.knowledge.observation)}")
        if self.knowledge.unknown or self.knowledge.missing:
            lines.append(f"Unknown/Missing : {self.knowledge.unknown + self.knowledge.missing}")
        return "\n".join(lines)


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

    def identity(self, title: str = "", domain: str = "", description: str = "") -> "ProblemBuilder":
        if title: self._identity.title = title
        if domain: self._identity.domain = domain
        if description: self._identity.description = description
        return self

    def goal(self, description: str = "", success_criteria: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        self._objective.goal = Goal(description=description, success_criteria=list(success_criteria or []))
        return self

    def current_state(self, description: str = "") -> "ProblemBuilder":
        self._objective.current_state = CurrentState(description=description)
        return self

    def difference(self, description: str = "", gaps: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        self._objective.difference = Difference(description=description, gaps=list(gaps or []))
        return self

    def add_constraint(self, statement: str, kind: str = "hard", priority: int = 0) -> "ProblemBuilder":
        c = ConstraintSpec(statement=statement, kind=kind, priority=priority)
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

    def scope(self, in_scope: Optional[Sequence[str]] = None, out_of_scope: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        if in_scope is not None: self._scope.in_scope = list(in_scope)
        if out_of_scope is not None: self._scope.out_of_scope = list(out_of_scope)
        return self

    def knowledge(self, observation: Optional[Sequence[str]] = None, inference: Optional[Sequence[str]] = None, assumption: Optional[Sequence[str]] = None, unknown: Optional[Sequence[str]] = None, missing: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        if observation is not None: self._knowledge.observation = list(observation)
        if inference is not None: self._knowledge.inference = list(inference)
        if assumption is not None: self._knowledge.assumption = list(assumption)
        if unknown is not None: self._knowledge.unknown = list(unknown)
        if missing is not None: self._knowledge.missing = list(missing)
        return self

    def thinking_profile(self, reasoning_bias: str = "balanced", depth: str = "normal", evidence_level: str = "observation_first") -> "ProblemBuilder":
        self._thinking = ThinkingProfile(reasoning_bias=reasoning_bias, depth=depth, evidence_level=evidence_level)
        return self

    def behavior(self, role: str = "collaborator", role_description: str = "", criticism_level: str = "1_normal", if_unknown: str = "answer_unknown", if_assumption: str = "mark_assumption", if_scope_violation: str = "stop", if_missing_required: str = "ask", if_low_confidence: str = "state_confidence") -> "ProblemBuilder":
        self._behavior = Behavior(
            role=role, role_description=role_description, criticism_level=criticism_level,
            rules=BehaviorRules(if_unknown=if_unknown, if_assumption=if_assumption, if_scope_violation=if_scope_violation, if_missing_required=if_missing_required, if_low_confidence=if_low_confidence),
        )
        return self

    def output(self, format: str = "markdown", language: str = "ja") -> "ProblemBuilder":
        self._output = OutputSpec(format=format, language=language)
        return self

    def evaluation_axis(self, axes: Dict[str, float], notes: str = "") -> "ProblemBuilder":
        self._evaluation = EvaluationAxis(axes=dict(axes), notes=notes)
        return self

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
        )
        for m in knowledge.missing:
            if m not in knowledge.unknown:
                knowledge.unknown.append(m)
        return ProblemSpecification(
            identity=self._identity, objective=self._objective, constraints=self._constraints,
            scope=self._scope, knowledge=knowledge, thinking_profile=self._thinking,
            behavior=self._behavior, output=self._output, evaluation=self._evaluation,
            phase_state=self._phase,
        )


@dataclass
class Finding:
    code: str
    severity: Severity
    message: str
    suggestion: str = ""


@dataclass
class ValidationReport:
    overall: Severity = Severity.PASS
    findings: List[Finding] = field(default_factory=list)

    def add(self, f: Finding) -> None:
        self.findings.append(f)
        if f.severity == Severity.ERROR:
            self.overall = Severity.ERROR
        elif f.severity == Severity.WARN and self.overall != Severity.ERROR:
            self.overall = Severity.WARN

    def summary(self) -> str:
        lines = [f"[Validation] Overall: {self.overall.value}"]
        for f in self.findings:
            lines.append(f"  [{f.severity.value}] {f.code}: {f.message}")
            if f.suggestion:
                lines.append(f"       → {f.suggestion}")
        if not self.findings:
            lines.append("  No issues.")
        return "\n".join(lines)


def validate(spec: ProblemSpecification) -> ValidationReport:
    report = ValidationReport()
    if not spec.identity.title.strip():
        report.add(Finding("IDENTITY_TITLE_MISSING", Severity.ERROR, "title が空です", "タイトルを設定してください"))
    if not spec.objective.goal.description.strip():
        report.add(Finding("OBJECTIVE_GOAL_MISSING", Severity.ERROR, "Goal が空です", "到達したい状態を書いてください"))
    if not spec.scope.in_scope and not spec.scope.out_of_scope:
        report.add(Finding("SCOPE_EMPTY", Severity.WARN, "Scope が未定義です", "in_scope / out_of_scope を設定してください"))
    if spec.knowledge.inference and not spec.knowledge.observation:
        report.add(Finding("KNOWLEDGE_INFERENCE_WITHOUT_OBSERVATION", Severity.WARN, "inference があるが observation が空です", "観測事実を追加するか、inference を assumption に移してください"))
    if spec.behavior.role == "custom" and not spec.behavior.role_description:
        report.add(Finding("BEHAVIOR_ROLE_DESC_MISSING", Severity.WARN, "role=custom なのに説明が空です", "role_description を書いてください"))
    if not spec.constraints.all():
        report.add(Finding("CONSTRAINT_EMPTY", Severity.WARN, "Constraints が空です", "safety constraint の追加を推奨"))
    return report


def render_specification(spec: ProblemSpecification) -> str:
    lines = [
        "=" * 50,
        "PROBLEM SPECIFICATION (Thinking Conditions)",
        f"schema : {spec.schema}",
        "=" * 50, "",
        f"Title  : {spec.identity.title}",
        f"Domain : {spec.identity.domain}",
        f"Goal   : {spec.objective.goal.description or '(none)'}",
        f"Phase  : {spec.phase_state.phase}", "",
        "--- Behavior Rules ---",
        f"  role              : {spec.behavior.role}",
        f"  if_unknown        : {spec.behavior.rules.if_unknown}",
        f"  if_assumption     : {spec.behavior.rules.if_assumption}",
        f"  if_scope_violation: {spec.behavior.rules.if_scope_violation}", "",
        "--- Knowledge ---",
    ]
    if spec.knowledge.observation:
        lines.append("Observation:")
        for x in spec.knowledge.observation:
            lines.append(f"  - {x}")
    if spec.knowledge.unknown or spec.knowledge.missing:
        lines.append("Unknown/Missing:")
        for x in spec.knowledge.unknown + spec.knowledge.missing:
            lines.append(f"  - {x}")
    if spec.knowledge.assumption:
        lines.append("Assumption:")
        for x in spec.knowledge.assumption:
            lines.append(f"  - {x}")
    lines.append("=" * 50)
    return "\n".join(lines)


def compile_for_generic(spec: ProblemSpecification) -> str:
    header = """あなたは PSS の思考条件仕様書を受け取ります。
Behavior の行動規則を必ず守ってください。
Observation と Inference / Assumption を区別し、Unknown は勝手に埋めないでください。
Phase に従って行動してください（Clarify なら質問のみ）。
"""
    return header + "\n" + render_specification(spec)


def main() -> None:
    print("=" * 60)
    print("PSS Single-File Demo (v0.9)")
    print("=" * 60)

    spec = (
        ProblemBuilder()
        .identity(title="進捗報告資料の作成", domain="business.document")
        .goal(description="会議で使える完成度の高い資料を提出する", success_criteria=["内容が明確", "次アクションがある"])
        .current_state(description="メモ書きしかない")
        .knowledge(
            observation=["会議は来週火曜 10:00", "Wordで提出"],
            unknown=["正式な出力フォーマット"],
            assumption=["Wordは利用可能"],
        )
        .add_default_safety_constraints()
        .behavior(role="collaborator", if_unknown="answer_unknown", if_assumption="mark_assumption")
        .phase(phase="1_clarify")
        .build()
    )

    print("\n[1] Summary")
    print(spec.summary())
    print("\n[2] Validate")
    print(validate(spec).summary())
    print("\n[3] JSON (truncated)")
    print(spec.to_json()[:400] + "\n...")
    print("\n[4] Adapter output (truncated)")
    print(compile_for_generic(spec)[:500] + "\n...")

    print("\n" + "=" * 60)
    print("Incomplete spec (for Validator demo)")
    print("=" * 60)
    bad = (
        ProblemBuilder()
        .identity(title="", domain="test")
        .goal(description="")
        .knowledge(inference=["おそらく前回と同じ"])
        .behavior(role="custom")
        .build()
    )
    print(validate(bad).summary())


if __name__ == "__main__":
    main()
