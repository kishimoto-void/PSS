# PSS Sequential Improvement Roadmap

実験は忠実に実際行って進める。

## Current State (2026-07-27)

- **Package (`pss/`)** : **v0.9.1**  
  - Core: Identity / Objective / **Mission** / Constraints / Scope / Knowledge / ThinkingProfile / **PredictionPolicy** / Behavior / Output / Evaluation / **EvaluationCriteria** / PhaseState / **Gate (diagnosis-only)**  
  - Validator + FixPlanner  
  - Public API + RC pillars coexisting  
  - **Test suite updated for 0.9.1 + Gate mutation check**

- **Single-file (`pss_single.py`)** : v1.0.0-rc1  
  - Pillars: Mission / ThinkingProfile / PredictionPolicy / EvaluationCriteria  
  - Gate (diagnosis only)

---

## Sequential Steps (優先順)

### Step 1 — Documentation & Dual-track Clarification (Done)
- [x] README に dual-track を明確化
- [x] ROADMAP.md 作成
- [x] USAGE.md を dual-track 対応に更新

### Step 2 — Package への RC 柱移植（互換性を保ちながら） (Done)
- [x] `Mission` / `SubMission` 構造を追加（Objective と並存）
- [x] `PredictionPolicy` を正式追加
- [x] `EvaluationCriteria` を追加（EvaluationAxis と並存）
- [x] Gate を diagnosis-only として `diagnose_gate()` / `run_gate()` を実装
- [x] Builder に `.main_mission()`, `.add_sub_mission()`, `.prediction_policy()` などを追加

### Step 3 — テストの最新化と忠実性強化 (Done)
- [x] pytest を 0.9.1 + RC 柱に合わせて更新
- [x] Gate / PredictionPolicy の「副作用なし」を `copy.deepcopy` で自動検証
- [x] Behavioral 寄りのケース（used-car 風 BLOCK、complete PASS など）を追加
- [x] Mission / PredictionPolicy / EvaluationCriteria の roundtrip テスト追加
- [ ] CI での実行確認（ユーザー側 or 次のアクション）

### Step 4 — Adapter / compile の統一
- package の `compile_for_generic` を RC の balanced/strict 形式に寄せる
- SPEC_EXPLANATION を簡潔化

### Step 5 — API 固定とクリーンアップ
- deprecated (`agent_role` など) の削除計画を明記
- `__all__` を厳格化
- schema version を 1.0 に向けて準備

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

Step 3 完了。次は **Step 4（Adapter 統一）** または ローカルで `pytest` を実行して確認。
