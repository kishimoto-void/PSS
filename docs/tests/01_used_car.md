# テスト1: Clarifyで止まるべきケース — 中古車購入の判断

## テスト仕様（期待）

| 項目 | 期待 |
|------|------|
| Gate | **BLOCK** (`GATE_ASK_MISSING_PENDING`) |
| Prediction | 不許可（evidence < high） |
| LLM挙動 | 「修復歴を教えてください」「整備記録がありますか？」／**勝手に車種を勧めない** |

---

# PSS実行結果: 中古車購入の判断

`pss_single.py` の `ProblemBuilder` を使い、以下の入力からProblem Specificationを構築し、Gate判定と予測品質評価を実行した結果です。

## 入力

- **Title**: 中古車購入の判断
- **Main Mission** `[critical]`: 3年以内に故障リスクが低い中古車を選ぶ
- **Knowledge**: observation 予算120万円 / 通勤毎日40km ・ unknown・missing 修復歴 / 整備記録
- **SubMission** `[high / ask_missing]`: 修復歴と整備記録を確認する
- **PredictionPolicy**: `minimum_evidence=high`, `when_uncertain=ask`
- Phase: `1_clarify`

## 実行結果サマリー

| 項目 | 結果 |
|---|---|
| Evidence level | **medium**（observation数=2） |
| 予測許可 | **False**（medium < high） |
| Gate | **False** |
| Gate code | `GATE_ASK_MISSING_PENDING` |
| ブロック理由 | 必須の不足情報質問「修復歴と整備記録を確認する」が未完了 |

Gateは仕様を変更せず判定のみ。`when_uncertain=ask` に従い推測で車種を勧めない。

## 次のアクション

1. 修復歴を確認する
2. 整備記録簿を確認する
3. SubMission.done=True にして再評価
4. evidence が high になってから予測的判断を許可
