"""
PSS Test Cases (v0.3)
=====================
Problem Specification System の基本動作を検証する。

実行:
  cd /home/workdir/artifacts
  python -m pytest pss/test_pss.py -v
"""

from __future__ import annotations

import pytest
from pss import (
    ProblemBuilder,
    ProblemSpecification,
    KnowledgeState,
    SectionGate,
    from_capsule,
    to_capsule,
    compile_for_generic,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def make_basic_spec() -> ProblemSpecification:
    return (
        ProblemBuilder()
        .title("仕事資料の作成")
        .description("進捗報告資料を作成する")
        .domain("business.document")
        .current_state(description="メモ書きしかない")
        .goal(
            description="完成度の高い資料を提出する",
            success_criteria=["内容が明確", "次アクションがある"],
        )
        .difference(
            description="素材 → 正式資料",
            gaps=["章立て", "数値裏付け"],
        )
        .add_default_safety_constraints()
        .add_constraint("社外秘を含めない", kind="hard", priority=20)
        .section_gate(
            name="DocumentRequirements",
            required_fields=["出力形式", "対象読者", "納期", "引用形式"],
            available_fields=["対象読者", "納期"],
        )
        .knowledge(
            known=["会議は火曜", "Wordで提出"],
            unknown=["引用形式"],
            assumption=["Wordは利用可能"],
        )
        .evaluation_axis({"Accuracy": 1.0, "Safety": 1.2})
        .tolerance(description="完璧でなくてよい", quantitative={"completeness": 0.15})
        .build()
    )


# ------------------------------------------------------------------
# 1. Builder / Core structure
# ------------------------------------------------------------------

class TestProblemBuilder:

    def test_basic_build(self):
        spec = make_basic_spec()
        assert spec.problem.title == "仕事資料の作成"
        assert spec.problem.domain == "business.document"
        assert spec.goal.description.startswith("完成度")
        assert len(spec.difference.gaps) == 2
        assert len(spec.constraints) >= 5  # default 4 + 1 custom

    def test_version_and_schema(self):
        spec = make_basic_spec()
        assert spec.version == "0.3"
        assert spec.schema.startswith("pss.problem_specification")

    def test_summary_contains_key_fields(self):
        spec = make_basic_spec()
        s = spec.summary()
        assert "仕事資料の作成" in s
        assert "MISSING" in s or "出力形式" in s
        assert "Assumption" in s or "Wordは利用可能" in s


# ------------------------------------------------------------------
# 2. Knowledge triad (Known / Unknown / Assumption)
# ------------------------------------------------------------------

class TestKnowledgeState:

    def test_explicit_knowledge(self):
        spec = make_basic_spec()
        assert "会議は火曜" in spec.knowledge.known
        assert "Wordで提出" in spec.knowledge.known
        assert "Wordは利用可能" in spec.knowledge.assumption
        assert "引用形式" in spec.knowledge.unknown

    def test_section_gate_missing_merged_into_unknown(self):
        """SectionGate の missing が Unknown に自動反映されること"""
        spec = make_basic_spec()
        # available に無い項目が unknown に入っている
        assert "出力形式" in spec.knowledge.unknown
        assert "引用形式" in spec.knowledge.unknown
        # available にあるものは missing にならない
        assert "対象読者" not in spec.section_gate.missing_fields
        assert "納期" not in spec.section_gate.missing_fields

    def test_assumption_is_separate_from_known(self):
        spec = make_basic_spec()
        for a in spec.knowledge.assumption:
            assert a not in spec.knowledge.known


# ------------------------------------------------------------------
# 3. SectionGate
# ------------------------------------------------------------------

class TestSectionGate:

    def test_incomplete_when_missing(self):
        gate = SectionGate(
            name="test",
            required_fields=["A", "B", "C"],
        ).evaluate(["A"])
        assert not gate.is_complete
        assert gate.missing_fields == ["B", "C"]
        assert gate.present_fields == ["A"]

    def test_complete_when_all_present(self):
        gate = SectionGate(
            name="test",
            required_fields=["A", "B"],
        ).evaluate(["A", "B", "extra"])
        assert gate.is_complete
        assert gate.missing_fields == []


# ------------------------------------------------------------------
# 4. Capsule round-trip (主入出力経路)
# ------------------------------------------------------------------

class TestCapsuleTransport:

    def test_to_capsule_and_from_capsule_roundtrip(self):
        original = make_basic_spec()
        capsule = to_capsule(original, source="test", clock=7, sequence=3)

        # header の基本確認
        assert capsule["header"]["source"] == "test"
        assert capsule["header"]["clock"] == 7
        assert capsule["header"]["sequence"] == 3
        assert "pss_payload" in capsule

        # 復元
        restored = from_capsule(capsule)

        assert restored.problem.title == original.problem.title
        assert restored.problem.domain == original.problem.domain
        assert restored.goal.description == original.goal.description
        assert restored.difference.gaps == original.difference.gaps
        assert restored.knowledge.known == original.knowledge.known
        assert restored.knowledge.unknown == original.knowledge.unknown
        assert restored.knowledge.assumption == original.knowledge.assumption
        assert restored.version == original.version

    def test_from_capsule_fallback_without_payload(self):
        """pss_payload が無い Capsule でも最低限の仕様が作れること"""
        minimal_capsule = {
            "header": {
                "source": "ExternalSystem",
                "clock": 0,
                "sequence": 0,
            },
            "input": {
                "raw_input": "何か問題がある",
                "metadata": {
                    "title": "外部からの問題",
                    "domain": "test",
                    "known": ["事実A"],
                    "unknown": ["不明B"],
                    "assumption": ["仮定C"],
                },
            },
            "observations": [],
            "delta": {"changes": {}},
            "integrity": {"valid": True},
        }
        spec = from_capsule(minimal_capsule)
        assert spec.problem.title == "外部からの問題"
        assert spec.problem.domain == "test"
        assert "事実A" in spec.knowledge.known
        assert "不明B" in spec.knowledge.unknown
        assert "仮定C" in spec.knowledge.assumption


# ------------------------------------------------------------------
# 5. Constraints
# ------------------------------------------------------------------

class TestConstraints:

    def test_default_safety_constraints_present(self):
        spec = make_basic_spec()
        statements = [c.statement for c in spec.constraints]
        assert any("推測しない" in s for s in statements)
        assert any("不可能なこと" in s for s in statements)
        assert any("社外秘" in s for s in statements)

    def test_priority_ordering(self):
        spec = make_basic_spec()
        # 社外秘は priority=20 で入れている
        high = [c for c in spec.constraints if c.priority >= 20]
        assert len(high) >= 1
        assert "社外秘" in high[0].statement


# ------------------------------------------------------------------
# 6. Serialization
# ------------------------------------------------------------------

class TestSerialization:

    def test_to_dict_from_dict_roundtrip(self):
        original = make_basic_spec()
        data = original.to_dict()
        restored = ProblemSpecification.from_dict(data)

        assert restored.problem.title == original.problem.title
        assert restored.knowledge.assumption == original.knowledge.assumption
        assert restored.evaluation_axis.axes == original.evaluation_axis.axes
        assert restored.tolerance.quantitative == original.tolerance.quantitative

    def test_schema_version_in_dict(self):
        spec = make_basic_spec()
        d = spec.to_dict()
        assert d["schema"].startswith("pss.")
        assert d["version"] == "0.3"


# ------------------------------------------------------------------
# 7. Adapter (smoke)
# ------------------------------------------------------------------

class TestAdapter:

    def test_compile_contains_explanation_and_spec(self):
        spec = make_basic_spec()
        text = compile_for_generic(spec)

        # 説明部分
        assert "Problem Specification" in text
        assert "Unknown" in text
        assert "Assumption" in text
        assert "勝手に埋めない" in text

        # 仕様本体
        assert "仕事資料の作成" in text
        assert "完成度の高い資料" in text


# ------------------------------------------------------------------
# 8. Edge cases
# ------------------------------------------------------------------

class TestEdgeCases:

    def test_empty_builder(self):
        spec = ProblemBuilder().build()
        assert spec.problem.title == ""
        assert spec.knowledge.known == []
        assert spec.constraints == []
        assert spec.section_gate is None

    def test_no_section_gate(self):
        spec = (
            ProblemBuilder()
            .title("単純な問題")
            .goal(description="ゴールだけ")
            .build()
        )
        assert spec.section_gate is None
        assert "単純な問題" in spec.summary()
