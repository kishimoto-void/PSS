# PSS の使い方

PSS は **問題仕様書** です。自然言語解析エンジンではありません。

> 現在は dual-track です。  
> - **推奨（RC）**: `pss_single.py`（1.0.0-rc1）— Mission / PredictionPolicy / Gate 中心  
> - **安定パッケージ**: `from pss import ...`（0.9.0）— Objective / Goal 中心  
> 詳細は [ROADMAP.md](../ROADMAP.md) を参照。

## 思想（魔法の言葉ではない）

よくある「LLMが賢くなる魔法のプロンプト」とは違います。

> **問題を、LLMが最大限答えやすい形に整える。**

- 何を達成するか（Mission）
- 何が分かっていて、何が分かっていないか（Knowledge）
- どこまで予測してよいか（PredictionPolicy）
- どの範囲で答えるか（Scope）
- 今は聞いてよいか・進めてよいか（Gate）

を先に固定するので、後段の LLM は「曖昧な依頼を推測で埋める」負担が減り、持っている性能を回答に集中できます。

---

## 一般LLMへの渡し方（重要）

```python
# RC 推奨
from pss_single import compile_for_generic

prompt = compile_for_generic(spec, mode="balanced")  # 推奨（デフォルト）
# prompt = compile_for_generic(spec, mode="strict")  # 監査・再現向き
```

### mode

| mode | 内容 |
|------|------|
| **balanced** | 自然な導入文 + 核心のみ（Mission / 既知・未知 / 予測可否 / Gate）。周辺は1行。 |
| **strict** | 上記 + 詳細ポリシー + 機械可読ブロック。 |

### balanced の出力イメージ

```text
あなたは優秀な問題解決のパートナーです。
以下は、今回の問題をできるだけ正確・安全に扱うための短い仕様です。
推測で穴埋めせず、仕様に書かれた条件の範囲で答えてください。

【やること】会議までの完成可否を判断
【範囲内】完成可否判断
【範囲外・触れない】執筆
【分かっていること】
  - 会議は火曜
  - ...
【予測・断定】根拠は足りているので、判断してよい（確信度=high）。
【進行】確認済みの範囲で答えてよい。
```

核心として残しているもの:

- Unknown / Missing の区別
- 予測の根拠レベル
- Gate（進んでよいかの判定）

---

## 役割分担

```text
ユーザー（自然言語 or 構造化入力）
        │
        ▼
  [任意] LLM が PSS 入力形式へ整理
        │
        ▼
  PSS（ProblemBuilder / validate / Gate / PredictionPolicy）
        │
        ▼
  compile_for_generic → 実行側 LLM が仕様に従って回答
```

---

## パターン1: 人間が直接入力（RC / single-file）

```python
from pss_single import ProblemBuilder, validate, compile_for_generic

spec = (
    ProblemBuilder()
    .identity(title="中古車購入の判断")
    .main_mission(goal="3年以内に故障リスクが低い中古車を選ぶ", priority="critical")
    .knowledge(
        observation=["予算120万円", "通勤40km"],
        unknown=["修復歴", "整備記録"],
        missing=["修復歴", "整備記録"],
    )
    .add_sub_mission(kind="ask_missing", description="修復歴と整備記録を確認する", priority="high")
    .prediction_policy(minimum_evidence="high", when_uncertain="ask")
    .phase(phase="1_clarify")
    .build()
)

spec.run_gate()
print(compile_for_generic(spec, mode="balanced"))
```

---

## パターン2: LLM に PSS 形式へ整理してもらう

ユーザーは普通の文章だけ書きます。

> 通勤用に120万円くらいで中古車を探しています。毎日40km乗ります。修復歴はまだ分かりません。

### LLM への依頼例（コピー用）

```text
以下のユーザー文を、PSS の入力形式に整理してください。

【厳守】
- 推測しない。文中に無い事実を Observation に書かない。
- 不足・不明な点は Unknown / Missing に分類する。
- 出力は次の見出しだけを使う。

Title:
Main Mission:
Observation:
Unknown:
Missing:

ユーザー文:
「（ここにユーザーの文章）」
```

---

## まとめ

| よくある誤解 | PSS の立場 |
|--------------|------------|
| 魔法のプロンプトで賢くする | しない |
| 問題を答えやすい仕様に固定する | **する** |
| 不足は推測で埋める | **しない**（Gate / Prediction で止める） |

関連: [`pss_single.py`](../pss_single.py) · [docs/tests/](tests/README.md) · [ROADMAP.md](../ROADMAP.md)
