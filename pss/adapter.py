"""
PSS Adapter / Compiler (v0.9.1)
===============================
Problem Specification（思考条件仕様）を各 Reasoning Engine 向けに解釈させる層。

RC 1.0-rc1 互換:
  - mode="balanced" (default): 自然な導入 + 核心のみ（Mission / 既知・未知 / 予測可否 / Gate）
  - mode="strict": 詳細ポリシー + 機械可読寄り

魔法のプロンプトは書かない。
思考条件の意味と、現在フェーズの許可範囲だけを伝える。
"""

from __future__ import annotations

from typing import Optional, Literal

from .core import ProblemSpecification, GateResult
from .transport import render_specification
from .phase import PhaseController


Mode = Literal["balanced", "strict"]


BALANCED_INTRO = """\
あなたは優秀な問題解決のパートナーです。
以下は、今回の問題をできるだけ正確・安全に扱うための短い仕様です。
推測で穴埋めせず、仕様に書かれた条件の範囲で答えてください。
""".strip()


STRICT_INTRO = """\
あなたは PSS (Problem Specification System) から生成された
「思考条件仕様書（Problem Specification）」を受け取ります。

これは「問題を解くための思考条件」を定義した仕様書です。
特定のモデルを制御するものではなく、人間・Agent・LLM が共有する共通の思考条件です。

ルール：
- Unknown や Missing を勝手に確定事実として扱わないでください。
- Assumption は「仮定」として明示的に扱ってください。
- 仕様書にない分析軸・スコア・フレームワークを追加しないでください。
- Thinking Profile と Behavior の指定に従って思考・応答してください。
- Gate の判定結果を尊重してください（diagnosis only）。
""".strip()


def _render_balanced(spec: ProblemSpecification, gate: Optional[GateResult] = None) -> str:
    """RC-style concise output."""
    lines = [BALANCED_INTRO, ""]

    # Mission / Goal
    mission_goal = spec.mission.goal or spec.objective.goal.description or "(未設定)"
    lines.append(f"【やること】{mission_goal}")

    if spec.mission.sub_missions:
        for sm in spec.mission.sub_missions:
            lines.append(f"  - [{sm.priority}] {sm.kind}: {sm.description}")

    # Scope
    if spec.scope.in_scope:
        lines.append(f"【範囲内】{', '.join(spec.scope.in_scope)}")
    if spec.scope.out_of_scope:
        lines.append(f"【範囲外・触れない】{', '.join(spec.scope.out_of_scope)}")

    # Knowledge
    if spec.knowledge.observation:
        lines.append("【分かっていること】")
        for o in spec.knowledge.observation:
            lines.append(f"  - {o}")

    unknowns = list(dict.fromkeys(spec.knowledge.unknown + spec.knowledge.missing))
    if unknowns:
        lines.append("【分かっていないこと / Missing】")
        for u in unknowns:
            lines.append(f"  - {u}")

    if spec.knowledge.assumption:
        lines.append("【仮定】")
        for a in spec.knowledge.assumption:
            lines.append(f"  - {a}")

    # PredictionPolicy
    pp = spec.prediction_policy
    pred_line = f"【予測・断定】minimum_evidence={pp.minimum_evidence}, when_uncertain={pp.when_uncertain}"
    if pp.allow_forward_looking:
        pred_line += " (forward-looking allowed)"
    lines.append(pred_line)

    # Gate (diagnosis)
    if gate is None:
        gate = spec.diagnose_gate()
    if gate.decision == "PASS":
        lines.append("【進行】確認済みの範囲で答えてよい。")
    elif gate.decision == "BLOCK":
        lines.append(f"【進行】BLOCK — {'; '.join(gate.reasons) or '不足情報あり'}")
    else:
        lines.append(f"【進行】ASK — {'; '.join(gate.reasons) or '確認が必要'}")

    # Behavior (brief)
    lines.append(f"【役割】{spec.behavior.role} / criticism={spec.behavior.criticism_level}")

    return "\n".join(lines)


def _render_strict(spec: ProblemSpecification, phase: Optional[PhaseController] = None) -> str:
    """Detailed output with full explanation + render_specification."""
    parts = [STRICT_INTRO]
    if phase is not None:
        parts.append("=" * 60)
        parts.append(phase.prompt_block())
        parts.append("=" * 60)
    parts.append(render_specification(spec))

    # Append Gate diagnosis
    gate = spec.diagnose_gate()
    parts.append("")
    parts.append("--- Gate Diagnosis (read-only) ---")
    parts.append(f"decision : {gate.decision}")
    if gate.reasons:
        parts.append("reasons  : " + "; ".join(gate.reasons))
    if gate.missing_required:
        parts.append("missing  : " + ", ".join(gate.missing_required))
    parts.append(gate.notes)

    return "\n\n".join(parts)


def compile_for_generic(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
    mode: Mode = "balanced",
) -> str:
    """
    汎用 Adapter (RC 1.0-rc1 互換)。

    mode:
      - "balanced" (default): 自然な導入 + 核心のみ
      - "strict": 詳細説明 + フル仕様 + Gate 診断

    後方互換: mode を省略すると balanced になる。
    旧呼び出し (phase のみ) も動作する。
    """
    if mode == "strict":
        return _render_strict(spec, phase)
    return _render_balanced(spec)


def compile_for_gpt(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
    mode: Mode = "balanced",
) -> str:
    return compile_for_generic(spec, phase, mode=mode)


def compile_for_claude(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
    mode: Mode = "balanced",
) -> str:
    return compile_for_generic(spec, phase, mode=mode)


def compile_for_gemini(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
    mode: Mode = "balanced",
) -> str:
    return compile_for_generic(spec, phase, mode=mode)


def compile_for_local(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
    mode: Mode = "balanced",
) -> str:
    return compile_for_generic(spec, phase, mode=mode)


def compile_phase_only(phase: PhaseController) -> str:
    """仕様書なしで、フェーズ制約だけを返す（テスト・デバッグ用）。"""
    return phase.prompt_block()
