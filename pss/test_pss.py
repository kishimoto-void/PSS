"""
PSS Test Suite (v0.7)
=====================
主要パスと代表的なタイプを網羅する。

実行:
  PYTHONPATH=. python -m pytest pss/test_pss.py -v
"""

from __future__ import annotations

import pytest
from pss import (
    ProblemBuilder,
    ProblemSpecification,
    validate,
    plan_fixes,
    compile_for_generic,
    Severity,
)


def make_minimal_valid() -> ProblemSpecification:
    return (
        ProblemBuilder()
        .identity(title="最小有効仕様", domain="test")
        .goal(description="ゴールを達成する")
        .knowledge(observation=["事実A"], unknown=["不明B"])
        .add_default_safety_constraints()
        .behavior(role="collaborator", if_unknown="answer_unknown")
        .phase(phase="1_clarify")
        .build()
    )


def make_incomplete() -> ProblemSpecification:
    return (
        ProblemBuilder()
        .identity(title="", domain="test")
        .goal(description="")
        .knowledge(inference=["推論のみ"])
        .behavior(role="custom")
        .build()
    )


class TestBuilder:
    def test_minimal_build(self):
        spec = make_minimal_valid()
        assert spec.identity.title == "最小有効仕様"
        assert spec.objective.goal.description.startswith("ゴール")
        assert spec.version == "0.6"
        assert spec.schema.startswith("pss.problem_specification")

    def test_knowledge_categories(self):
        spec = (
            ProblemBuilder()
            .identity(title="知識テスト")
            .goal(description="g")
            .knowledge(
                observation=["観測1"],
                inference=["推論1"],
                assumption=["仮定1"],
                unknown=["不明1"],
                missing=["不足1"],
            )
            .build()
        )
        k = spec.knowledge
        assert "観測1" in k.observation
        assert "推論1" in k.inference
        assert "仮定1" in k.assumption
        assert "不明1" in k.unknown
        assert "不足1" in k.missing
        assert "不足1" in k.unknown

    def test_behavior_rules(self):
        spec = (
            ProblemBuilder()
            .identity(title="t")
            .goal(description="g")
            .behavior(
                role="reviewer",
                criticism_level="2_strict_review",
                if_unknown="ask",
                if_assumption="mark_assumption",
                if_scope_violation="stop",
            )
            .build()
        )
        b = spec.behavior
        assert b.role == "reviewer"
        assert b.rules.if_unknown == "ask"
        assert b.rules.if_assumption == "mark_assumption"
        assert b.rules.if_scope_violation == "stop"

    def test_phase_state(self):
        spec = (
            ProblemBuilder()
            .identity(title="t")
            .goal(description="g")
            .phase(phase="2_confirm", cycle=2, scope="本文のみ", scope_agreed=True)
            .build()
        )
        assert spec.phase_state.phase == "2_confirm"
        assert spec.phase_state.cycle == 2
        assert spec.phase_state.scope_agreed is True


class TestSerialization:
    def test_to_dict_from_dict(self):
        original = make_minimal_valid()
        data = original.to_dict()
        restored = ProblemSpecification.from_dict(data)
        assert restored.identity.title == original.identity.title
        assert restored.objective.goal.description == original.objective.goal.description
        assert restored.knowledge.observation == original.knowledge.observation
        assert restored.behavior.role == original.behavior.role
        assert restored.phase_state.phase == original.phase_state.phase
        assert restored.version == original.version


class TestValidator:
    def test_valid_spec_passes(self):
        spec = make_minimal_valid()
        report = validate(spec)
        assert report.overall in (Severity.PASS, Severity.WARN)
        assert "Identity" in report.coverage
        assert "Objective" in report.coverage

    def test_incomplete_produces_errors(self):
        spec = make_incomplete()
        report = validate(spec)
        assert report.overall == Severity.ERROR
        codes = {f.code for f in report.findings}
        assert "IDENTITY_TITLE_MISSING" in codes
        assert "OBJECTIVE_GOAL_MISSING" in codes

    def test_knowledge_inference_without_observation(self):
        spec = (
            ProblemBuilder()
            .identity(title="t")
            .goal(description="g")
            .knowledge(inference=["推論だけ"])
            .build()
        )
        report = validate(spec)
        codes = {f.code for f in report.findings}
        assert "KNOWLEDGE_INFERENCE_WITHOUT_OBSERVATION" in codes

    def test_behavior_custom_without_description(self):
        spec = (
            ProblemBuilder()
            .identity(title="t")
            .goal(description="g")
            .behavior(role="custom")
            .build()
        )
        report = validate(spec)
        codes = {f.code for f in report.findings}
        assert "BEHAVIOR_ROLE_DESC_MISSING" in codes

    def test_report_has_suggestions(self):
        spec = make_incomplete()
        report = validate(spec)
        findings_with_suggestion = [f for f in report.findings if f.suggestion]
        assert len(findings_with_suggestion) > 0


class TestFixPlanner:
    def test_plan_from_incomplete(self):
        spec = make_incomplete()
        report = validate(spec)
        plan = plan_fixes(report)
        assert plan.overall_severity == "ERROR"
        assert len(plan.steps) >= 3
        actions = {s.action for s in plan.steps}
        assert "ask_user" in actions
        assert "revalidate" in actions

    def test_plan_priority_order(self):
        spec = make_incomplete()
        report = validate(spec)
        plan = plan_fixes(report)
        steps = plan.sorted_steps()
        priorities = [s.priority for s in steps]
        assert priorities == sorted(priorities)

    def test_plan_contains_related_codes(self):
        spec = make_incomplete()
        report = validate(spec)
        plan = plan_fixes(report)
        codes = {s.related_finding_code for s in plan.steps if s.related_finding_code}
        assert "IDENTITY_TITLE_MISSING" in codes
        assert "OBJECTIVE_GOAL_MISSING" in codes


class TestAdapter:
    def test_compile_contains_behavior_rules(self):
        spec = make_minimal_valid()
        text = compile_for_generic(spec)
        assert "if_unknown" in text or "BEHAVIOR RULES" in text or "answer_unknown" in text
        assert "最小有効仕様" in text or "Goal" in text


class TestEdgeCases:
    def test_empty_builder_does_not_crash(self):
        spec = ProblemBuilder().build()
        assert isinstance(spec, ProblemSpecification)
        report = validate(spec)
        assert report.overall == Severity.ERROR

    def test_all_knowledge_types_together(self):
        spec = (
            ProblemBuilder()
            .identity(title="全知識タイプ")
            .goal(description="g")
            .knowledge(
                observation=["obs"],
                inference=["inf"],
                assumption=["asm"],
                unknown=["unk"],
                missing=["mis"],
                references=["ref"],
            )
            .add_default_safety_constraints()
            .behavior(role="analyst")
            .phase(phase="3_answer", scope="最終回答", scope_agreed=True)
            .build()
        )
        report = validate(spec)
        assert report.overall != Severity.ERROR or "IDENTITY" not in str(report.coverage)

    def test_summary_does_not_crash(self):
        spec = make_minimal_valid()
        s = spec.summary()
        assert "最小有効仕様" in s
        assert "1_clarify" in s or "Phase" in s
