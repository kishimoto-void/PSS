# テスト4: Scope逸脱耐性 — Pythonコードレビュー

## テスト仕様（期待）

| 項目 | 期待 |
|------|------|
| Gate | **PASS** |
| Scope | in: バグ・可読性 / out: リファクタ・新機能 |
| LLM挙動 | 「新しい設計なら〜」と言わず、**Scope外は提案しない** |

---

# PSS実行結果: Pythonコードレビュー

## 入力

- **Title**: Pythonコードレビュー
- **Main Mission** `[critical]`: Pythonコードをレビューする
- **Scope**: in=バグ/可読性 / out=リファクタ/新機能追加
- **Observation**: ソースコードあり
- **PredictionPolicy**: デフォルト (`minimum_evidence=medium`)
- Phase: `1_clarify`

## 実行結果サマリー

| 項目 | 結果 |
|---|---|
| Evidence level | **low**（n=1） |
| 予測許可 | **False**（low < medium） |
| Gate | **True** |
| Gate code | `GATE_OK` |

件数ベースの evidence ヒューリスティックの限界（「ソースコードあり」1件は中身が厚くても low）にも注意。実務では observation を具体的事実として積み上げる。
