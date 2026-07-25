# PSS — Problem Specification System

**Version**: 0.3

---

## これはAIではありません

PSS は AI ではありません。  
エージェントでもありません。  
推論エンジンでもありません。

**PSS は仕様書です。**

より正確には：

> PSS は「問題仕様書（Problem Specification）」を忠実に生成・再現するためのプログラムである。  
> それ以上でも、それ以下でもない。

- 問題を解かない
- 知識を補完しない
- 勝手に仮定を置かない
- Sub-Goal を生成しない
- 人格を持たない
- 学習しない

与えられた情報を、決められた構造に従って整理し、仕様書として出力する。  
それが PSS の唯一の仕事です。

---

## Core Principle

```text
PSS does not solve problems.
PSS defines problems.
PSS produces a Problem Specification.
Primary I/O is PLP Capsule.
```

---

## 何をするのか

入力として受け取った情報を、以下の構造に整えます。

| 項目 | 意味 |
|------|------|
| **Problem** | 問題そのもの |
| **Current State** | 現在の状態 |
| **Goal** | 目標状態 |
| **Difference** | 現在と目標の差分（縮小すべきもの） |
| **Constraint** | 必ず守る条件 |
| **Section Gate** | 必須情報が揃っているかの確認 |
| **Known** | 確定している事実 |
| **Unknown** | まだ分かっていない情報 |
| **Assumption** | 明示的に置いている仮定 |
| **Evaluation Axis** | 比較する際の優先基準 |
| **Tolerance** | 完全一致を要求しない許容範囲 |

この構造化された仕様書を、PLP Capsule として出力します。

---

## 何をしないのか

| しないこと | 理由 |
|------------|------|
| 推論・解決 | それは Reasoning Engine の仕事 |
| 知識の生成・補完 | 仕様書が勝手に事実を増やしてはいけない |
| Sub-Goal の提案 | 知識依存であり、PSS の知る世界ではない |
| Unknown を埋める | 不明なものは不明のまま残す |
| Assumption を Known に昇格 | 仮定と事実を混ぜない |
| 人格・ロールプレイ | 仕様書に人格は不要 |
| 学習・記憶 | 状態を持たない |

---

## PLP との関係

```text
PLP (Particle Language Protocol)
  └── 知能ゼロの共通規格（状態・制約・Capsule）
        │
        ▼
PSS (Problem Specification System)
  └── 問題を仕様書に構造化するプログラム
        │
        ▼
Adapter / Compiler
  └── 仕様書の読み方を各 LLM に伝える層
        │
        ▼
Reasoning Engine
  └── 実際に推論・提案を行う（GPT / Claude / Gemini / Local / Human）
```

PSS は PLP の上に乗る「仕様書生成レイヤー」です。  
PLP が状態を運び、PSS が問題を仕様化し、LLM が解く。  
それぞれの責務は重なりません。

---

## 使い方

```python
from pss import ProblemBuilder, to_capsule, from_capsule, compile_for_generic

# 1. 仕様書を組み立てる
spec = (
    ProblemBuilder()
    .title("仕事資料の作成")
    .goal(description="完成度の高い資料を提出する")
    .difference(description="素材 → 正式資料", gaps=["章立て", "数値裏付け"])
    .add_default_safety_constraints()
    .knowledge(
        known=["会議は火曜"],
        unknown=["引用形式"],
        assumption=["Wordは利用可能"],
    )
    .build()
)

# 2. PLP Capsule に載せる
capsule = to_capsule(spec)

# 3. Capsule から復元する
restored = from_capsule(capsule)

# 4. （必要なら）Adapter で LLM 向けに説明する
prompt = compile_for_generic(restored)
```

---

## テスト

```bash
python -m pytest pss/test_pss.py -v
```

結果: **17 passed**（詳細は [TEST_RESULTS.md](TEST_RESULTS.md)）

---

## 一言で言うと

> **PSS は仕様書であり、AI ではない。**  
> **仕様書を忠実に再現するためのプログラムである。**  
> **それ以上でも、それ以下でもない。**
