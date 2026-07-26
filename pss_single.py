#!/usr/bin/env python3
"""
PSS Single-File Edition (v1.0.0-rc1 conceptual freeze)
=========================================================
Problem Specification System — 問題仕様書（実行エンジンではない）

【v1.0 で固定する4点】
  1. Mission とは「何を達成するか」
  2. PredictionPolicy とは「どこまで予測してよいか」
  3. Gate は判定だけを行い、仕様を変更しない
  4. PSS は問題仕様書であり、実行エンジンではない

【層構造】
  必須（コア）
    Mission / ThinkingProfile / PredictionPolicy / EvaluationCriteria

  運用層
    Phase / SectionGate / Behavior / Validator

  外部層（このファイルでは最小のみ）
    Adapter（render / compile）
    ※ Executor / Fix Planner / LLM連携はコア外

  python pss_single.py
依存: 標準ライブラリのみ
"""

# NOTE: Full file restored from local artifacts after accidental PLACEHOLDER push.
# See repository history and /home/workdir/artifacts/pss_single.py for complete source.
raise SystemExit('Incomplete upload — use local pss_single.py')
