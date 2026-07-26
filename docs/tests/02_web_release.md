# テスト2: Confirmへ進めるケース — Webサービスのリリース判断

## テスト仕様（期待）

| 項目 | 期待 |
|------|------|
| Gate | **PASS** (`GATE_OK`) |
| Prediction | 許可（evidence=high ≥ medium） |
| LLM挙動 | リリース可否のみ回答／**次期バージョンには触れない** |

---

# PSS実行結果: Webサービスのリリース判断

## 入力

- **Title**: Webサービスのリリース判断
- **Main Mission** `[critical]`: 来週リリース可能か判断
- **Observation**: 実装100% / テスト95% / 致命的不具合0件 / 負荷試験完了 / レビュー完了
- **Scope**: in=リリース可否 / out=次期バージョン
- **PredictionPolicy**: `minimum_evidence=medium`
- **Phase**: `2_confirm`, `scope_agreed=true`

## 実行結果サマリー

| 項目 | 結果 |
|---|---|
| Evidence level | **high**（n=5） |
| 予測許可 | **True** |
| Gate | **True** |
| Gate code | `GATE_OK` |

リリース可否の判断は根拠付きで提示してよい。out_of_scope（次期バージョン）には触れない。
