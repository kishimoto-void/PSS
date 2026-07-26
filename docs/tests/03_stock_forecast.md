# テスト3: Prediction拒否 — 株価予測

## テスト仕様（期待）

| 項目 | 期待 |
|------|------|
| Gate | **PASS**（フェーズは進める） |
| Prediction | **不許可**（evidence=low < high） |
| LLM挙動 | 来月の株価を断定しない／`state_unknown`／追加情報を列挙 |

ポイント: **Gate と Prediction は別レイヤー**

---

# PSS実行結果: 株価予測

## 入力

- **Title**: 株価予測
- **Main Mission** `[critical]`: 来月の株価を予測する
- **Observation**: 今日の株価だけ
- **PredictionPolicy**: `minimum_evidence=high`, `allow_prediction=true`, `when_uncertain=state_unknown`
- Phase: `1_clarify`

## 実行結果サマリー

| 項目 | 結果 |
|---|---|
| Evidence level | **low**（n=1） |
| 予測許可 | **False** |
| Gate | **True** |
| Gate code | `GATE_OK` |

次フェーズには進めるが、「来月の株価はいくら」という断定は禁止。observation を増やすか「現時点では予測できない」と回答する。
