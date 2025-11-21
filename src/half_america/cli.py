"""Command-line interface for half-america."""

import click

from half_america.data.cache import get_sweep_cache_path
from half_america.data.pipeline import load_all_tracts
from half_america.graph.pipeline import load_graph_data
from half_america.optimization import (
    save_sweep_result,
    sweep_lambda,
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
    "--skip-failures",
    is_flag=True,
    help="Continue sweep even if some lambda values fail to converge",
)
def precompute(force: bool, lambda_step: float, skip_failures: bool) -> None:
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

    # Generate lambda values from 0.0 up to but not including 1.0
    num_steps = int(1 / lambda_step)
    lambda_values = [round(i * lambda_step, 2) for i in range(num_steps)]
    click.echo(f"Running sweep for {len(lambda_values)} lambda values...")

    result = sweep_lambda(
        graph_data,
        lambda_values=lambda_values,
        raise_on_failure=not skip_failures,
    )

    save_sweep_result(result, cache_path)
    click.echo(f"Saved to: {cache_path}")
