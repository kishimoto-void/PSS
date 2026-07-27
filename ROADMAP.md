# PSS Sequential Improvement Roadmap

実験は忠実に実際行って進める。

## Current State (2026-07-27)

- **Package (`pss/`)** : **v0.9.1** (Step 2 in progress)  
  - Core: Identity / Objective (Goal + CurrentState + Difference) / **Mission** / Constraints / Scope / Knowledge / ThinkingProfile / **PredictionPolicy** / Behavior / Output / Evaluation / **EvaluationCriteria** / PhaseState / **Gate (diagnosis-only)**  
  - Validator + FixPlanner 完成度高  
  - Public API freeze candidate + RC pillars coexisting

- **Single-file (`pss_single.py`)** : v1.0.0-rc1  
  - Pillars: **Mission** (Main/Sub) / ThinkingProfile / **PredictionPolicy** / **EvaluationCriteria**  
  - Gate (diagnosis only) / Phase / Behavior  
  - `compile_for_generic(mode="balanced"|"strict")`

両者は思想は一致。package 側に RC 柱を非破壊追加した。

---

## Sequential Steps (優先順)

### Step 1 — Documentation & Dual-track Clarification (Done)
- [x] README に dual-track を明確化
- [x] ROADMAP.md 作成
- [x] USAGE.md を dual-track 対応に更新

### Step 2 — Package への RC 柱移植（互換性を保ちながら） (In Progress)
- [x] `Mission` / `SubMission` 構造を追加（Objective と並存）
- [x] `PredictionPolicy` を正式追加
- [x] `EvaluationCriteria` を追加（EvaluationAxis と並存）
- [x] Gate を diagnosis-only として `diagnose_gate()` / `run_gate()` を実装
- [x] Builder に `.main_mission()`, `.add_sub_mission()`, `.prediction_policy()` などを追加
- [ ] 既存テストが通ることを確認
- [ ] Adapter / compile の更新（Step 4 と連携）

### Step 3 — テストの最新化と忠実性強化
- pytest を 0.9.1 + RC 柱に合わせて更新
- Behavioral tests (docs/tests) を pytest に統合
- Gate / PredictionPolicy の「副作用なし」を自動検証
- multi-seed / different Knowledge 構成での挙動確認

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

Step 2 のコード追加は完了。次は既存テストの確認と Step 3（テスト強化）へ。
