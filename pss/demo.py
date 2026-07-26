"""
PSS Demo (v0.7)
===============
現行構造に合わせた最小デモ。
"""

from __future__ import annotations

from pss import (
    ProblemBuilder,
    validate,
    plan_fixes,
    to_capsule,
    from_capsule,
    compile_for_generic,
)


def main() -> None:
    # 1. Build
    spec = (
        ProblemBuilder()
        .identity(
            title="進捗報告資料の作成",
            domain="business.document",
            description="部門長向けの進捗報告資料を整える",
        )
        .goal(
            description="会議で使える完成度の高い資料を提出する",
            success_criteria=["内容が明確", "次アクションがある"],
        )
        .current_state(description="メモ書きしかない")
        .difference(description="素材 → 正式資料", gaps=["章立て", "数値裏付け"])
        .knowledge(
            observation=[
                "会議は来週火曜 10:00",
                "参加者は部門長とプロジェクトメンバー",
                "Wordで提出する",
            ],
            unknown=["正式な出力フォーマット", "引用形式の指定"],
            assumption=["Wordは利用可能"],
        )
        .add_default_safety_constraints()
        .hard_constraint("社外秘を含めない", priority=20)
        .thinking_profile(
            reasoning_bias="balanced",
            depth="normal",
            evidence_level="observation_first",
        )
        .behavior(
            role="collaborator",
            role_description="壁打ち相手として一緒に整理する",
            if_unknown="answer_unknown",
            if_assumption="mark_assumption",
            if_scope_violation="stop",
        )
        .output(format="markdown", language="ja")
        .evaluation_axis({"Accuracy": 1.0, "Safety": 1.2, "Clarity": 1.0})
        .phase(phase="1_clarify", cycle=1)
        .build()
    )

    print("=== Specification Summary ===")
    print(spec.summary())
    print()

    # 2. Validate
    report = validate(spec)
    print("=== Validation ===")
    print(report.summary())
    print()

    # 3. Fix Plan (if needed)
    if report.overall.value != "PASS":
        plan = plan_fixes(report)
        print("=== Fix Plan ===")
        print(plan.summary())
        print()

    # 4. Capsule round-trip
    capsule = to_capsule(spec, source="demo", clock=1, sequence=1)
    restored = from_capsule(capsule)

    print("=== Round-trip ===")
    print("OK:", restored.identity.title == spec.identity.title)
    print("Role:", restored.behavior.role)
    print("Phase:", restored.phase_state.phase)
    print("Observation count:", len(restored.knowledge.observation))
    print()

    # 5. Compile for LLM
    text = compile_for_generic(spec)
    print("=== Adapter output (first 600 chars) ===")
    print(text[:600])
    print("...")


if __name__ == "__main__":
    main()
