"""
PSS Validator (v0.7)
====================
思考条件仕様書を診断する。

設計思想:
  - 単純な Yes/No ではなく、診断レポートを返す
  - PASS / WARN / ERROR の3段階
  - 各観点を独立した Validator に分離
  - CompositeValidator が集約
  - 将来の「修正提案」まで拡張可能な構造にする
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence
from .core import ProblemSpecification, Phase


class Severity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class Finding:
    """個別の診断結果。"""
    code: str
    severity: Severity
    message: str
    location: str = ""
    suggestion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationReport:
    """総合診断レポート。"""
    overall: Severity = Severity.PASS
    findings: List[Finding] = field(default_factory=list)
    coverage: Dict[str, Severity] = field(default_factory=dict)
    version: str = "0.7"

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)
        if finding.severity == Severity.ERROR:
            self.overall = Severity.ERROR
        elif finding.severity == Severity.WARN and self.overall != Severity.ERROR:
            self.overall = Severity.WARN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": self.overall.value,
            "version": self.version,
            "coverage": {k: v.value for k, v in self.coverage.items()},
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary(),
        }

    def summary(self) -> str:
        lines = [
            f"[PSS Validation Report v{self.version}]",
            f"Overall : {self.overall.value}",
            "",
            "Coverage",
            "---------",
        ]
        for k, v in sorted(self.coverage.items()):
            lines.append(f"{k:<12} {v.value}")
        errors = [f for f in self.findings if f.severity == Severity.ERROR]
        warns = [f for f in self.findings if f.severity == Severity.WARN]
        if errors:
            lines.append("")
            lines.append("Errors")
            lines.append("------")
            for f in errors:
                lines.append(f"- [{f.code}] {f.message}")
                if f.suggestion:
                    lines.append(f"  → Suggestion: {f.suggestion}")
        if warns:
            lines.append("")
            lines.append("Warnings")
            lines.append("--------")
            for f in warns:
                lines.append(f"- [{f.code}] {f.message}")
                if f.suggestion:
                    lines.append(f"  → Suggestion: {f.suggestion}")
        if not errors and not warns:
            lines.append("")
            lines.append("No issues found.")
        return "\n".join(lines)


class BaseValidator:
    name: str = "base"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        raise NotImplementedError


class ScopeValidator(BaseValidator):
    name = "Scope"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        s = spec.scope
        if not s.in_scope and not s.out_of_scope:
            findings.append(Finding(
                code="SCOPE_EMPTY",
                severity=Severity.WARN,
                message="Scope が未定義です（in_scope / out_of_scope が空）",
                location="scope",
                suggestion="主要な対象範囲を in_scope に、扱わないものを out_of_scope に書いてください",
            ))
        if s.in_scope and s.out_of_scope:
            overlap = set(s.in_scope) & set(s.out_of_scope)
            if overlap:
                findings.append(Finding(
                    code="SCOPE_OVERLAP",
                    severity=Severity.ERROR,
                    message=f"in_scope と out_of_scope に重複があります: {list(overlap)}",
                    location="scope",
                    suggestion="重複を解消してください",
                ))
        return findings


class PhaseValidator(BaseValidator):
    name = "Phase"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        ps = spec.phase_state
        valid_phases = {p.value for p in Phase}
        if ps.phase not in valid_phases and not ps.phase.startswith(("1_", "2_", "3_")):
            findings.append(Finding(
                code="PHASE_INVALID",
                severity=Severity.ERROR,
                message=f"不正な Phase 値です: {ps.phase}",
                location="phase_state.phase",
                suggestion="1_clarify / 2_confirm / 3_answer のいずれかを使用してください",
            ))
        if ps.phase in ("2_confirm", "3_answer") and not ps.scope and not ps.scope_agreed:
            findings.append(Finding(
                code="PHASE_SCOPE_MISSING",
                severity=Severity.WARN,
                message="Confirm/Answer フェーズなのに scope が未設定です",
                location="phase_state",
                suggestion="Phase 2 で scope を確定し、scope_agreed=True にしてください",
            ))
        if ps.cycle < 1:
            findings.append(Finding(
                code="PHASE_CYCLE_INVALID",
                severity=Severity.ERROR,
                message=f"cycle は 1 以上である必要があります（現在: {ps.cycle}）",
                location="phase_state.cycle",
            ))
        return findings


class BehaviorValidator(BaseValidator):
    name = "Behavior"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        b = spec.behavior
        rules = b.rules
        required_rules = [
            ("if_unknown", rules.if_unknown),
            ("if_assumption", rules.if_assumption),
            ("if_scope_violation", rules.if_scope_violation),
            ("if_missing_required", rules.if_missing_required),
            ("if_low_confidence", rules.if_low_confidence),
        ]
        for name, value in required_rules:
            if not value or not str(value).strip():
                findings.append(Finding(
                    code="BEHAVIOR_RULE_MISSING",
                    severity=Severity.WARN,
                    message=f"Behavior rule '{name}' が未設定です",
                    location=f"behavior.rules.{name}",
                    suggestion=f"{name} に具体的な行動を設定してください（例: answer_unknown / ask / stop）",
                ))
        if b.role == "custom" and not b.role_description:
            findings.append(Finding(
                code="BEHAVIOR_ROLE_DESC_MISSING",
                severity=Severity.WARN,
                message="role=custom なのに role_description が空です",
                location="behavior.role_description",
                suggestion="カスタムロールの説明を書いてください",
            ))
        return findings


class KnowledgeValidator(BaseValidator):
    name = "Knowledge"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        k = spec.knowledge
        if k.inference and not k.observation:
            findings.append(Finding(
                code="KNOWLEDGE_INFERENCE_WITHOUT_OBSERVATION",
                severity=Severity.WARN,
                message="inference が存在しますが observation が空です（観測なしの推論）",
                location="knowledge",
                suggestion="推論の根拠となる観測事実を observation に追加するか、inference を assumption に移してください",
            ))
        if k.assumption and not k.observation and not k.inference:
            findings.append(Finding(
                code="KNOWLEDGE_ONLY_ASSUMPTION",
                severity=Severity.WARN,
                message="assumption のみで observation / inference がありません",
                location="knowledge",
                suggestion="可能な範囲で観測事実を追加してください",
            ))
        for m in k.missing:
            if m not in k.unknown:
                findings.append(Finding(
                    code="KNOWLEDGE_MISSING_NOT_IN_UNKNOWN",
                    severity=Severity.WARN,
                    message=f"missing の項目が unknown に含まれていません: {m}",
                    location="knowledge.missing",
                    suggestion="missing は unknown にも含めることを推奨します",
                ))
        if not any([k.observation, k.inference, k.assumption, k.unknown, k.missing]):
            findings.append(Finding(
                code="KNOWLEDGE_EMPTY",
                severity=Severity.WARN,
                message="Knowledge が完全に空です",
                location="knowledge",
                suggestion="少なくとも Known（observation）または Unknown を記入してください",
            ))
        return findings


class ConstraintValidator(BaseValidator):
    name = "Constraint"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        c = spec.constraints
        all_c = c.all()
        if not all_c:
            findings.append(Finding(
                code="CONSTRAINT_EMPTY",
                severity=Severity.WARN,
                message="Constraints が空です",
                location="constraints",
                suggestion="最低限の safety constraint（推測しない、など）を追加することを推奨します",
            ))
        for item in all_c:
            if item.priority < 0:
                findings.append(Finding(
                    code="CONSTRAINT_PRIORITY_NEGATIVE",
                    severity=Severity.WARN,
                    message=f"priority が負です: {item.statement[:40]}...",
                    location="constraints",
                ))
        return findings


class OutputValidator(BaseValidator):
    name = "Output"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        o = spec.output
        if not o.format:
            findings.append(Finding(
                code="OUTPUT_FORMAT_MISSING",
                severity=Severity.WARN,
                message="output.format が未設定です",
                location="output.format",
                suggestion="markdown / plain / json などを指定してください",
            ))
        if o.format == "json" and not o.required_sections:
            findings.append(Finding(
                code="OUTPUT_JSON_NO_SCHEMA",
                severity=Severity.WARN,
                message="format=json なのに required_sections が空です（スキーマ相当の指定がない）",
                location="output",
                suggestion="出力に含めるべきキーを required_sections に列挙してください",
            ))
        return findings


class IdentityValidator(BaseValidator):
    name = "Identity"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        if not spec.identity.title.strip():
            findings.append(Finding(
                code="IDENTITY_TITLE_MISSING",
                severity=Severity.ERROR,
                message="title が空です",
                location="identity.title",
                suggestion="問題を識別できるタイトルを付けてください",
            ))
        return findings


class ObjectiveValidator(BaseValidator):
    name = "Objective"
    def validate(self, spec: ProblemSpecification) -> List[Finding]:
        findings: List[Finding] = []
        if not spec.objective.goal.description.strip():
            findings.append(Finding(
                code="OBJECTIVE_GOAL_MISSING",
                severity=Severity.ERROR,
                message="Goal が空です",
                location="objective.goal",
                suggestion="到達したい状態を Goal に記述してください",
            ))
        return findings


class CompositeValidator:
    def __init__(self, validators: Optional[Sequence[BaseValidator]] = None) -> None:
        self.validators: List[BaseValidator] = list(validators) if validators else [
            IdentityValidator(),
            ObjectiveValidator(),
            ScopeValidator(),
            PhaseValidator(),
            BehaviorValidator(),
            KnowledgeValidator(),
            ConstraintValidator(),
            OutputValidator(),
        ]

    def validate(self, spec: ProblemSpecification) -> ValidationReport:
        report = ValidationReport()
        for v in self.validators:
            findings = v.validate(spec)
            severity = Severity.PASS
            for f in findings:
                report.add(f)
                if f.severity == Severity.ERROR:
                    severity = Severity.ERROR
                elif f.severity == Severity.WARN and severity != Severity.ERROR:
                    severity = Severity.WARN
            report.coverage[v.name] = severity
        return report


def validate(spec: ProblemSpecification) -> ValidationReport:
    return CompositeValidator().validate(spec)
