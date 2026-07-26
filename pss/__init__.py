"""
PSS — Problem Specification System (v0.9)
=========================================
思考条件を定義し、検証する共通仕様。

Public API (stable toward v1.0)
-------------------------------
    from pss import (
        ProblemSpecification,
        ProblemBuilder,
        validate,
        plan_fixes,
        to_capsule,
        from_capsule,
        compile_for_generic,
        render_specification,
    )

Other symbols are available but considered internal / transitional.
"""

from .core import (
    ProblemSpecification,
    Identity,
    Objective,
    CurrentState,
    Goal,
    Difference,
    Constraints,
    ConstraintSpec,
    Scope,
    KnowledgeState,
    ThinkingProfile,
    Behavior,
    BehaviorRules,
    OutputSpec,
    EvaluationAxis,
    PhaseState,
    Phase,
    ReasoningBias,
    Depth,
    EvidenceLevel,
    AgentRole,
    Audience,
    ConfidencePolicy,
    InteractionPolicy,
    CriticismLevel,
)
from .builder import ProblemBuilder
from .transport import (
    to_capsule,
    from_capsule,
    to_plp_capsule,
    from_plp_capsule,
    problem_spec_to_dict,
    problem_spec_to_json,
    render_specification,
)
from .adapter import compile_for_generic
from .validator import validate, ValidationReport, Finding, Severity
from .planner import plan_fixes, FixPlan, FixStep, FixAction

# Transitional / internal
from .adapter import (
    compile_for_gpt,
    compile_for_claude,
    compile_for_gemini,
    compile_for_local,
    compile_phase_only,
)
from .validator import (
    CompositeValidator,
    ScopeValidator,
    PhaseValidator,
    BehaviorValidator,
    KnowledgeValidator,
    ConstraintValidator,
    OutputValidator,
    IdentityValidator,
    ObjectiveValidator,
)
from .planner import FixPlanner
from .phase import Phase as PhaseEnum, PhaseState as PhaseStateLegacy, PhaseController, PHASE_RULES

__version__ = "0.9.0"

__all__ = [
    "ProblemSpecification",
    "ProblemBuilder",
    "validate",
    "plan_fixes",
    "to_capsule",
    "from_capsule",
    "compile_for_generic",
    "render_specification",
    "ValidationReport",
    "Finding",
    "Severity",
    "FixPlan",
    "FixStep",
    "FixAction",
    "Identity",
    "Objective",
    "KnowledgeState",
    "Behavior",
    "BehaviorRules",
    "PhaseState",
    "Phase",
    "__version__",
]
