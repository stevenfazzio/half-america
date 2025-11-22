"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)

__all__ = [
    "DissolveResult",
    "dissolve_partition",
    "dissolve_all_lambdas",
]
