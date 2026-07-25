"""
PSS Adapter / Compiler (v0.5)
=============================
Problem Specification（思考条件仕様）を各 Reasoning Engine 向けに解釈させる層。

フェーズ制約はプログラム側（PhaseController）が持つ。
魔法のプロンプトは書かない。
思考条件の意味と、現在フェーズの許可範囲だけを伝える。
"""

from __future__ import annotations

from typing import Optional

from .core import ProblemSpecification
from .transport import render_specification
from .phase import PhaseController


SPEC_EXPLANATION = """\
あなたは PSS (Problem Specification System) から生成された
「思考条件仕様書（Problem Specification）」を受け取ります。

これは「問題を解くための思考条件」を定義した仕様書です。
特定のモデルを制御するものではなく、人間・Agent・LLM が共有する共通の思考条件です。

各項目の役割：

【Identity】
- Title / Domain / Description : 問題の識別情報

【Objective】
- Goal : 目標状態
- Current State : 現在の状態
- Difference : 現在と目標の差分（縮小すべきもの）
- Success Criteria : 成功の判断基準

【Constraints】
- Hard : 必ず守る絶対条件
- Soft : 望ましいが破っても致命的ではない条件
- Assumptions : 明示的に置いている仮定
- Risks : 注意すべきリスク

【Scope】
- In Scope / Out of Scope / Priority / Allowed Changes

【Knowledge】
- Known : 確定している事実
- Unknown / Missing : まだ分かっていない情報（勝手に埋めない）
- Assumption : 仮定（明示的に扱う）
- References : 参照情報

【Thinking Profile】
- Reasoning Bias : 思考の偏り（balanced / engineering / scientific など）
- Depth : quick / normal / deep
- Evidence Policy : observation_first / allow_assumption / strict_evidence

【Agent Role】
- Collaborator（壁打ち） / Reviewer / Challenger / Supporter / Teacher / Analyst / Mediator など

【Output】
- Format / Style / Length / Language / Required Sections

【Evaluation】
- Accuracy / Safety / Clarity / Speed などの優先軸

【Extensions】
- Audience / Confidence Policy / Interaction Policy / Criticism Level

ルール：
- Unknown や Missing を勝手に確定事実として扱わないでください。
- Assumption は「仮定」として明示的に扱ってください。
- 仕様書にない分析軸・スコア・フレームワークを追加しないでください。
- Thinking Profile と Agent Role の指定に従って思考・応答してください。
"""


def compile_for_generic(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
) -> str:
    """
    汎用 Adapter。
    phase を渡すと、現在フェーズの許可/禁止を先頭に付与する。
    """
    parts = [SPEC_EXPLANATION.strip()]
    if phase is not None:
        parts.append("=" * 60)
        parts.append(phase.prompt_block())
        parts.append("=" * 60)
    parts.append(render_specification(spec))
    return "\n\n".join(parts)


def compile_for_gpt(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
) -> str:
    return compile_for_generic(spec, phase)


def compile_for_claude(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
) -> str:
    return compile_for_generic(spec, phase)


def compile_for_gemini(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
) -> str:
    return compile_for_generic(spec, phase)


def compile_for_local(
    spec: ProblemSpecification,
    phase: Optional[PhaseController] = None,
) -> str:
    return compile_for_generic(spec, phase)


def compile_phase_only(phase: PhaseController) -> str:
    """仕様書なしで、フェーズ制約だけを返す（テスト・デバッグ用）。"""
    return phase.prompt_block()
