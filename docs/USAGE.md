# PSS の使い方

PSS は **問題仕様書** です。自然言語解析エンジンではありません。

## 思想（魔法の言葉ではない）

よくある「LLMが賢くなる魔法のプロンプト」とは違います。

PSS がやることは次です。

> **問題を、LLMが最大限答えやすい形に整える。**

- 何を達成するか（Mission）
- 何が分かっていて、何が分かっていないか（Knowledge）
- どこまで予測してよいか（PredictionPolicy）
- どの範囲で答えるか（Scope）
- 今は聞いてよいか・進めてよいか（Gate）

を先に固定するので、後段の LLM は「曖昧な依頼を推測で埋める」負担が減り、持っている性能を回答に集中できます。

賢く見せるための呪文ではなく、**答えやすい問題定義**です。

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
  実行側 LLM が仕様に従って回答
```

| 役割 | 担当 |
|------|------|
| 自然言語 → PSS 入力への変換（推測禁止） | 前段 LLM または人間 |
| 仕様の検証・Gate・予測許可 | **PSS** |
| 仕様に従った回答 | 後段 LLM |

---

## パターン1: 人間が直接入力

すでに整理できている場合は、そのまま構造化して `ProblemBuilder` に渡します。

```text
Title: 中古車購入の判断

Main Mission:
  3年以内に故障リスクが低い中古車を選ぶ

Observation:
  - 予算120万円
  - 通勤40km

Unknown:
  - 修復歴
  - 整備記録
```

```python
from pss_single import ProblemBuilder, validate  # または from pss import ...

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

print(validate(spec).summary())
print(spec.run_gate().codes)
```

---

## パターン2: LLM に PSS 形式へ整理してもらう

ユーザーは普通の文章だけ書きます。

> 通勤用に120万円くらいで中古車を探しています。毎日40km乗ります。修復歴はまだ分かりません。

### LLM への依頼例（コピー用）

```text
以下のユーザー文を、PSS（Problem Specification System）の入力形式に整理してください。

【厳守】
- 推測しない。文中に無い事実を Observation に書かない。
- 不足・不明な点は Unknown / Missing に分類する。
- Goal が曖昧なら、文意の範囲で最短の Main Mission にする。
- 出力は次の見出しだけを使う（説明文は不要）。

Title:
Main Mission:
Success Criteria:（任意）
Observation:
Inference:（任意・観測から明示的に導ける場合のみ）
Assumption:（任意・仮定と明示できる場合のみ）
Unknown:
Missing:
Scope in:（任意）
Scope out:（任意）
SubMission:（任意・kind と priority）

ユーザー文:
「（ここにユーザーの文章）」
```

### 期待される整理例

```text
Title:
中古車購入の判断

Main Mission:
3年以内に故障リスクが低い中古車を選ぶ

Observation:
- 予算120万円
- 毎日40km走行

Unknown:
- 修復歴
- 整備記録

Missing:
- 修復歴証明
- 整備記録簿
```

この出力を人間または小さなパーサで `ProblemBuilder` に流し込みます。

---

## プログラムを渡して「この枠で整理して」と頼む

`pss_single.py` を貼ったうえで、次のように依頼しても構いません。

```text
この PSS プログラム（pss_single.py）を使った問題解決の枠組みで考えたい。
次の文章を、ProblemBuilder に渡せる形（Title / Main Mission / Observation / Unknown / Missing 等）に整理して。
推測は禁止。足りない情報は Unknown/Missing へ。

文章:
「……」
```

PSS 自身は自然言語を解釈しません。LLM が「入力の整形」を担当し、PSS が「仕様としての判定」を担当します。

---

## 後段 LLM（回答側）への渡し方

`compile_for_generic(spec)` または `render_specification(spec)` の出力を、回答用 LLM に渡します。

```text
あなたは PSS の問題仕様書に従って回答してください。
Gate が BLOCK なら先に進まず、足りない情報を聞いてください。
Prediction が不許可なら断定せず、when_uncertain に従ってください。
Scope 外には触れないでください。

（ここに compile_for_generic の出力）
```

ここで効くのは「魔法の一文」ではなく、**すでに整理された Mission / Knowledge / Policy / Gate** です。LLM は推測の余地が減り、答えやすい条件のうえで性能を出せます。

---

## まとめ

| よくある誤解 | PSS の立場 |
|--------------|------------|
| 魔法のプロンプトで賢くする | しない |
| LLM に「よく考えて」と言う | しない |
| 問題を答えやすい仕様に固定する | **する** |
| 不足は聞かず推測で埋める | **しない**（Gate / Prediction で止める） |

「このコードに沿うように問題入力を作って」と LLM に頼む運用は、この思想と一致しています。

関連:
- 単一ファイル: [`pss_single.py`](../pss_single.py)
- 振る舞いテスト: [`docs/tests/`](tests/README.md)
