# Deprecations & Compatibility Plan

実験は忠実に実際行って、破壊的変更は最小限に抑える。

## Current (v0.9.1)

以下は **引き続き動作** しますが、v1.0 以降は非推奨、v2.0 で削除予定です。

| Symbol / Method | Preferred replacement | Removal target |
|-----------------|-----------------------|----------------|
| `ProblemBuilder.agent_role(...)` | `.behavior(role=..., role_description=...)` | v2.0 |
| `EvaluationAxis` | `EvaluationCriteria` | v2.0 |
| Heavy reliance on `Objective` only | Prefer `Mission` (+ keep Objective for compatibility) | — (Objective remains) |
| Old long `SPEC_EXPLANATION` | `compile_for_generic(..., mode="balanced")` | already replaced |

## Policy

1. **v0.9.x / v1.x** : 後方互換を可能な限り維持
2. **v2.0** : 上記 deprecated を削除可能
3. Gate / Validator / Planner は今後も **診断・計画のみ**（副作用なし）
4. Observation / Inference / Assumption / Unknown / Missing の区別は崩さない

## Schema

- Current: `pss.problem_specification/0.9`
- Target for v1.0: `pss.problem_specification/1.0`（非破壊的な拡張）

## Notes for users

- 新しいコードは `Mission` + `PredictionPolicy` + `EvaluationCriteria` + `mode="balanced"` を推奨
- 既存の `Objective` / `EvaluationAxis` / `agent_role` を使っているコードは当面そのまま動く
