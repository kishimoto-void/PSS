"""
PSS Transport (v0.3)
====================
主入出力を PLP Capsule に統一する。

- 入力: Capsule → ProblemSpecification
- 出力: ProblemSpecification → Capsule

魔法のプロンプトはここには置かない。
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import time
from uuid import uuid4

from .core import (
    Problem,
    CurrentState,
    Goal,
    Difference,
    ConstraintSpec,
    SectionGate,
    EvaluationAxis,
    Tolerance,
    KnowledgeState,
    ProblemSpecification,
)


def problem_spec_to_dict(spec: ProblemSpecification) -> Dict[str, Any]:
    return spec.to_dict()


def problem_spec_to_json(spec: ProblemSpecification, indent: int = 2) -> str:
    return json.dumps(spec.to_dict(), ensure_ascii=False, indent=indent)


# ------------------------------------------------------------------
# Capsule → ProblemSpecification（主入力経路）
# ------------------------------------------------------------------

def from_capsule_dict(capsule: Dict[str, Any]) -> ProblemSpecification:
    """
    PLP Capsule 互換 dict から ProblemSpecification を復元する。

    優先順位:
      1. pss_payload / pgs_payload が存在する → それを正式仕様として使う
      2. それ以外 → header / input / observations から最小限の仕様を組み立てる
    """
    # 正式なペイロードがある場合
    payload = capsule.get("pss_payload") or capsule.get("pgs_payload")
    if isinstance(payload, dict) and payload.get("schema", "").startswith(("pss.", "pgs.")):
        return ProblemSpecification.from_dict(payload)

    # フォールバック: Capsule の基本情報から最小仕様を作る
    header = capsule.get("header") or {}
    inp = capsule.get("input") or {}
    meta = inp.get("metadata") or {}

    title = str(meta.get("title") or header.get("source") or "Untitled Problem")
    domain = str(meta.get("domain") or "")
    description = str(inp.get("raw_input") or meta.get("description") or "")

    known = list(meta.get("known") or [])
    unknown = list(meta.get("unknown") or [])
    assumption = list(meta.get("assumption") or [])

    return ProblemSpecification(
        problem=Problem(
            title=title,
            description=description,
            domain=domain,
        ),
        current_state=CurrentState(
            description=str(meta.get("current_state") or ""),
        ),
        goal=Goal(
            description=str(meta.get("goal") or ""),
        ),
        knowledge=KnowledgeState(
            known=known,
            unknown=unknown,
            assumption=assumption,
        ),
    )


def from_capsule(capsule: Dict[str, Any]) -> ProblemSpecification:
    """公開 API。Capsule dict を受け取り ProblemSpecification を返す。"""
    return from_capsule_dict(capsule)


# ------------------------------------------------------------------
# ProblemSpecification → Capsule（出力）
# ------------------------------------------------------------------

def to_capsule_dict(
    spec: ProblemSpecification,
    *,
    source: str = "PSS",
    clock: int = 0,
    sequence: int = 0,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """ProblemSpecification を PLP Capsule 互換 dict に載せる。"""
    payload = spec.to_dict()

    observation = {
        "name": "pss.problem_specification",
        "schema": "pss.problem_specification/0.3",
        "capability": "custom",
        "values": {},
        "clock": clock,
    }

    return {
        "header": {
            "protocol": "PLP/1.0",
            "capsule_schema": "capsule.v1",
            "version": "1.3",
            "capsule_id": str(uuid4()),
            "parent_id": parent_id,
            "clock": clock,
            "sequence": sequence,
            "timestamp": time.time(),
            "source": source,
            "flags": {
                "compressed": False,
                "encrypted": False,
                "partial": False,
                "realtime": True,
            },
        },
        "input": {
            "raw_input": None,
            "input_type": "pss.problem_specification",
            "metadata": {
                "pss_version": spec.version,
                "title": spec.problem.title,
                "domain": spec.problem.domain,
            },
            "reference": None,
        },
        "observations": [observation],
        "delta": {"changes": {}},
        "integrity": {
            "content_hash": None,
            "valid": True,
            "observer_valid": True,
            "hash_valid": None,
            "error": None,
        },
        "pss_payload": payload,
    }


def to_capsule(
    spec: ProblemSpecification,
    *,
    source: str = "PSS",
    clock: int = 0,
    sequence: int = 0,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    return to_capsule_dict(
        spec,
        source=source,
        clock=clock,
        sequence=sequence,
        parent_id=parent_id,
    )


# 互換エイリアス
to_plp_capsule = to_capsule
from_plp_capsule = from_capsule


def render_specification(spec: ProblemSpecification) -> str:
    """純粋な仕様書テキスト。命令は一切入れない。"""
    lines = [
        "=" * 60,
        "PROBLEM SPECIFICATION",
        f"schema : {spec.schema}",
        f"version: {spec.version}",
        "=" * 60,
        "",
        f"Title       : {spec.problem.title}",
        f"Domain      : {spec.problem.domain}",
        f"Description : {spec.problem.description}",
        "",
        "--- Current State ---",
        spec.current_state.description or "(none)",
        "",
        "--- Goal ---",
        spec.goal.description or "(none)",
    ]
    if spec.goal.success_criteria:
        lines.append("Success criteria:")
        for c in spec.goal.success_criteria:
            lines.append(f"  - {c}")

    lines.extend([
        "",
        "--- Difference ---",
        spec.difference.description or "(none)",
    ])
    if spec.difference.gaps:
        lines.append("Gaps:")
        for g in spec.difference.gaps:
            lines.append(f"  - {g}")

    if spec.constraints:
        lines.extend(["", "--- Constraints ---"])
        for c in sorted(spec.constraints, key=lambda x: -x.priority):
            lines.append(f"  [{c.kind}/{c.priority}] {c.statement}")

    if spec.section_gate:
        lines.extend(["", "--- Section Gate ---"])
        lines.append(f"Name     : {spec.section_gate.name}")
        lines.append(f"Complete : {spec.section_gate.is_complete}")
        if spec.section_gate.missing_fields:
            lines.append("Missing  :")
            for m in spec.section_gate.missing_fields:
                lines.append(f"  - {m}")

    lines.extend(["", "--- Knowledge ---"])
    if spec.knowledge.known:
        lines.append("Known:")
        for k in spec.knowledge.known:
            lines.append(f"  - {k}")
    if spec.knowledge.unknown:
        lines.append("Unknown:")
        for u in spec.knowledge.unknown:
            lines.append(f"  - {u}")
    if spec.knowledge.assumption:
        lines.append("Assumption:")
        for a in spec.knowledge.assumption:
            lines.append(f"  - {a}")

    if spec.evaluation_axis.axes:
        lines.extend(["", "--- Evaluation Axes ---"])
        for k, v in spec.evaluation_axis.axes.items():
            lines.append(f"  {k}: {v}")
        if spec.evaluation_axis.notes:
            lines.append(f"  notes: {spec.evaluation_axis.notes}")

    if spec.tolerance.description or spec.tolerance.quantitative or spec.tolerance.qualitative:
        lines.extend(["", "--- Tolerance ---"])
        if spec.tolerance.description:
            lines.append(spec.tolerance.description)
        for k, v in spec.tolerance.quantitative.items():
            lines.append(f"  {k}: ±{v}")
        for q in spec.tolerance.qualitative:
            lines.append(f"  - {q}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
