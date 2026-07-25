"""
PSS — Problem Specification System (v0.4)
=========================================
PLP 上に載せる問題仕様書生成レイヤー。

責務:
  - 問題を適切に定義・構造化する
  - PLP Capsule を主入出力とする
  - Phase 1→2→3 の一巡制御（プログラム側）

非責務:
  - 推論そのもの
  - 知識生成・補完
  - Sub-Goal の生成
  - 人格 / ロールプレイ
  - 学習 / 記憶 / 世界モデル
  - AI モデルの呼び出し

設計原則:
  PSS does not solve problems.
  PSS defines problems.
  PSS produces a Problem Specification.
  Primary I/O is PLP Capsule.
  Phase transitions are owned by the program, not the LLM.
  Interpretation instructions belong to the Adapter / Compiler layer.

Phase cycle:
  1 Clarify → 2 Confirm → 3 Answer  (one closed cycle)
  Definition-level failure → new_cycle() from Phase 1
"""

from .core import (
    Problem,
    CurrentState,
    Goal,
    Difference,
    ConstraintSpec,
    SectionGate,
    EvaluationAxis,
    Tolerance,
    KnowledgeState,
    ProblemSpecification,
)
from .builder import ProblemBuilder
from .transport import (
    from_capsule,
    to_capsule,
    from_plp_capsule,
    to_plp_capsule,
    problem_spec_to_dict,
    problem_spec_to_json,
    render_specification,
)
from .phase import (
    Phase,
    PhaseState,
    PhaseController,
    PHASE_RULES,
)
from .adapter import (
    compile_for_generic,
    compile_for_gpt,
    compile_for_claude,
    compile_for_gemini,
    compile_for_local,
    compile_phase_only,
)

__all__ = [
    # core
    "Problem",
    "CurrentState",
    "Goal",
    "Difference",
    "ConstraintSpec",
    "SectionGate",
    "EvaluationAxis",
    "Tolerance",
    "KnowledgeState",
    "ProblemSpecification",
    # builder
    "ProblemBuilder",
    # transport
    "from_capsule",
    "to_capsule",
    "from_plp_capsule",
    "to_plp_capsule",
    "problem_spec_to_dict",
    "problem_spec_to_json",
    "render_specification",
    # phase
    "Phase",
    "PhaseState",
    "PhaseController",
    "PHASE_RULES",
    # adapter
    "compile_for_generic",
    "compile_for_gpt",
    "compile_for_claude",
    "compile_for_gemini",
    "compile_for_local",
    "compile_phase_only",
]
