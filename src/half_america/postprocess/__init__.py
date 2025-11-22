"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)
from half_america.postprocess.simplify import (
    DEFAULT_TOLERANCE,
    SimplifyResult,
    simplify_all_lambdas,
    simplify_geometry,
)

__all__ = [
    # Dissolve
    "DissolveResult",
    "dissolve_partition",
    "dissolve_all_lambdas",
    # Simplify
    "DEFAULT_TOLERANCE",
    "SimplifyResult",
    "simplify_geometry",
    "simplify_all_lambdas",
]
