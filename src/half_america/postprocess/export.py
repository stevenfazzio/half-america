"""Export geometries to TopoJSON format for web delivery."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import geopandas as gpd
from shapely import MultiPolygon, Polygon
from topojson import Topology

from half_america.config import TOPOJSON_DIR

if TYPE_CHECKING:
    from half_america.optimization.sweep import SweepResult
    from half_america.postprocess.dissolve import DissolveResult
    from half_america.postprocess.simplify import SimplifyResult

# Default quantization factor (1e5 = good balance of precision vs file size)
DEFAULT_QUANTIZATION = 1e5


class ExportResult(NamedTuple):
    """Result from exporting a geometry to TopoJSON."""

    path: Path
    file_size_bytes: int
    lambda_value: float
    object_name: str


class ExportMetadata(NamedTuple):
    """Metadata to embed in TopoJSON properties."""

    lambda_value: float
    population_selected: int
    total_population: int
    area_sqm: float
    num_parts: int
    total_area_all_sqm: float  # Total area of all tracts (entire US)


def export_to_topojson(
    geometry: MultiPolygon | Polygon,
    output_path: Path,
    metadata: ExportMetadata,
    object_name: str = "selected_region",
    quantization: float = DEFAULT_QUANTIZATION,
) -> ExportResult:
    """
    Export a geometry to TopoJSON format.

    Args:
        geometry: Shapely geometry in EPSG:5070 (Conus Albers)
        output_path: Path for output .json file
        metadata: Metadata to embed as properties
        object_name: Name for the geometry object in TopoJSON
        quantization: Quantization factor (default 1e5)

    Returns:
        ExportResult with path and file size

    Raises:
        ValueError: If geometry is empty
    """
    if geometry.is_empty:
        raise ValueError("Cannot export empty geometry")

    # Create GeoDataFrame with metadata as properties
    gdf = gpd.GeoDataFrame(
        {
            "lambda_value": [metadata.lambda_value],
            "population_selected": [metadata.population_selected],
            "total_population": [metadata.total_population],
            "area_sqm": [metadata.area_sqm],
            "num_parts": [metadata.num_parts],
            "total_area_all_sqm": [metadata.total_area_all_sqm],
            "geometry": [geometry],
        },
        crs="EPSG:5070",
    )

    # Transform to WGS84 for web (Mapbox GL JS expects EPSG:4326)
    gdf_wgs84 = gdf.to_crs("EPSG:4326")

    # Create TopoJSON
    topo = Topology(
        data=gdf_wgs84,
        prequantize=quantization,
        topology=True,
        object_name=object_name,
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    topo.to_json(str(output_path))

    return ExportResult(
        path=output_path,
        file_size_bytes=output_path.stat().st_size,
        lambda_value=metadata.lambda_value,
        object_name=object_name,
    )


def export_all_lambdas(
    simplify_results: dict[float, SimplifyResult],
    dissolve_results: dict[float, DissolveResult],
    sweep_result: SweepResult,
    output_dir: Path | None = None,
    verbose: bool = True,
) -> dict[float, ExportResult]:
    """
    Export simplified geometries for all lambda values to individual TopoJSON files.

    Args:
        simplify_results: Dictionary mapping lambda values to SimplifyResult
        dissolve_results: Dictionary mapping lambda values to DissolveResult
            (needed for population/area metadata)
        sweep_result: SweepResult with optimization results (needed for total_area)
        output_dir: Output directory (default: data/output/topojson)
        verbose: Print progress messages

    Returns:
        Dictionary mapping lambda values to ExportResult
    """
    if output_dir is None:
        output_dir = TOPOJSON_DIR

    results: dict[float, ExportResult] = {}

    for lambda_val in simplify_results:
        if verbose:
            print(f"Exporting λ={lambda_val:.2f}...")

        simplify_result = simplify_results[lambda_val]
        dissolve_result = dissolve_results[lambda_val]

        # Get total area from sweep result
        opt_result = sweep_result.results[lambda_val].search_result.result
        total_area_all_sqm = opt_result.total_area

        # Build metadata from dissolve result
        metadata = ExportMetadata(
            lambda_value=lambda_val,
            population_selected=dissolve_result.population_selected,
            total_population=dissolve_result.total_population,
            area_sqm=dissolve_result.total_area_sqm,
            num_parts=dissolve_result.num_parts,
            total_area_all_sqm=total_area_all_sqm,
        )

        output_path = output_dir / f"lambda_{lambda_val:.2f}.json"
        result = export_to_topojson(
            geometry=simplify_result.geometry,
            output_path=output_path,
            metadata=metadata,
        )
        results[lambda_val] = result

        if verbose:
            size_kb = result.file_size_bytes / 1024
            print(f"  → {result.path.name} ({size_kb:.1f} KB)")

    return results


def export_combined_topojson(
    simplify_results: dict[float, SimplifyResult],
    dissolve_results: dict[float, DissolveResult],
    sweep_result: SweepResult,
    output_path: Path | None = None,
    quantization: float = DEFAULT_QUANTIZATION,
    verbose: bool = True,
) -> Path:
    """
    Export all lambda values to a single multi-object TopoJSON file.

    Args:
        simplify_results: Dictionary mapping lambda values to SimplifyResult
        dissolve_results: Dictionary mapping lambda values to DissolveResult
        sweep_result: SweepResult with optimization results (needed for total_area)
        output_path: Output file path (default: data/output/topojson/combined.json)
        quantization: Quantization factor
        verbose: Print progress messages

    Returns:
        Path to the combined TopoJSON file
    """
    if output_path is None:
        output_path = TOPOJSON_DIR / "combined.json"

    # Build list of GeoDataFrames with object names
    gdfs = []
    object_names = []

    for lambda_val in sorted(simplify_results.keys()):
        simplify_result = simplify_results[lambda_val]
        dissolve_result = dissolve_results[lambda_val]

        # Get total area from sweep result
        opt_result = sweep_result.results[lambda_val].search_result.result
        total_area_all_sqm = opt_result.total_area

        gdf = gpd.GeoDataFrame(
            {
                "lambda_value": [lambda_val],
                "population_selected": [dissolve_result.population_selected],
                "total_population": [dissolve_result.total_population],
                "area_sqm": [dissolve_result.total_area_sqm],
                "num_parts": [dissolve_result.num_parts],
                "total_area_all_sqm": [total_area_all_sqm],
                "geometry": [simplify_result.geometry],
            },
            crs="EPSG:5070",
        )
        gdf_wgs84 = gdf.to_crs("EPSG:4326")
        gdfs.append(gdf_wgs84)
        object_names.append(f"lambda_{lambda_val:.2f}")

    if verbose:
        print(f"Creating combined TopoJSON with {len(gdfs)} objects...")

    # Create multi-object TopoJSON
    topo = Topology(
        data=gdfs,
        prequantize=quantization,
        topology=True,
        object_name=object_names,
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    topo.to_json(str(output_path))

    if verbose:
        size_kb = output_path.stat().st_size / 1024
        print(f"  → {output_path.name} ({size_kb:.1f} KB)")

    return output_path
