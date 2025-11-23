"""Command-line interface for half-america."""

from pathlib import Path

import click

from half_america.config import TOPOJSON_DIR
from half_america.data.cache import get_sweep_cache_path
from half_america.data.pipeline import load_all_tracts
from half_america.graph.pipeline import load_graph_data
from half_america.optimization import (
    save_sweep_result,
    sweep_lambda,
)
from half_america.optimization.sweep import load_sweep_result
from half_america.postprocess import (
    dissolve_all_lambdas,
    export_all_lambdas,
    export_combined_topojson,
    simplify_all_lambdas,
)


@click.group()
def cli() -> None:
    """Half of America - topology optimization for population distribution."""
    pass


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Rebuild cache even if it exists",
)
@click.option(
    "--lambda-step",
    type=float,
    default=0.1,
    help="Lambda increment (default: 0.1)",
)
@click.option(
    "--lambda-max",
    type=float,
    default=0.99,
    help="Maximum lambda value, exclusive (default: 0.99)",
)
@click.option(
    "--skip-failures",
    is_flag=True,
    help="Continue sweep even if some lambda values fail to converge",
)
def precompute(
    force: bool, lambda_step: float, lambda_max: float, skip_failures: bool
) -> None:
    """Pre-compute optimization results for all lambda values."""
    cache_path = get_sweep_cache_path(lambda_step)

    if cache_path.exists() and not force:
        click.echo(f"Cache exists: {cache_path}")
        click.echo("Use --force to rebuild")
        return

    click.echo("Loading tract data...")
    gdf = load_all_tracts()

    click.echo("Building graph data...")
    graph_data = load_graph_data(gdf)

    # Generate lambda values from 0.0 up to but not including lambda_max
    num_steps = int(lambda_max / lambda_step)
    lambda_values = [round(i * lambda_step, 2) for i in range(num_steps)]
    click.echo(f"Running sweep for {len(lambda_values)} lambda values...")

    result = sweep_lambda(
        graph_data,
        lambda_values=lambda_values,
        raise_on_failure=not skip_failures,
    )

    save_sweep_result(result, cache_path)
    click.echo(f"Saved to: {cache_path}")


@cli.command()
@click.option(
    "--lambda-step",
    type=float,
    default=0.1,
    help="Lambda step size (must match precomputed sweep)",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help=f"Output directory (default: {TOPOJSON_DIR})",
)
@click.option(
    "--combined",
    is_flag=True,
    help="Also export all lambdas to a single combined.json file",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing output files",
)
def export(
    lambda_step: float,
    output_dir: Path | None,
    combined: bool,
    force: bool,
) -> None:
    """Export post-processed geometries as TopoJSON for web delivery."""
    # Resolve output directory
    if output_dir is None:
        output_dir = TOPOJSON_DIR

    # Check for existing output
    if output_dir.exists() and any(output_dir.glob("*.json")) and not force:
        click.echo(f"Output files exist in: {output_dir}")
        click.echo("Use --force to overwrite")
        return

    # Load sweep result
    cache_path = get_sweep_cache_path(lambda_step)
    if not cache_path.exists():
        click.echo(f"Sweep cache not found: {cache_path}")
        click.echo("Run 'half-america precompute' first")
        return

    click.echo(f"Loading sweep result from {cache_path}...")
    sweep_result = load_sweep_result(cache_path)

    click.echo("Loading tract data...")
    gdf = load_all_tracts()

    # Run postprocessing pipeline
    click.echo("Dissolving partitions...")
    dissolve_results = dissolve_all_lambdas(gdf, sweep_result, verbose=False)

    click.echo("Simplifying geometries...")
    simplify_results = simplify_all_lambdas(dissolve_results, verbose=False)

    # Export to TopoJSON
    click.echo(f"Exporting TopoJSON to {output_dir}...")
    export_results = export_all_lambdas(
        simplify_results,
        dissolve_results,
        output_dir=output_dir,
        verbose=True,
    )

    # Optionally create combined file
    if combined:
        click.echo("Creating combined TopoJSON...")
        combined_path = export_combined_topojson(
            simplify_results,
            dissolve_results,
            output_path=output_dir / "combined.json",
            verbose=True,
        )
        click.echo(f"Combined file: {combined_path}")

    # Summary
    total_size = sum(r.file_size_bytes for r in export_results.values())
    total_kb = total_size / 1024
    click.echo(f"\nExported {len(export_results)} files ({total_kb:.1f} KB total)")
