# PSS Sequential Improvement Roadmap

実験は忠実に実際行って進める。

## Current State (2026-07-27)

- **Package (`pss/`)** : **v0.9.1**  
  - Core + RC pillars (Mission / PredictionPolicy / EvaluationCriteria / Gate diagnosis-only)  
  - **Adapter**: `compile_for_generic(..., mode="balanced"|"strict")` 対応完了  
  - Test suite updated

- **Single-file (`pss_single.py`)** : v1.0.0-rc1

---

## Sequential Steps (優先順)

### Step 1 — Documentation & Dual-track Clarification (Done)
- [x] README / ROADMAP / USAGE 更新

### Step 2 — Package への RC 柱移植 (Done)
- [x] Mission / PredictionPolicy / EvaluationCriteria / Gate (diagnosis-only)
- [x] Builder 対応メソッド追加

### Step 3 — テストの最新化と忠実性強化 (Done)
- [x] pytest 更新 + Gate 副作用なし検証 + Behavioral ケース

### Step 4 — Adapter / compile の統一 (Done)
- [x] `compile_for_generic(spec, mode="balanced"|"strict")` を実装
- [x] balanced: 自然な導入 + Mission / Knowledge / Prediction / Gate 核心のみ
- [x] strict: 詳細説明 + フル render_specification + Gate 診断
- [x] 後方互換維持（mode 省略時は balanced）

### Step 5 — API 固定とクリーンアップ
- deprecated (`agent_role` など) の削除計画を明記
- `__all__` を厳格化
- schema version を 1.0 に向けて準備
- 既存テストの最終確認

### Step 6 — v1.0.0 リリース
- package と single-file を揃える
- タグ付け
- 非破壊的な互換性を可能な限り維持

---

## Principles for every step

1. **実験は忠実に実際行って** — 変更は必ずテストとログで検証する
2. Gate / Validator / Planner は **診断・計画のみ**（副作用をコアに入れない）
3. Observation / Inference / Assumption / Unknown / Missing の区別を崩さない
4. コアは軽量に保つ。Executor は外に出す
5. 破壊的変更は v2.0 まで延期

---

## Next Action

Step 4 完了。次は **Step 5（API 固定とクリーンアップ）**。
