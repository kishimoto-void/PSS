"""
PSS — Problem Specification System (v0.5)
=========================================
思考条件を定義する共通仕様。

設計思想:
  PSS は「LLMを制御する仕様」ではなく、「思考条件を定義する仕様」である。
  人間 / Agent / LLM が同じ思考条件を共有できるようにする。
"""

from .core import (
    # Identity
    Identity,
    # Objective
    Objective,
    CurrentState,
    Goal,
    Difference,
    # Constraints
    Constraints,
    ConstraintSpec,
    # Scope
    Scope,
    # Knowledge
    KnowledgeState,
    # Thinking Profile
    ThinkingProfile,
    ReasoningBias,
    Depth,
    EvidencePolicy,
    # Agent Role
    AgentRoleSpec,
    AgentRole,
    # Output
    OutputSpec,
    # Evaluation
    EvaluationAxis,
    # Extensions
    ExtensionOptions,
    Audience,
    ConfidencePolicy,
    InteractionPolicy,
    CriticismLevel,
    # Aggregate
    ProblemSpecification,
)
from .builder import ProblemBuilder
from .transport import (
    from_capsule,
    to_capsule,
    from_plp_capsule,
    to_plp_capsule,
    problem_spec_to_dict,
    problem_spec_to_json,
    render_specification,
)
from .phase import (
    Phase,
    PhaseState,
    PhaseController,
    PHASE_RULES,
)
from .adapter import (
    compile_for_generic,
    compile_for_gpt,
    compile_for_claude,
    compile_for_gemini,
    compile_for_local,
    compile_phase_only,
)

__all__ = [
    # core
    "Identity",
    "Objective",
    "CurrentState",
    "Goal",
    "Difference",
    "Constraints",
    "ConstraintSpec",
    "Scope",
    "KnowledgeState",
    "ThinkingProfile",
    "ReasoningBias",
    "Depth",
    "EvidencePolicy",
    "AgentRoleSpec",
    "AgentRole",
    "OutputSpec",
    "EvaluationAxis",
    "ExtensionOptions",
    "Audience",
    "ConfidencePolicy",
    "InteractionPolicy",
    "CriticismLevel",
    "ProblemSpecification",
    # builder
    "ProblemBuilder",
    # transport
    "from_capsule",
    "to_capsule",
    "from_plp_capsule",
    "to_plp_capsule",
    "problem_spec_to_dict",
    "problem_spec_to_json",
    "render_specification",
    # phase
    "Phase",
    "PhaseState",
    "PhaseController",
    "PHASE_RULES",
    # adapter
    "compile_for_generic",
    "compile_for_gpt",
    "compile_for_claude",
    "compile_for_gemini",
    "compile_for_local",
    "compile_phase_only",
]
