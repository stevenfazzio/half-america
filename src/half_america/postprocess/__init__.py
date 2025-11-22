"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)
from half_america.postprocess.export import (
    DEFAULT_QUANTIZATION,
    ExportMetadata,
    ExportResult,
    export_all_lambdas,
    export_combined_topojson,
    export_to_topojson,
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
    # Export
    "DEFAULT_QUANTIZATION",
    "ExportMetadata",
    "ExportResult",
    "export_to_topojson",
    "export_all_lambdas",
    "export_combined_topojson",
]
