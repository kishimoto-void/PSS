# テスト5: 実戦（厳しい）— ChatGPTの性能比較

## テスト仕様（期待）

| 項目 | 期待 |
|------|------|
| Gate | **BLOCK** (`GATE_KNOWLEDGE_EMPTY`) |
| Prediction | 不許可（evidence=none < high） |
| LLM挙動 | 用途を尋ねる／「最強」と断言しない／Evaluation（正確性・根拠・公平性）に沿う |

曖昧な質問例: 「Gemini・Claude・ChatGPTのどれが一番優秀？」

---

# PSS実行結果: ChatGPTの性能比較

## 入力

- **Title**: ChatGPTの性能比較
- **Main Mission** `[critical]`: ChatGPTの性能を比較する
- **SubMission**（すべて normal=省略可）: alternatives / risk_scan / ask_missing
- **ThinkingProfile**: stance=analytical / perspective=reviewer
- **PredictionPolicy**: `minimum_evidence=high`
- **EvaluationCriteria**: 正確性 0.5 / 根拠 0.3 / 公平性 0.2
- Phase: `1_clarify`
- **Knowledge: 未指定**（observation / unknown なし）

## 実行結果サマリー

| 項目 | 結果 |
|---|---|
| Evidence level | **none**（n=0） |
| 予測許可 | **False** |
| Gate | **False** |
| Gate code | `GATE_KNOWLEDGE_EMPTY` |
| ブロック理由 | observation も unknown も無い |

比較対象・比較軸が無い状態では断定不可。Gate を通すには最低限の unknown（比較対象・軸）や observation が必要。
