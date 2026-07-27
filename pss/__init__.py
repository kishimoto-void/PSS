"""
PSS — Problem Specification System (v0.9.1)
===========================================
思考条件を定義し、検証する共通仕様。

Public API (freeze candidate toward v1.0)
-----------------------------------------
    from pss import (
        ProblemSpecification,
        ProblemBuilder,
        validate,
        plan_fixes,
        to_capsule,
        from_capsule,
        compile_for_generic,
        render_specification,
        Mission,
        PredictionPolicy,
        EvaluationCriteria,
        GateResult,
        GateDecision,
    )

Deprecations (kept for compatibility until v2.0):
  - ProblemBuilder.agent_role(...)  → use .behavior(role=..., role_description=...)
  - EvaluationAxis                 → prefer EvaluationCriteria
  - Objective                      → prefer Mission (Objective remains supported)

See DEPRECATIONS.md and ROADMAP.md for the full plan.
"""

from .core import (
    ProblemSpecification,
    Identity,
    Objective,
    CurrentState,
    Goal,
    Difference,
    Mission,
    SubMission,
    Constraints,
    ConstraintSpec,
    Scope,
    KnowledgeState,
    ThinkingProfile,
    PredictionPolicy,
    Behavior,
    BehaviorRules,
    OutputSpec,
    EvaluationAxis,
    EvaluationCriteria,
    PhaseState,
    Phase,
    GateResult,
    GateDecision,
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

# Transitional / internal (not in __all__)
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

__version__ = "0.9.1"

# Strict public surface toward v1.0
__all__ = [
    # Core entry points
    "ProblemSpecification",
    "ProblemBuilder",
    "validate",
    "plan_fixes",
    "to_capsule",
    "from_capsule",
    "compile_for_generic",
    "render_specification",
    # Results / reports
    "ValidationReport",
    "Finding",
    "Severity",
    "FixPlan",
    "FixStep",
    "FixAction",
    "GateResult",
    "GateDecision",
    # Primary data structures (RC-aligned)
    "Identity",
    "Mission",
    "SubMission",
    "KnowledgeState",
    "PredictionPolicy",
    "ThinkingProfile",
    "Behavior",
    "BehaviorRules",
    "EvaluationCriteria",
    "PhaseState",
    "Phase",
    # Still supported (compatibility)
    "Objective",
    "EvaluationAxis",
    # Meta
    "__version__",
]
