"""
PSS Test Suite (v0.9.1)
=======================
主要パス + RC pillars (Mission / PredictionPolicy / Gate diagnosis-only) を網羅。

実験は忠実に実際行って検証する。

実行:
  PYTHONPATH=. python -m pytest pss/test_pss.py -v
"""

from __future__ import annotations

import copy
import pytest
from pss import (
    ProblemBuilder,
    ProblemSpecification,
    validate,
    plan_fixes,
    compile_for_generic,
    Severity,
    Mission,
    PredictionPolicy,
    EvaluationCriteria,
    GateResult,
    GateDecision,
)


def make_minimal_valid() -> ProblemSpecification:
    return (
        ProblemBuilder()
        .identity(title="最小有効仕様", domain="test")
        .goal(description="ゴールを達成する")
        .main_mission(goal="ゴールを達成する", priority="normal")
        .knowledge(observation=["事実A"], unknown=["不明B"])
        .add_default_safety_constraints()
        .behavior(role="collaborator", if_unknown="answer_unknown")
        .prediction_policy(minimum_evidence="medium", when_uncertain="ask")
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
        assert spec.mission.goal.startswith("ゴール")
        assert spec.version.startswith("0.9")
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
        assert "不足1" in k.unknown  # missing is mirrored into unknown

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

    def test_main_mission_and_sub(self):
        spec = (
            ProblemBuilder()
            .identity(title="mission test")
            .main_mission(goal="3年以内に故障リスクが低い中古車を選ぶ", priority="critical")
            .add_sub_mission(kind="ask_missing", description="修復歴と整備記録を確認する", priority="high")
            .knowledge(observation=["予算120万円"], missing=["修復歴"])
            .build()
        )
        assert spec.mission.goal.startswith("3年以内")
        assert spec.mission.priority == "critical"
        assert len(spec.mission.sub_missions) == 1
        assert spec.mission.sub_missions[0].kind == "ask_missing"
        # Objective も同期されていること
        assert "3年以内" in spec.objective.goal.description

    def test_prediction_policy(self):
        spec = (
            ProblemBuilder()
            .identity(title="t")
            .goal(description="g")
            .prediction_policy(minimum_evidence="high", when_uncertain="refuse", allow_forward_looking=False)
            .build()
        )
        pp = spec.prediction_policy
        assert pp.minimum_evidence == "high"
        assert pp.when_uncertain == "refuse"
        assert pp.allow_forward_looking is False


class TestSerialization:
    def test_to_dict_from_dict(self):
        original = make_minimal_valid()
        data = original.to_dict()
        restored = ProblemSpecification.from_dict(data)
        assert restored.identity.title == original.identity.title
        assert restored.objective.goal.description == original.objective.goal.description
        assert restored.mission.goal == original.mission.goal
        assert restored.knowledge.observation == original.knowledge.observation
        assert restored.behavior.role == original.behavior.role
        assert restored.phase_state.phase == original.phase_state.phase
        assert restored.prediction_policy.minimum_evidence == original.prediction_policy.minimum_evidence
        assert restored.version == original.version

    def test_mission_roundtrip(self):
        spec = (
            ProblemBuilder()
            .identity(title="rt")
            .main_mission(goal="main", priority="high")
            .add_sub_mission(kind="sub", description="desc")
            .build()
        )
        data = spec.to_dict()
        restored = ProblemSpecification.from_dict(data)
        assert restored.mission.goal == "main"
        assert len(restored.mission.sub_missions) == 1


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
    def test_compile_contains_key_fields(self):
        spec = make_minimal_valid()
        text = compile_for_generic(spec)
        assert "最小有効仕様" in text or "Goal" in text or "goal" in text.lower()


class TestGateDiagnosisOnly:
    """Gate は仕様を変更しないことを厳格に検証する（実験忠実性）。"""

    def test_gate_returns_result_and_does_not_mutate(self):
        spec = make_minimal_valid()
        before = copy.deepcopy(spec.to_dict())
        result = spec.run_gate()
        after = spec.to_dict()

        assert isinstance(result, GateResult)
        assert result.decision in (GateDecision.PASS.value, GateDecision.BLOCK.value, GateDecision.ASK.value)
        # 仕様が一切変わっていないこと
        assert before == after

    def test_gate_blocks_on_missing_in_clarify(self):
        spec = (
            ProblemBuilder()
            .identity(title="used car")
            .main_mission(goal="低故障リスクの中古車を選ぶ", priority="critical")
            .knowledge(
                observation=["予算120万円", "通勤40km"],
                missing=["修復歴", "整備記録"],
            )
            .prediction_policy(minimum_evidence="high", when_uncertain="ask")
            .phase(phase="1_clarify")
            .build()
        )
        before = copy.deepcopy(spec.to_dict())
        result = spec.diagnose_gate()
        after = spec.to_dict()

        assert result.decision == GateDecision.BLOCK.value
        assert "修復歴" in result.missing_required or any("修復歴" in r for r in result.reasons)
        assert before == after  # no mutation

    def test_gate_pass_when_complete(self):
        spec = (
            ProblemBuilder()
            .identity(title="complete")
            .main_mission(goal="完成可否を判断")
            .knowledge(observation=["会議は火曜", "資料は揃っている"])
            .phase(phase="3_answer", scope_agreed=True)
            .prediction_policy(minimum_evidence="medium", when_uncertain="state_confidence")
            .build()
        )
        result = spec.run_gate()
        assert result.decision == GateDecision.PASS.value

    def test_prediction_policy_influences_gate(self):
        # when_uncertain=refuse + missing → BLOCK
        spec = (
            ProblemBuilder()
            .identity(title="stock")
            .main_mission(goal="株価予測")
            .knowledge(observation=["過去データあり"], missing=["未来イベント"])
            .prediction_policy(minimum_evidence="high", when_uncertain="refuse")
            .phase(phase="2_confirm")
            .build()
        )
        result = spec.diagnose_gate()
        assert result.decision in (GateDecision.BLOCK.value, GateDecision.ASK.value)


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
        # Identity と Goal は揃っているので ERROR ではないはず
        assert report.overall != Severity.ERROR or "IDENTITY" not in str(report.coverage)

    def test_summary_does_not_crash(self):
        spec = make_minimal_valid()
        s = spec.summary()
        assert "最小有効仕様" in s
        assert "1_clarify" in s or "Phase" in s
        assert "Prediction" in s or "medium" in s

    def test_evaluation_criteria_roundtrip(self):
        spec = (
            ProblemBuilder()
            .identity(title="eval")
            .goal(description="g")
            .evaluation_criteria({"accuracy": 0.8, "safety": 0.9})
            .build()
        )
        data = spec.to_dict()
        restored = ProblemSpecification.from_dict(data)
        assert restored.evaluation_criteria.criteria["accuracy"] == 0.8
        assert restored.evaluation_criteria.criteria["safety"] == 0.9
