"""
PSS Demo (v0.3)
===============
1. ProblemBuilder で仕様を組み立てる
2. Capsule に載せる
3. Capsule から復元する（主入力経路の確認）
4. Adapter で LLM 向けにコンパイルする
"""

from __future__ import annotations

from pss import ProblemBuilder
from pss.transport import to_capsule, from_capsule, render_specification
from pss.adapter import compile_for_generic


def main() -> None:
    # ----------------------------------------------------------
    # 1. Builder で組み立て（手動経路）
    # ----------------------------------------------------------
    builder = (
        ProblemBuilder()
        .title("仕事資料の作成")
        .description("来週の定例会議で使う進捗報告資料を作成する")
        .domain("business.document")
        .current_state(description="現在はメモ書き程度の素材しかない")
        .goal(
            description="会議で使える完成度の高い進捗報告資料を提出する",
            success_criteria=[
                "部門長が内容を理解できる",
                "次のアクションが明確",
                "事実に基づいている",
            ],
        )
        .difference(
            description="素材メモ → 正式資料への変換が必要",
            gaps=[
                "構造化された章立て",
                "数値の裏付け",
                "リスクと次アクションの明示",
            ],
        )
        .add_default_safety_constraints()
        .add_constraint("社外秘情報を含めない", kind="hard", priority=20)
        .section_gate(
            name="DocumentRequirements",
            required_fields=["出力形式", "対象読者", "納期", "引用形式", "ページ制約"],
            available_fields=["対象読者", "納期"],
        )
        .knowledge(
            known=[
                "会議は来週火曜 10:00",
                "参加者は部門長とプロジェクトメンバー",
                "Wordで提出する",
            ],
            unknown=[
                "正式な出力フォーマット",
                "引用形式の指定",
                "ページ数上限",
            ],
            assumption=[
                "Wordは利用可能と仮定する",
                "前回の資料フォーマットを踏襲してよいと仮定する",
            ],
        )
        .evaluation_axis(
            {"Accuracy": 1.0, "Safety": 1.2, "Clarity": 0.9, "Speed": 0.4},
            notes="安全性と正確性を最優先",
        )
        .tolerance(
            description="完璧な資料である必要はない",
            quantitative={"completeness": 0.15},
            qualitative=["主要な論点さえ押さえれば可"],
        )
    )

    spec = builder.build()

    print("=" * 60)
    print("1. summary()")
    print("=" * 60)
    print(spec.summary())
    print()

    # ----------------------------------------------------------
    # 2. Capsule に載せる
    # ----------------------------------------------------------
    capsule = to_capsule(spec, source="PSS-Demo", clock=1)
    print("=" * 60)
    print("2. to_capsule() → Capsule header")
    print("=" * 60)
    print("source  :", capsule["header"]["source"])
    print("schema  :", capsule["pss_payload"]["schema"])
    print("version :", capsule["pss_payload"]["version"])
    print()

    # ----------------------------------------------------------
    # 3. Capsule から復元（主入力経路）
    # ----------------------------------------------------------
    restored = from_capsule(capsule)
    print("=" * 60)
    print("3. from_capsule() → restored summary")
    print("=" * 60)
    print(restored.summary())
    print()
    print("Round-trip OK:", restored.problem.title == spec.problem.title)
    print()

    # ----------------------------------------------------------
    # 4. Adapter
    # ----------------------------------------------------------
    print("=" * 60)
    print("4. compile_for_generic() 冒頭")
    print("=" * 60)
    compiled = compile_for_generic(restored)
    print(compiled[:800] + "\n... (truncated)")


if __name__ == "__main__":
    main()
