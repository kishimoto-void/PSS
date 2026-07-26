"""
PSS Transport (v0.7)
====================
主入出力を PLP Capsule に統一する。
v0.7 構造に対応。
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import time
from uuid import uuid4

from .core import ProblemSpecification


def problem_spec_to_dict(spec: ProblemSpecification) -> Dict[str, Any]:
    return spec.to_dict()


def problem_spec_to_json(spec: ProblemSpecification, indent: int = 2) -> str:
    return json.dumps(spec.to_dict(), ensure_ascii=False, indent=indent)


def from_capsule_dict(capsule: Dict[str, Any]) -> ProblemSpecification:
    payload = capsule.get("pss_payload") or capsule.get("pgs_payload")
    if isinstance(payload, dict) and (
        payload.get("schema", "").startswith(("pss.", "pgs.")) or "identity" in payload or "objective" in payload
    ):
        return ProblemSpecification.from_dict(payload)

    header = capsule.get("header") or {}
    inp = capsule.get("input") or {}
    meta = inp.get("metadata") or {}

    from .core import Identity, KnowledgeState

    return ProblemSpecification(
        identity=Identity(
            title=str(meta.get("title") or header.get("source") or "Untitled Problem"),
            domain=str(meta.get("domain") or ""),
            description=str(inp.get("raw_input") or meta.get("description") or ""),
        ),
        knowledge=KnowledgeState(
            observation=list(meta.get("known") or meta.get("observation") or []),
            unknown=list(meta.get("unknown") or []),
            assumption=list(meta.get("assumption") or []),
        ),
    )


def from_capsule(capsule: Dict[str, Any]) -> ProblemSpecification:
    return from_capsule_dict(capsule)


def to_capsule_dict(
    spec: ProblemSpecification,
    *,
    source: str = "PSS",
    clock: int = 0,
    sequence: int = 0,
    parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = spec.to_dict()

    observation = {
        "name": "pss.problem_specification",
        "schema": "pss.problem_specification/0.6",
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
                "title": spec.identity.title,
                "domain": spec.identity.domain,
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


to_plp_capsule = to_capsule
from_plp_capsule = from_capsule


def render_specification(spec: ProblemSpecification) -> str:
    lines = [
        "=" * 60,
        "PROBLEM SPECIFICATION (Thinking Conditions)",
        f"schema : {spec.schema}",
        f"version: {spec.version}",
        "=" * 60,
        "",
        "--- Identity ---",
        f"Title       : {spec.identity.title}",
        f"Domain      : {spec.identity.domain}",
        f"Description : {spec.identity.description}",
        "",
        "--- Objective ---",
        f"Goal        : {spec.objective.goal.description or '(none)'}",
        f"Current     : {spec.objective.current_state.description or '(none)'}",
        f"Difference  : {spec.objective.difference.description or '(none)'}",
    ]
    if spec.objective.goal.success_criteria:
        lines.append("Success criteria:")
        for c in spec.objective.goal.success_criteria:
            lines.append(f"  - {c}")

    lines.extend(["", "--- Constraints ---"])
    for kind, lst in [
        ("hard", spec.constraints.hard),
        ("soft", spec.constraints.soft),
        ("assumption", spec.constraints.assumptions),
        ("risk", spec.constraints.risks),
    ]:
        for c in sorted(lst, key=lambda x: -x.priority):
            lines.append(f"  [{kind}/{c.priority}] {c.statement}")

    if any([spec.scope.in_scope, spec.scope.out_of_scope, spec.scope.priority]):
        lines.extend(["", "--- Scope ---"])
        if spec.scope.in_scope:
            lines.append("In Scope : " + ", ".join(spec.scope.in_scope))
        if spec.scope.out_of_scope:
            lines.append("Out of Scope : " + ", ".join(spec.scope.out_of_scope))
        if spec.scope.priority:
            lines.append("Priority : " + ", ".join(spec.scope.priority))

    lines.extend(["", "--- Knowledge ---"])
    if spec.knowledge.observation:
        lines.append("Observation:")
        for k in spec.knowledge.observation:
            lines.append(f"  - {k}")
    if spec.knowledge.inference:
        lines.append("Inference:")
        for k in spec.knowledge.inference:
            lines.append(f"  - {k}")
    if spec.knowledge.unknown or spec.knowledge.missing:
        lines.append("Unknown / Missing:")
        for u in spec.knowledge.unknown + spec.knowledge.missing:
            lines.append(f"  - {u}")
    if spec.knowledge.assumption:
        lines.append("Assumption:")
        for a in spec.knowledge.assumption:
            lines.append(f"  - {a}")

    lines.extend([
        "",
        "--- Thinking Profile ---",
        f"Reasoning Bias : {spec.thinking_profile.reasoning_bias}",
        f"Depth          : {spec.thinking_profile.depth}",
        f"Evidence Level : {spec.thinking_profile.evidence_level}",
    ])

    lines.extend([
        "",
        "--- Behavior ---",
        f"Role             : {spec.behavior.role}",
        f"Criticism        : {spec.behavior.criticism_level}",
        f"Confidence       : {spec.behavior.confidence_policy}",
        f"Interaction      : {spec.behavior.interaction_policy}",
        f"if_unknown       : {spec.behavior.rules.if_unknown}",
        f"if_assumption    : {spec.behavior.rules.if_assumption}",
        f"if_scope_violation: {spec.behavior.rules.if_scope_violation}",
    ])
    if spec.behavior.role_description:
        lines.append(f"Role note        : {spec.behavior.role_description}")

    lines.extend([
        "",
        "--- Output ---",
        f"Format : {spec.output.format} / Style : {spec.output.style} / Length : {spec.output.length}",
        f"Language : {spec.output.language}",
    ])

    lines.extend([
        "",
        "--- Phase ---",
        f"Phase : {spec.phase_state.phase} (cycle {spec.phase_state.cycle})",
    ])
    if spec.phase_state.scope:
        lines.append(f"Scope : {spec.phase_state.scope} (agreed={spec.phase_state.scope_agreed})")

    if spec.evaluation.axes:
        lines.extend(["", "--- Evaluation Axes ---"])
        for k, v in spec.evaluation.axes.items():
            lines.append(f"  {k}: {v}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
