# PSS Experiment Log

このドキュメントは、PSS が「プロンプト寄りの仕様書」から「思考条件を定義する共通仕様」へ進化した実験過程をまとめたものです。

---

## 1. 出発点

初期のPSSは、問題を構造化してLLMに渡すための軽量な仕様層として始まった。

主な関心は以下だった：

- Problem / Goal / Difference / Constraint
- Known / Unknown / Assumption
- Capsule への載せる・復元する
- Adapter でLLM向けテキストを生成する

この時点では「良いプロンプトを作るための構造化」に近かった。

---

## 2. 転機：思考条件という捉え方

実験を進める中で、PSSの本質は「LLMを制御するプロンプト」ではなく、

> **人間・Agent・LLMが共有する思考条件の仕様**

であるという認識に到達した。

これにより設計方針が明確になった：

- 特定のモデルに依存しない
- 実装詳細を持ち込まない
- 「どう考えるか」を定義し、「何を答えるか」は残さない

---

## 3. 主な設計進化

### v0.5 — 構造の拡大と正式化

- Identity / Objective / Constraints / Scope / Knowledge をコアとして強化
- ThinkingProfile / AgentRole / Output を正式追加
- Audience / Confidence / Interaction / Criticism を拡張オプションとして用意

### v0.6 — 実行規則への転換

最大の転換点は「宣言」から「行動規則」への移行だった。

```yaml
rules:
  if_unknown: answer_unknown
  if_assumption: mark_assumption
  if_scope_violation: stop
  if_missing_required: ask
  if_low_confidence: state_confidence
```

これにより：

- モデルごとの解釈差が減る
- Agentが迷いにくくなる
- 「Role」だけではなく「具体的な振る舞い」が定義できる

あわせて Knowledge を以下に分離した：

- Observation（観測）
- Inference（推論）
- Assumption（仮定）
- Unknown / Missing

「観測 → 推論」を無意識に飛び越える問題への対策として有効だった。

PhaseState を Specification 本体に統合したことで、Capsule 単体で現在状態を完結できるようになった。

### v0.7 — 診断と計画の分離

Validator と Fix Planner を導入した。

```
Specification
      │
      ▼
  Validator          ← 診断のみ（修正しない）
      │
      ▼
   Findings
      │
      ▼
  Fix Planner        ← 修正計画を生成（副作用なし）
      │
      ▼
   Fix Plan
      │
      ▼
 Executor（コア外）
```

重要な判断：

- Validator は仕様を変更しない
- Fix Planner も仕様を変更しない
- 実行主体（人間 / LLM / IDE / CI）はコアに含めない

これにより責務が明確に分離された。

---

## 4. 現在のレイヤー構成

| Layer            | 責務                                       |
|------------------|--------------------------------------------|
| Specification    | 何を定義するか                             |
| Builder          | どう組み立てるか                           |
| Adapter          | どうLLMへ渡すか                            |
| Validator        | 何が問題か（診断）                         |
| Fix Planner      | どう直すか（計画）                         |

Executor / CLI / IDE 拡張はコアに入れず、必要に応じて別パッケージとする方針を採用した。

---

## 5. テスト結果（v0.7時点）

包括的なテストスイートを整備し、以下を確認した：

- Builder の各フィールド構築
- Knowledge 全カテゴリの独立性
- Behavior rules の設定と復元
- PhaseState の保持
- to_dict / from_dict 往復
- Validator の ERROR / WARN 検出
- Fix Planner の計画生成と priority 順
- Adapter への Behavior 反映
- 空仕様や全タイプ同時投入などのエッジケース

**結果: 17 passed**

---

## 6. 設計上の重要な判断まとめ

1. **PSSはプロンプトではない**  
   思考条件の仕様である。

2. **宣言より行動規則**  
   Role だけではなく `if_…` ルールを持つ。

3. **Observation と Inference を分ける**  
   先回りを抑制する中核。

4. **Validator は診断に徹する**  
   修正はしない。

5. **Fix Planner は計画だけを返す**  
   実行は呼び出し側に委ねる。

6. **コアは軽量に保つ**  
   Executor などの実行系は外に出す。

7. **今は安定化フェーズ**  
   機能追加より、API固定・命名統一・テスト・サンプルの充実を優先する。

---

## 7. 今後の方向（v1.0に向けて）

- 公開APIの固定
- 命名の統一
- READMEの継続的な改善
- サンプルの追加
- テストのさらなる充実

大きな機能追加は慎重に行い、必要な場合は衛星パッケージとして切り出す。

---

## 8. 結論

PSSは「問題を構造化してLLMに渡す道具」から始まり、

**人間・Agent・LLMが同じ思考条件を共有するための仕様ライブラリ**

へと進化した。

現在の構成（Specification / Builder / Adapter / Validator / Fix Planner）は、責務が明確で拡張しやすい。

このまま安定化を進めることで、長期的に依存できる基盤になると考えている。
