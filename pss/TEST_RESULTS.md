# PSS Test Results

**Date**: 2026-07-25  
**Version**: 0.3  
**Environment**: Python 3.12.3 / pytest 9.0.3  
**Command**: `python -m pytest pss/test_pss.py -v`

---

## Summary

| Item | Value |
|------|-------|
| Total tests | 17 |
| Passed | 17 |
| Failed | 0 |
| Skipped | 0 |
| Duration | 1.76s |
| Result | **ALL PASSED** |

---

## Test Groups

### 1. TestProblemBuilder (3)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_basic_build` | PASSED | title / domain / goal / gaps / constraints が正しく構築される |
| `test_version_and_schema` | PASSED | version=`0.3`, schema が `pss.problem_specification` で始まる |
| `test_summary_contains_key_fields` | PASSED | summary() にタイトル・MISSING・Assumption が含まれる |

### 2. TestKnowledgeState (3)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_explicit_knowledge` | PASSED | Known / Unknown / Assumption が正しく分離されている |
| `test_section_gate_missing_merged_into_unknown` | PASSED | SectionGate の missing が Unknown に自動反映される |
| `test_assumption_is_separate_from_known` | PASSED | Assumption が Known に混入しない |

### 3. TestSectionGate (2)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_incomplete_when_missing` | PASSED | 不足がある場合 `is_complete=False` と missing リストが正しい |
| `test_complete_when_all_present` | PASSED | 全て揃っている場合 `is_complete=True` |

### 4. TestCapsuleTransport (2)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_to_capsule_and_from_capsule_roundtrip` | PASSED | Capsule 往復で title / gaps / knowledge / version が完全復元される |
| `test_from_capsule_fallback_without_payload` | PASSED | pss_payload が無い Capsule でも最低限の仕様が作れる |

### 5. TestConstraints (2)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_default_safety_constraints_present` | PASSED | 「推測しない」「不可能なこと」「社外秘」などの安全制約が含まれる |
| `test_priority_ordering` | PASSED | priority ≥ 20 の制約が正しく設定されている |

### 6. TestSerialization (2)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_to_dict_from_dict_roundtrip` | PASSED | to_dict → from_dict で主要フィールドが復元される |
| `test_schema_version_in_dict` | PASSED | dict 内に正しい schema / version が含まれる |

### 7. TestAdapter (1)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_compile_contains_explanation_and_spec` | PASSED | 説明文（Unknown / Assumption）と仕様本体の両方が含まれる |

### 8. TestEdgeCases (2)

| Test | Result | What it verifies |
|------|--------|------------------|
| `test_empty_builder` | PASSED | 空の Builder でも例外なく仕様が生成される |
| `test_no_section_gate` | PASSED | SectionGate なしでも正常に動作する |

---

## Key Design Verifications

以下の設計意図がテストで確認できている：

1. **PSS は推論しない**  
   - Sub-Goal 生成ロジックは存在せず、テスト対象外（意図的）

2. **Known / Unknown / Assumption の分離**  
   - Assumption が Known に混入しないことを明示的に検証

3. **Capsule が主入出力**  
   - Round-trip テストで完全性を確認
   - payload なしのフォールバックも動作

4. **SectionGate → Unknown の自動反映**  
   - missing 項目が knowledge.unknown に入ることを確認

---

## Conclusion

PSS v0.3 のコア機能はすべて正常に動作している。  
特に Capsule 往復と Knowledge triad の分離が安定している点を確認した。

```
17 passed in 1.76s
```
