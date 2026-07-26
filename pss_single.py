#!/usr/bin/env python3
"""
PSS Single-File Edition (v1.0.0-rc1 conceptual freeze)
=========================================================
Problem Specification System — 問題仕様書（実行エンジンではない）

【v1.0 で固定する4点】
  1. Mission とは「何を達成するか」
  2. PredictionPolicy とは「どこまで予測してよいか」
  3. Gate は判定だけを行い、仕様を変更しない
  4. PSS は問題仕様書であり、実行エンジンではない

【層構造】
  必須（コア）
    Mission / ThinkingProfile / PredictionPolicy / EvaluationCriteria

  運用層
    Phase / SectionGate / Behavior / Validator

  外部層（このファイルでは最小のみ）
    Adapter（render / compile）
    ※ Executor / Fix Planner / LLM連携はコア外

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


# =============================================================================
# Enums
# =============================================================================

class Phase(str, Enum):
    CLARIFY = "1_clarify"
    CONFIRM = "2_confirm"
    ANSWER = "3_answer"


class Severity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    ERROR = "ERROR"


class Priority(str, Enum):
    """Mission / SubMission の重要度。情報が足りないときの省略判断に使う。"""
    CRITICAL = "critical"  # 必須・省略不可
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"            # 省略可


class ThinkingStance(str, Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CAUTIOUS = "cautious"
    SPEED = "speed"
    BALANCED = "balanced"


class Perspective(str, Enum):
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    IMPLEMENTER = "implementer"
    EDUCATOR = "educator"
    ADVISOR = "advisor"
    CUSTOM = "custom"


class EvidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class SubMissionKind(str, Enum):
    GATHER_INFO = "gather_info"
    RISK_SCAN = "risk_scan"
    ALTERNATIVES = "alternatives"
    ASK_MISSING = "ask_missing"
    CUSTOM = "custom"


# Gate 理由コード（機械可読。自由文は blocking に残してもよいが code を優先）
class GateCode(str, Enum):
    OK = "GATE_OK"
    MISSION_GOAL_EMPTY = "GATE_MISSION_GOAL_EMPTY"
    ASK_MISSING_PENDING = "GATE_ASK_MISSING_PENDING"
    KNOWLEDGE_EMPTY = "GATE_KNOWLEDGE_EMPTY"
    SCOPE_NOT_AGREED = "GATE_SCOPE_NOT_AGREED"
    SCOPE_UNDEFINED = "GATE_SCOPE_UNDEFINED"


# =============================================================================
# コア1: Mission
# =============================================================================

@dataclass
class MainMission:
    goal: str = ""
    success_criteria: List[str] = field(default_factory=list)
    priority: str = Priority.CRITICAL.value  # Main は通常 critical

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "success_criteria": list(self.success_criteria),
            "priority": self.priority,
        }


@dataclass
class SubMission:
    kind: str = SubMissionKind.CUSTOM.value
    description: str = ""
    done: bool = False
    priority: str = Priority.NORMAL.value  # high / normal / low など

    def is_optional(self) -> bool:
        return self.priority in (Priority.LOW.value, Priority.NORMAL.value)

    def is_required(self) -> bool:
        return self.priority in (Priority.CRITICAL.value, Priority.HIGH.value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "description": self.description,
            "done": self.done,
            "priority": self.priority,
        }


@dataclass
class Mission:
    main: MainMission = field(default_factory=MainMission)
    subs: List[SubMission] = field(default_factory=list)

    def required_subs(self) -> List[SubMission]:
        return [s for s in self.subs if s.is_required()]

    def optional_subs(self) -> List[SubMission]:
        return [s for s in self.subs if s.is_optional()]

    def to_dict(self) -> Dict[str, Any]:
        return {"main": self.main.to_dict(), "subs": [s.to_dict() for s in self.subs]}


# =============================================================================
# Knowledge / Constraints / Scope
# =============================================================================

@dataclass
class KnowledgeState:
    observation: List[str] = field(default_factory=list)
    inference: List[str] = field(default_factory=list)
    assumption: List[str] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    def evidence_count(self) -> int:
        return len(self.observation)

    def estimated_evidence_level(self) -> str:
        n = self.evidence_count()
        if n >= 5:
            return EvidenceLevel.HIGH.value
        if n >= 2:
            return EvidenceLevel.MEDIUM.value
        if n >= 1:
            return EvidenceLevel.LOW.value
        return EvidenceLevel.NONE.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation": list(self.observation),
            "inference": list(self.inference),
            "assumption": list(self.assumption),
            "unknown": list(self.unknown),
            "missing": list(self.missing),
            "evidence_count": self.evidence_count(),
            "estimated_evidence_level": self.estimated_evidence_level(),
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

    def to_dict(self) -> Dict[str, Any]:
        return {"in_scope": list(self.in_scope), "out_of_scope": list(self.out_of_scope)}


# =============================================================================
# コア2: ThinkingProfile
# =============================================================================

@dataclass
class ThinkingProfile:
    stance: str = ThinkingStance.BALANCED.value
    perspective: str = Perspective.ADVISOR.value
    depth: str = "normal"
    reasoning_bias: str = "balanced"
    evidence_level: str = "observation_first"
    perspective_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stance": self.stance,
            "perspective": self.perspective,
            "depth": self.depth,
            "reasoning_bias": self.reasoning_bias,
            "evidence_level": self.evidence_level,
            "perspective_note": self.perspective_note,
        }


# =============================================================================
# 運用: Behavior
# =============================================================================

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
    criticism_level: str = "1_normal"
    rules: BehaviorRules = field(default_factory=BehaviorRules)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "role_description": self.role_description,
            "criticism_level": self.criticism_level,
            "rules": self.rules.to_dict(),
        }


# =============================================================================
# コア3: PredictionPolicy
# =============================================================================

@dataclass
class PredictionPolicy:
    allow_prediction: bool = True
    minimum_evidence: str = EvidenceLevel.MEDIUM.value
    when_uncertain: str = "state_unknown"
    show_confidence: bool = True
    explain_reason: bool = True
    refuse_if_below_minimum: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allow_prediction": self.allow_prediction,
            "minimum_evidence": self.minimum_evidence,
            "when_uncertain": self.when_uncertain,
            "show_confidence": self.show_confidence,
            "explain_reason": self.explain_reason,
            "refuse_if_below_minimum": self.refuse_if_below_minimum,
        }

    def allows_with(self, evidence_level: str) -> bool:
        if not self.allow_prediction:
            return False
        order = {"none": 0, "low": 1, "medium": 2, "high": 3}
        return order.get(evidence_level, 0) >= order.get(self.minimum_evidence, 2)


@dataclass
class PredictionQuality:
    confidence: str = "unknown"
    uncertainty: str = "unknown"
    evidence_count: int = 0
    evidence_level: str = EvidenceLevel.NONE.value
    reason: str = ""
    is_prediction_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "evidence_count": self.evidence_count,
            "evidence_level": self.evidence_level,
            "reason": self.reason,
            "is_prediction_allowed": self.is_prediction_allowed,
        }


# =============================================================================
# コア4: EvaluationCriteria
# =============================================================================

@dataclass
class EvaluationCriterion:
    name: str
    weight: float = 0.25
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "weight": self.weight, "notes": self.notes}


@dataclass
class EvaluationCriteria:
    criteria: List[EvaluationCriterion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"criteria": [c.to_dict() for c in self.criteria]}

    def normalized(self) -> List[EvaluationCriterion]:
        total = sum(c.weight for c in self.criteria) or 1.0
        return [
            EvaluationCriterion(name=c.name, weight=round(c.weight / total, 4), notes=c.notes)
            for c in self.criteria
        ]


# 後方互換
Evaluation = EvaluationCriteria


# =============================================================================
# 運用: SectionGate（判定のみ・仕様を変更しない）
# =============================================================================

@dataclass
class GateResult:
    phase: str
    can_proceed: bool
    codes: List[str] = field(default_factory=list)   # GateCode 値
    reasons: List[str] = field(default_factory=list) # 人間向け説明
    blocking: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "can_proceed": self.can_proceed,
            "codes": list(self.codes),
            "reasons": list(self.reasons),
            "blocking": list(self.blocking),
        }


@dataclass
class PhaseState:
    phase: str = Phase.CLARIFY.value
    cycle: int = 1
    scope: str = ""
    scope_agreed: bool = False
    last_gate: Optional[GateResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "cycle": self.cycle,
            "scope": self.scope,
            "scope_agreed": self.scope_agreed,
            "last_gate": self.last_gate.to_dict() if self.last_gate else None,
        }


def evaluate_gate(spec: "ProblemSpecification") -> GateResult:
    """Gate は判定のみ。仕様を mutate しない。"""
    phase = spec.phase_state.phase
    codes: List[str] = []
    reasons: List[str] = []
    blocking: List[str] = []

    if phase == Phase.CLARIFY.value:
        if not spec.mission.main.goal.strip():
            codes.append(GateCode.MISSION_GOAL_EMPTY.value)
            blocking.append("Main Mission の goal が空")
        if not spec.knowledge.observation and not spec.knowledge.unknown:
            codes.append(GateCode.KNOWLEDGE_EMPTY.value)
            blocking.append("observation も unknown も無い")
        # required な ask_missing のみブロック対象（optional は省略可）
        pending = [
            s for s in spec.mission.subs
            if s.kind == SubMissionKind.ASK_MISSING.value
            and not s.done
            and s.is_required()
            and spec.knowledge.missing
        ]
        if pending:
            codes.append(GateCode.ASK_MISSING_PENDING.value)
            blocking.append(
                "必須の不足情報質問が未完了: "
                + str([s.description or s.kind for s in pending])
            )
        if not blocking:
            codes.append(GateCode.OK.value)
            reasons.append("Main Mission と最低限の Knowledge が揃っている")
        return GateResult(
            phase=phase, can_proceed=len(blocking) == 0,
            codes=codes, reasons=reasons, blocking=blocking,
        )

    if phase == Phase.CONFIRM.value:
        if not spec.phase_state.scope_agreed:
            codes.append(GateCode.SCOPE_NOT_AGREED.value)
            blocking.append("scope_agreed が False")
        if not spec.phase_state.scope.strip() and not (spec.scope.in_scope or spec.scope.out_of_scope):
            codes.append(GateCode.SCOPE_UNDEFINED.value)
            blocking.append("確認すべき scope が未定義")
        if not blocking:
            codes.append(GateCode.OK.value)
            reasons.append("scope_agreed=True で確認済み")
        return GateResult(
            phase=phase, can_proceed=len(blocking) == 0,
            codes=codes, reasons=reasons, blocking=blocking,
        )

    codes.append(GateCode.OK.value)
    reasons.append("Answer フェーズ（完了判定は呼び出し側）")
    return GateResult(phase=phase, can_proceed=True, codes=codes, reasons=reasons, blocking=blocking)


# =============================================================================
# Aggregate
# =============================================================================

@dataclass
class Identity:
    title: str = ""
    domain: str = ""
    version: str = "1.0.0-rc1"
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "domain": self.domain,
            "version": self.version, "description": self.description,
        }


@dataclass
class OutputSpec:
    format: str = "markdown"
    language: str = "ja"
    include_pros_cons: bool = False
    include_confidence: bool = True
    include_needed_info: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format, "language": self.language,
            "include_pros_cons": self.include_pros_cons,
            "include_confidence": self.include_confidence,
            "include_needed_info": self.include_needed_info,
        }


@dataclass
class ProblemSpecification:
    identity: Identity = field(default_factory=Identity)
    # --- コア4本柱 ---
    mission: Mission = field(default_factory=Mission)
    thinking_profile: ThinkingProfile = field(default_factory=ThinkingProfile)
    prediction_policy: PredictionPolicy = field(default_factory=PredictionPolicy)
    evaluation: EvaluationCriteria = field(default_factory=EvaluationCriteria)
    # --- 運用層 ---
    knowledge: KnowledgeState = field(default_factory=KnowledgeState)
    constraints: Constraints = field(default_factory=Constraints)
    scope: Scope = field(default_factory=Scope)
    behavior: Behavior = field(default_factory=Behavior)
    phase_state: PhaseState = field(default_factory=PhaseState)
    output: OutputSpec = field(default_factory=OutputSpec)
    created_at: float = field(default_factory=time.time)
    schema: str = "pss.problem_specification/1.0"
    version: str = "1.0.0-rc1"

    def assess_prediction_quality(self) -> PredictionQuality:
        level = self.knowledge.estimated_evidence_level()
        count = self.knowledge.evidence_count()
        allowed = self.prediction_policy.allows_with(level)
        conf_map = {"high": "high", "medium": "medium", "low": "low", "none": "unknown"}
        unc_map = {"high": "low", "medium": "medium", "low": "high", "none": "high"}
        if not self.prediction_policy.allow_prediction:
            reason = "予測がポリシーで禁止されている"
        elif not allowed:
            reason = f"根拠レベル {level} が minimum_evidence={self.prediction_policy.minimum_evidence} 未満"
        else:
            reason = f"observation={count} 件に基づく予測が許容される"
        return PredictionQuality(
            confidence=conf_map.get(level, "unknown"),
            uncertainty=unc_map.get(level, "unknown"),
            evidence_count=count,
            evidence_level=level,
            reason=reason,
            is_prediction_allowed=allowed,
        )

    def run_gate(self) -> GateResult:
        result = evaluate_gate(self)
        self.phase_state.last_gate = result
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "version": self.version,
            "created_at": self.created_at,
            "identity": self.identity.to_dict(),
            "mission": self.mission.to_dict(),
            "thinking_profile": self.thinking_profile.to_dict(),
            "prediction_policy": self.prediction_policy.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "knowledge": self.knowledge.to_dict(),
            "constraints": self.constraints.to_dict(),
            "scope": self.scope.to_dict(),
            "behavior": self.behavior.to_dict(),
            "phase_state": self.phase_state.to_dict(),
            "output": self.output.to_dict(),
            "prediction_quality": self.assess_prediction_quality().to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def summary(self) -> str:
        pq = self.assess_prediction_quality()
        gate = self.phase_state.last_gate
        lines = [
            f"[PSS ProblemSpecification v{self.version}]",
            f"Title       : {self.identity.title}",
            f"Main Mission: {self.mission.main.goal} [{self.mission.main.priority}]",
            f"SubMissions : req={len(self.mission.required_subs())} opt={len(self.mission.optional_subs())}",
            f"Phase       : {self.phase_state.phase}",
            f"Stance/Persp: {self.thinking_profile.stance} / {self.thinking_profile.perspective}",
            f"Pred allow  : {pq.is_prediction_allowed} ({pq.evidence_level}, n={pq.evidence_count})",
        ]
        if self.evaluation.criteria:
            crit = ", ".join(f"{c.name}={c.weight:.2f}" for c in self.evaluation.normalized())
            lines.append(f"Eval        : {crit}")
        if gate is not None:
            lines.append(f"Gate        : proceed={gate.can_proceed} codes={gate.codes}")
        return "\n".join(lines)


# =============================================================================
# Builder
# =============================================================================

class ProblemBuilder:
    def __init__(self) -> None:
        self._identity = Identity()
        self._mission = Mission()
        self._thinking = ThinkingProfile()
        self._prediction = PredictionPolicy()
        self._evaluation = EvaluationCriteria()
        self._knowledge = KnowledgeState()
        self._constraints = Constraints()
        self._scope = Scope()
        self._behavior = Behavior()
        self._phase = PhaseState()
        self._output = OutputSpec()

    def identity(self, title: str = "", domain: str = "", description: str = "") -> "ProblemBuilder":
        if title:
            self._identity.title = title
        if domain:
            self._identity.domain = domain
        if description:
            self._identity.description = description
        return self

    def main_mission(
        self,
        goal: str = "",
        success_criteria: Optional[Sequence[str]] = None,
        priority: str = "critical",
    ) -> "ProblemBuilder":
        self._mission.main = MainMission(
            goal=goal,
            success_criteria=list(success_criteria or []),
            priority=priority,
        )
        return self

    def goal(self, description: str = "", success_criteria: Optional[Sequence[str]] = None, priority: str = "critical") -> "ProblemBuilder":
        return self.main_mission(goal=description, success_criteria=success_criteria, priority=priority)

    def add_sub_mission(
        self,
        kind: str = "custom",
        description: str = "",
        priority: str = "normal",
        done: bool = False,
    ) -> "ProblemBuilder":
        self._mission.subs.append(
            SubMission(kind=kind, description=description, priority=priority, done=done)
        )
        return self

    def add_constraint(self, statement: str, kind: str = "hard", priority: int = 0) -> "ProblemBuilder":
        c = ConstraintSpec(statement=statement, kind=kind, priority=priority)
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
        for stmt, pri in [
            ("推測しない。不明な点は不明と明示する。", 10),
            ("不可能なことは不可能と言う。", 10),
            ("制約違反を隠さない。", 10),
            ("不足情報を明示する。", 9),
        ]:
            self.add_constraint(stmt, kind="hard", priority=pri)
        return self

    def scope(self, in_scope: Optional[Sequence[str]] = None, out_of_scope: Optional[Sequence[str]] = None) -> "ProblemBuilder":
        if in_scope is not None:
            self._scope.in_scope = list(in_scope)
        if out_of_scope is not None:
            self._scope.out_of_scope = list(out_of_scope)
        return self

    def knowledge(
        self,
        observation: Optional[Sequence[str]] = None,
        inference: Optional[Sequence[str]] = None,
        assumption: Optional[Sequence[str]] = None,
        unknown: Optional[Sequence[str]] = None,
        missing: Optional[Sequence[str]] = None,
    ) -> "ProblemBuilder":
        if observation is not None:
            self._knowledge.observation = list(observation)
        if inference is not None:
            self._knowledge.inference = list(inference)
        if assumption is not None:
            self._knowledge.assumption = list(assumption)
        if unknown is not None:
            self._knowledge.unknown = list(unknown)
        if missing is not None:
            self._knowledge.missing = list(missing)
        return self

    def thinking_profile(
        self,
        stance: str = "balanced",
        perspective: str = "advisor",
        depth: str = "normal",
        reasoning_bias: str = "balanced",
        evidence_level: str = "observation_first",
        perspective_note: str = "",
    ) -> "ProblemBuilder":
        self._thinking = ThinkingProfile(
            stance=stance, perspective=perspective, depth=depth,
            reasoning_bias=reasoning_bias, evidence_level=evidence_level,
            perspective_note=perspective_note,
        )
        return self

    def behavior(
        self,
        role: str = "collaborator",
        role_description: str = "",
        criticism_level: str = "1_normal",
        if_unknown: str = "answer_unknown",
        if_assumption: str = "mark_assumption",
        if_scope_violation: str = "stop",
        if_missing_required: str = "ask",
        if_low_confidence: str = "state_confidence",
    ) -> "ProblemBuilder":
        self._behavior = Behavior(
            role=role, role_description=role_description, criticism_level=criticism_level,
            rules=BehaviorRules(
                if_unknown=if_unknown, if_assumption=if_assumption,
                if_scope_violation=if_scope_violation,
                if_missing_required=if_missing_required,
                if_low_confidence=if_low_confidence,
            ),
        )
        return self

    def prediction_policy(
        self,
        allow_prediction: bool = True,
        minimum_evidence: str = "medium",
        when_uncertain: str = "state_unknown",
        show_confidence: bool = True,
        explain_reason: bool = True,
        refuse_if_below_minimum: bool = True,
    ) -> "ProblemBuilder":
        self._prediction = PredictionPolicy(
            allow_prediction=allow_prediction,
            minimum_evidence=minimum_evidence,
            when_uncertain=when_uncertain,
            show_confidence=show_confidence,
            explain_reason=explain_reason,
            refuse_if_below_minimum=refuse_if_below_minimum,
        )
        return self

    def evaluation(self, criteria: Sequence[Dict[str, Any]]) -> "ProblemBuilder":
        self._evaluation = EvaluationCriteria(
            criteria=[
                EvaluationCriterion(
                    name=str(c["name"]),
                    weight=float(c.get("weight", 0.25)),
                    notes=str(c.get("notes", "")),
                )
                for c in criteria
            ]
        )
        return self

    def output(self, format: str = "markdown", language: str = "ja", **kwargs: Any) -> "ProblemBuilder":
        self._output = OutputSpec(format=format, language=language, **{
            k: kwargs[k] for k in ("include_pros_cons", "include_confidence", "include_needed_info") if k in kwargs
        })
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
            identity=self._identity,
            mission=self._mission,
            thinking_profile=self._thinking,
            prediction_policy=self._prediction,
            evaluation=self._evaluation,
            knowledge=knowledge,
            constraints=self._constraints,
            scope=self._scope,
            behavior=self._behavior,
            phase_state=self._phase,
            output=self._output,
        )


# =============================================================================
# Validator（運用層）
# =============================================================================

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
        report.add(Finding("IDENTITY_TITLE_MISSING", Severity.ERROR, "title が空", "タイトルを設定"))
    if not spec.mission.main.goal.strip():
        report.add(Finding("MISSION_GOAL_MISSING", Severity.ERROR, "Main Mission goal が空", "達成目標を書く"))
    if not spec.scope.in_scope and not spec.scope.out_of_scope:
        report.add(Finding("SCOPE_EMPTY", Severity.WARN, "Scope 未定義", "in_scope / out_of_scope を設定"))
    if spec.knowledge.inference and not spec.knowledge.observation:
        report.add(Finding("KNOWLEDGE_INFERENCE_WITHOUT_OBSERVATION", Severity.WARN, "inference のみ", "観測を追加か assumption へ"))
    if not spec.constraints.all():
        report.add(Finding("CONSTRAINT_EMPTY", Severity.WARN, "Constraints が空", "safety constraint 推奨"))
    if not spec.evaluation.criteria:
        report.add(Finding("EVALUATION_EMPTY", Severity.WARN, "EvaluationCriteria が空", "評価基準と重みを設定推奨"))
    pq = spec.assess_prediction_quality()
    if spec.prediction_policy.allow_prediction and not pq.is_prediction_allowed:
        report.add(Finding(
            "PREDICTION_BELOW_MINIMUM_EVIDENCE", Severity.WARN,
            f"根拠不足 (level={pq.evidence_level}, need={spec.prediction_policy.minimum_evidence})",
            f"when_uncertain={spec.prediction_policy.when_uncertain} に従う",
        ))
    return report


# =============================================================================
# Adapter（外部層・最小）
# =============================================================================

def render_specification(spec: ProblemSpecification) -> str:
    pq = spec.assess_prediction_quality()
    gate = spec.phase_state.last_gate
    lines = [
        "=" * 50,
        "PROBLEM SPECIFICATION",
        f"schema : {spec.schema}",
        "=" * 50,
        "",
        f"Title : {spec.identity.title}",
        "",
        "--- Mission (core) ---",
        f"  Main [{spec.mission.main.priority}]: {spec.mission.main.goal}",
    ]
    if spec.mission.main.success_criteria:
        for c in spec.mission.main.success_criteria:
            lines.append(f"    success: {c}")
    if spec.mission.subs:
        lines.append("  Subs:")
        for s in spec.mission.subs:
            mark = "✓" if s.done else "·"
            lines.append(f"    {mark} [{s.priority}/{s.kind}] {s.description or s.kind}")
    lines.extend([
        "",
        f"--- ThinkingProfile (core) ---",
        f"  stance={spec.thinking_profile.stance} perspective={spec.thinking_profile.perspective}",
        "",
        f"--- PredictionPolicy (core) ---",
        f"  allow={spec.prediction_policy.allow_prediction} min={spec.prediction_policy.minimum_evidence}",
        f"  quality: allowed={pq.is_prediction_allowed} level={pq.evidence_level} conf={pq.confidence}",
        f"  reason: {pq.reason}",
    ])
    if spec.evaluation.criteria:
        lines.append("")
        lines.append("--- EvaluationCriteria (core) ---")
        for c in spec.evaluation.normalized():
            lines.append(f"  {c.name}: {c.weight:.2f}")
    lines.append("")
    lines.append(f"--- Phase / Gate (ops) ---")
    lines.append(f"  phase={spec.phase_state.phase}")
    if gate is not None:
        lines.append(f"  gate: proceed={gate.can_proceed} codes={gate.codes}")
        if gate.blocking:
            lines.append(f"  blocking: {gate.blocking}")
    lines.append("=" * 50)
    return "\n".join(lines)


def compile_for_generic(spec: ProblemSpecification) -> str:
    pq = spec.assess_prediction_quality()
    header = f"""あなたは PSS の問題仕様書を受け取ります。実行エンジンではなく仕様に従ってください。

【Mission】[{spec.mission.main.priority}] {spec.mission.main.goal}
【Thinking】stance={spec.thinking_profile.stance} perspective={spec.thinking_profile.perspective}
【Prediction】allow={spec.prediction_policy.allow_prediction} min={spec.prediction_policy.minimum_evidence}
  現在根拠={pq.evidence_level}(n={pq.evidence_count}) → 予測許可={pq.is_prediction_allowed}
  不確実時={spec.prediction_policy.when_uncertain}
"""
    if not pq.is_prediction_allowed:
        header += f"根拠不足のため予測せず「{spec.prediction_policy.when_uncertain}」に従うこと。\n"
    if spec.evaluation.criteria:
        header += "評価: " + ", ".join(f"{c.name}({c.weight:.2f})" for c in spec.evaluation.normalized()) + "\n"
    return header + "\n" + render_specification(spec)


# =============================================================================
# Demo
# =============================================================================

def main() -> None:
    print("=" * 60)
    print("PSS v1.0.0-rc1 — Release Candidate")
    print("Core: Mission / ThinkingProfile / PredictionPolicy / Evaluation")
    print("=" * 60)

    print("\n### Case A: required ask_missing → Gate block")
    spec_a = (
        ProblemBuilder()
        .identity(title="リリース可否", domain="product")
        .main_mission(goal="来月リリース可否を判断する", success_criteria=["リスク許容"], priority="critical")
        .add_sub_mission(kind="ask_missing", description="不明点を質問", priority="high")  # required
        .add_sub_mission(kind="alternatives", description="代替案", priority="low")         # optional
        .knowledge(observation=["開発80%"], missing=["負荷試験"], unknown=["負荷試験"])
        .add_default_safety_constraints()
        .thinking_profile(stance="cautious", perspective="reviewer")
        .prediction_policy(minimum_evidence="high", when_uncertain="ask")
        .evaluation([
            {"name": "正確性", "weight": 0.45},
            {"name": "安全性", "weight": 0.35},
            {"name": "速度", "weight": 0.20},
        ])
        .phase(phase="1_clarify")
        .build()
    )
    g = spec_a.run_gate()
    print(spec_a.summary())
    print(f"Gate codes={g.codes} proceed={g.can_proceed}")

    print("\n### Case B: optional missing only → Gate pass (optional は省略可)")
    spec_b = (
        ProblemBuilder()
        .identity(title="資料完成可否", domain="business")
        .main_mission(goal="会議までの完成可否を判断", priority="critical")
        .add_sub_mission(kind="ask_missing", description="任意の確認", priority="low")  # optional
        .knowledge(observation=["会議は火曜", "初稿は今週", "レビュー金曜", "前回2日", "データ済"])
        .scope(in_scope=["完成可否判断"], out_of_scope=["執筆"])
        .add_default_safety_constraints()
        .thinking_profile(stance="analytical", perspective="advisor")
        .prediction_policy(minimum_evidence="medium")
        .evaluation([{"name": "正確性", "weight": 0.6}, {"name": "速度", "weight": 0.4}])
        .phase(phase="2_confirm", scope="完成可否のみ", scope_agreed=True)
        .build()
    )
    g2 = spec_b.run_gate()
    print(spec_b.summary())
    print(f"Gate codes={g2.codes} proceed={g2.can_proceed}")
    print()
    print(compile_for_generic(spec_b)[:500])
    print("...")


if __name__ == "__main__":
    main()
