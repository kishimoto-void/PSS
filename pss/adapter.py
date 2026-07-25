"""
PSS Adapter / Compiler (v0.4)
=============================
Problem Specification を各 Reasoning Engine 向けに解釈させる層。

フェーズ制約はプログラム側（PhaseController）が持つ。
魔法のプロンプトは書かない。
データ構造の意味と、現在フェーズの許可範囲だけを伝える。
"""

from __future__ import annotations

from typing import Optional

from .core import ProblemSpecification
from .transport import render_specification
from .phase import PhaseController, PhaseState, Phase


SPEC_EXPLANATION = """\
あなたは PSS (Problem Specification System) から生成された
Problem Specification を受け取ります。

これは「問題を構造化した仕様書」です。
各項目には以下の役割があります。

- Goal
  目標状態

- Difference
  現在状態と目標状態の差異（縮小すべきもの）

- Constraint
  必ず守る条件（hard は絶対）

- Section Gate
  必須情報が揃っているかの確認結果
  Missing がある場合は、まずそれを埋める必要がある

- Known
  確定している事実

- Unknown
  まだ分かっていない情報（勝手に埋めない）

- Assumption
  現時点で置いている仮定（明示的に扱ってよい範囲）

- Evaluation Axis
  提案を比較する際の優先基準

- Tolerance
  完全一致を要求しない許容範囲

Unknown を勝手に確定事実として扱わないでください。
Assumption は明示した仮定として扱ってください。
仕様書にない分析軸・スコア・フレームワークを追加しないでください。
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
