# PSS Sequential Improvement Roadmap

実験は忠実に実際行って進める。

## Current State (2026-07-27)

- **Package (`pss/`)** : **v0.9.1**  
  - RC pillars + Gate diagnosis-only + balanced/strict Adapter  
  - Public API tightened  
  - CHANGELOG / RELEASE_NOTES_0.9.1 / DEPRECATIONS 整備済み

- **Single-file** : v1.0.0-rc1

---

## Sequential Steps

### Step 1 — Documentation & Dual-track Clarification (Done)
### Step 2 — Package への RC 柱移植 (Done)
### Step 3 — テストの最新化と忠実性強化 (Done)
### Step 4 — Adapter / compile の統一 (Done)
### Step 5 — API 固定とクリーンアップ (Done)
### Step 6 — v1.0.0 / 0.9.1 リリース準備 (Done)
- [x] CHANGELOG.md 作成
- [x] RELEASE_NOTES_0.9.1.md 作成
- [x] DEPRECATIONS.md 整備
- [x] README / ROADMAP 最終更新
- [ ] PR レビュー & マージ（ユーザー作業）
- [ ] タグ `v0.9.1` 作成（ユーザー作業）

---

## Principles

1. **実験は忠実に実際行って**
2. Gate / Validator / Planner は **診断・計画のみ**
3. Observation / Inference / Assumption / Unknown / Missing の区別を崩さない
4. コアは軽量に保つ
5. 破壊的変更は v2.0 まで延期

---

## Next Actions (for maintainer)

1. PR #1 をレビューしてマージ
2. 必要なら `git tag v0.9.1` を打つ
3. さらに single-file との完全揃えを進める場合は次のイテレーション
