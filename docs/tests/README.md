# PSS Behavioral Tests (v1.0 RC)

LLMが「先回りしないか」「Gateで止まれるか」「PredictionPolicyを守れるか」を確認するテスト群です。

| # | ケース | 期待の要点 |
|---|--------|------------|
| [01](01_used_car.md) | 中古車購入の判断 | Gate BLOCK / 先回りで車種を勧めない |
| [02](02_web_release.md) | Webサービスリリース判断 | Gate PASS / Scope内のみ回答 |
| [03](03_stock_forecast.md) | 株価予測 | Gate PASS だが予測拒否 |
| [04](04_code_review.md) | Pythonコードレビュー | Scope逸脱しない |
| [05](05_chatgpt_comparison.md) | ChatGPT性能比較 | 根拠なしで断定しない / 追加情報を求める |

実行基盤: [`pss_single.py`](../../pss_single.py)（変更なし）

各ファイルに **テスト仕様** と **実行結果** を記載しています。

## 判定の読み方

- **Gate**: フェーズを次へ進めてよいか（仕様は変更しない）
- **PredictionQuality**: その時点で予測・断定してよいか（Gateとは独立）
- **Scope**: 回答範囲の境界（out_of_scope に触れない）
