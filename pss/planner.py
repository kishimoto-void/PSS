"""
PSS Fix Planner (v0.7)
======================
Validator の Findings から「修正計画（Fix Plan）」を生成する。

設計思想:
  - Validator は診断だけを行う（修正しない）
  - Fix Planner は Findings を受け取り、実行可能な計画を返す
  - 実行主体（人間 / LLM / IDE / CI）は問わない
  - 計画は純粋データとして扱える
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

from .validator import Finding, Severity, ValidationReport


class FixAction(str, Enum):
    ASK_USER = "ask_user"
    SET_FIELD = "set_field"
    ADD_ITEM = "add_item"
    MOVE_ITEM = "move_item"
    ADD_CONSTRAINT = "add_constraint"
    SET_RULE = "set_rule"
    REVALIDATE = "revalidate"
    REVIEW = "review"


@dataclass
class FixStep:
    priority: int
    action: str
    location: str
    description: str
    suggested_value: Any = None
    related_finding_code: str = ""
    severity: str = "WARN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority": self.priority,
            "action": self.action,
            "location": self.location,
            "description": self.description,
            "suggested_value": self.suggested_value,
            "related_finding_code": self.related_finding_code,
            "severity": self.severity,
        }


@dataclass
class FixPlan:
    steps: List[FixStep] = field(default_factory=list)
    overall_severity: str = "PASS"
    version: str = "0.7"

    def add(self, step: FixStep) -> None:
        self.steps.append(step)

    def sorted_steps(self) -> List[FixStep]:
        return sorted(self.steps, key=lambda s: (s.priority, s.severity != "ERROR"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "overall_severity": self.overall_severity,
            "steps": [s.to_dict() for s in self.sorted_steps()],
            "summary": self.summary(),
        }

    def summary(self) -> str:
        lines = [
            f"[PSS Fix Plan v{self.version}]",
            f"Overall severity : {self.overall_severity}",
            f"Total steps      : {len(self.steps)}",
            "",
        ]
        if not self.steps:
            lines.append("No fixes required.")
            return "\n".join(lines)

        lines.append("Plan")
        lines.append("----")
        for i, step in enumerate(self.sorted_steps(), 1):
            lines.append(f"{i}. [{step.severity}] {step.description}")
            lines.append(f"   action   : {step.action}")
            lines.append(f"   location : {step.location}")
            if step.suggested_value is not None:
                lines.append(f"   suggested: {step.suggested_value}")
            lines.append("")
        lines.append("After applying steps, re-run validation is recommended.")
        return "\n".join(lines)


def _plan_from_finding(f: Finding) -> List[FixStep]:
    steps: List[FixStep] = []
    code = f.code
    sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)

    if code == "IDENTITY_TITLE_MISSING":
        steps.append(FixStep(10, "ask_user", "identity.title", "Title が空です。問題を識別できるタイトルを設定してください。", related_finding_code=code, severity=sev))
    elif code == "OBJECTIVE_GOAL_MISSING":
        steps.append(FixStep(10, "ask_user", "objective.goal.description", "Goal が空です。到達したい状態を記述してください。", related_finding_code=code, severity=sev))
    elif code == "SCOPE_EMPTY":
        steps.append(FixStep(30, "ask_user", "scope", "Scope が未定義です。in_scope / out_of_scope を設定してください。", related_finding_code=code, severity=sev))
    elif code == "SCOPE_OVERLAP":
        steps.append(FixStep(20, "review", "scope", "in_scope と out_of_scope に重複があります。重複を解消してください。", related_finding_code=code, severity=sev))
    elif code == "PHASE_INVALID":
        steps.append(FixStep(15, "set_field", "phase_state.phase", "不正な Phase 値です。1_clarify / 2_confirm / 3_answer のいずれかに設定してください。", suggested_value="1_clarify", related_finding_code=code, severity=sev))
    elif code == "PHASE_SCOPE_MISSING":
        steps.append(FixStep(25, "ask_user", "phase_state.scope", "Confirm/Answer フェーズなのに scope が未設定です。出力範囲を確定してください。", related_finding_code=code, severity=sev))
    elif code == "PHASE_CYCLE_INVALID":
        steps.append(FixStep(15, "set_field", "phase_state.cycle", "cycle は 1 以上である必要があります。", suggested_value=1, related_finding_code=code, severity=sev))
    elif code == "BEHAVIOR_RULE_MISSING":
        rule_name = f.location.split(".")[-1] if f.location else "unknown"
        default_map = {"if_unknown": "answer_unknown", "if_assumption": "mark_assumption", "if_scope_violation": "stop", "if_missing_required": "ask", "if_low_confidence": "state_confidence"}
        steps.append(FixStep(40, "set_rule", f.location or "behavior.rules", f"Behavior rule '{rule_name}' が未設定です。デフォルト値を設定することを推奨します。", suggested_value=default_map.get(rule_name, "ask"), related_finding_code=code, severity=sev))
    elif code == "BEHAVIOR_ROLE_DESC_MISSING":
        steps.append(FixStep(45, "ask_user", "behavior.role_description", "role=custom なのに説明が空です。ロールの説明を追加してください。", related_finding_code=code, severity=sev))
    elif code == "KNOWLEDGE_INFERENCE_WITHOUT_OBSERVATION":
        steps.append(FixStep(35, "move_item", "knowledge", "inference がありますが observation が空です。推論を assumption に移すか、根拠となる観測を追加してください。", related_finding_code=code, severity=sev))
    elif code == "KNOWLEDGE_ONLY_ASSUMPTION":
        steps.append(FixStep(40, "ask_user", "knowledge.observation", "assumption のみです。可能な範囲で観測事実を追加してください。", related_finding_code=code, severity=sev))
    elif code == "KNOWLEDGE_MISSING_NOT_IN_UNKNOWN":
        steps.append(FixStep(50, "add_item", "knowledge.unknown", "missing の項目が unknown に含まれていません。unknown にも追加してください。", related_finding_code=code, severity=sev))
    elif code == "KNOWLEDGE_EMPTY":
        steps.append(FixStep(30, "ask_user", "knowledge", "Knowledge が空です。少なくとも observation または unknown を記入してください。", related_finding_code=code, severity=sev))
    elif code == "CONSTRAINT_EMPTY":
        steps.append(FixStep(50, "add_constraint", "constraints.hard", "Constraints が空です。最低限の safety constraint を追加することを推奨します。", suggested_value="推測しない。不明な点は不明と明示する。", related_finding_code=code, severity=sev))
    elif code == "CONSTRAINT_PRIORITY_NEGATIVE":
        steps.append(FixStep(55, "set_field", "constraints", "priority が負の Constraint があります。0 以上に修正してください。", suggested_value=0, related_finding_code=code, severity=sev))
    elif code == "OUTPUT_FORMAT_MISSING":
        steps.append(FixStep(60, "set_field", "output.format", "output.format が未設定です。", suggested_value="markdown", related_finding_code=code, severity=sev))
    elif code == "OUTPUT_JSON_NO_SCHEMA":
        steps.append(FixStep(60, "ask_user", "output.required_sections", "format=json なのに required_sections が空です。出力キーを指定してください。", related_finding_code=code, severity=sev))
    if not steps:
        steps.append(FixStep(90, "review", f.location or "", f.message, related_finding_code=code, severity=sev))
    return steps


class FixPlanner:
    def plan(self, report: ValidationReport) -> FixPlan:
        plan = FixPlan(overall_severity=report.overall.value if hasattr(report.overall, "value") else str(report.overall))
        for finding in report.findings:
            for step in _plan_from_finding(finding):
                plan.add(step)
        if plan.steps:
            plan.add(FixStep(100, "revalidate", "", "修正後に Validation を再実行してください。", severity="INFO"))
        return plan


def plan_fixes(report: ValidationReport) -> FixPlan:
    return FixPlanner().plan(report)
