# PSS Sequential Improvement Roadmap

実験は忠実に実際行って進める。

## Current State (2026-07-27)

- **Package (`pss/`)** : **v0.9.1**  
  - RC pillars + Gate diagnosis-only + balanced/strict Adapter  
  - Public API tightened toward v1.0  
  - Deprecations documented (`DEPRECATIONS.md`)

- **Single-file** : v1.0.0-rc1

---

## Sequential Steps

### Step 1 — Documentation & Dual-track Clarification (Done)
### Step 2 — Package への RC 柱移植 (Done)
### Step 3 — テストの最新化と忠実性強化 (Done)
### Step 4 — Adapter / compile の統一 (Done)
### Step 5 — API 固定とクリーンアップ (Done)
- [x] `__all__` を厳格化（Public API を明確化）
- [x] deprecated 一覧を `DEPRECATIONS.md` に記載
- [x] `agent_role` → `behavior` への移行を明記
- [x] schema / version を v1.0 に向けて準備（現状 0.9.1）

### Step 6 — v1.0.0 リリース準備
- package と single-file の最終揃え
- タグ付け
- CHANGELOG / RELEASE_NOTES の整備
- 非破壊的な互換性の最終確認

---

## Principles

1. **実験は忠実に実際行って**
2. Gate / Validator / Planner は **診断・計画のみ**
3. Observation / Inference / Assumption / Unknown / Missing の区別を崩さない
4. コアは軽量に保つ
5. 破壊的変更は v2.0 まで延期

---

## Next Action

Step 5 完了。次は **Step 6（v1.0.0 リリース準備）** または PR のレビュー・マージ。
