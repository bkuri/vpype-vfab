"""Main vpype commands for vpype-plotty."""

from pathlib import Path

import click
import vpype
import vpype_cli
import yaml

from vpype_plotty.database import PlottyIntegration
from vpype_plotty.utils import (
    format_job_list,
    format_job_status,
    generate_job_name,
    validate_preset,
)


def _interactive_pen_mapping(document, job_name: str, workspace: str = None) -> dict:
    """Interactive pen mapping for multi-pen designs.

    Args:
        document: vpype document with layers
        job_name: Name of the job
        workspace: ploTTY workspace path

    Returns:
        Dictionary mapping layer IDs to pen numbers
    """
    pen_mapping = {}

    # Get existing pen mapping file path
    config_dir = Path(workspace) if workspace else Path.home() / ".vpype-plotty"
    config_dir.mkdir(parents=True, exist_ok=True)
    pen_mapping_file = config_dir / "pen_mappings.yaml"

    # Load existing pen mappings if available
    existing_mappings = {}
    if pen_mapping_file.exists():
        try:
            with open(pen_mapping_file, "r") as f:
                existing_mappings = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            click.echo("⚠ Warning: Could not load existing pen mappings", err=True)

    click.echo(f"\n🎨 Interactive Pen Mapping for Job '{job_name}'")
    click.echo("=" * 50)

    # Check if document has multiple layers
    if len(document.layers) <= 1:
        click.echo("Document has only one layer. Using default pen (1).")
        return {1: 1}

    click.echo(f"Found {len(document.layers)} layers in document:")

    # Display layers and prompt for pen assignments
    for layer_id in sorted(document.layers.keys()):
        layer = document.layers[layer_id]
        layer_color = layer.property(vpype.METADATA_FIELD_COLOR)

        # Display layer info
        click.echo(f"\nLayer {layer_id}:")
        click.echo(f"  Color: {layer_color or 'Default'}")
        click.echo(f"  Paths: {len(layer)}")

        # Check for existing mapping
        existing_pen = existing_mappings.get(str(layer_color), None)
        if existing_pen:
            default_prompt = f"Enter pen number (1-8) [default: {existing_pen}]: "
        else:
            default_prompt = "Enter pen number (1-8): "

        # Get pen assignment from user
        while True:
            pen_input = click.prompt(
                default_prompt, default=existing_pen or 1, type=int
            )

            if 1 <= pen_input <= 8:
                pen_mapping[layer_id] = pen_input
                break
            else:
                click.echo("⚠ Pen number must be between 1 and 8")

        # Save mapping for this color
        if layer_color:
            existing_mappings[str(layer_color)] = pen_mapping[layer_id]

    # Save updated pen mappings
    try:
        with open(pen_mapping_file, "w") as f:
            yaml.dump(existing_mappings, f, default_flow_style=False)
        click.echo(f"\n✓ Pen mappings saved to {pen_mapping_file}")
    except (yaml.YAMLError, OSError) as e:
        click.echo(f"⚠ Warning: Could not save pen mappings: {e}", err=True)

    # Display final mapping
    click.echo("\nFinal Pen Mapping:")
    for layer_id, pen_num in pen_mapping.items():
        layer = document.layers[layer_id]
        layer_color = layer.property(vpype.METADATA_FIELD_COLOR)
        click.echo(
            f"  Layer {layer_id} (color: {layer_color or 'Default'}) → Pen {pen_num}"
        )

    return pen_mapping


@click.command()
@click.option(
    "--name",
    "-n",
    help="Job name (defaults to auto-generated)",
)
@click.option(
    "--preset",
    "-p",
    default="fast",
    type=click.Choice(["fast", "default", "hq"]),
    help="Optimization preset",
)
@click.option(
    "--paper",
    default="A4",
    help="Paper size",
)
@click.option(
    "--queue/--no-queue",
    default=False,
    help="Automatically queue job after adding",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@vpype_cli.global_processor
def plotty_add(document, name, preset, paper, queue, workspace):
    """Add current document to ploTTY job queue."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # Generate job name if not provided
        if not name:
            name = generate_job_name(document)

        # Validate preset
        preset = validate_preset(preset)

        # Add job to ploTTY
        job_id = plotty.add_job(document, name, preset, paper)

        click.echo(f"✓ Added job '{job_id}' to ploTTY")

        # Queue job if requested
        if queue:
            plotty.queue_job(job_id)
            click.echo(f"✓ Queued job '{job_id}' for plotting")

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--name",
    "-n",
    required=True,
    help="Job name to queue",
)
@click.option(
    "--priority",
    default=1,
    type=int,
    help="Job priority",
)
@click.option(
    "--interactive/--no-interactive",
    default=True,
    help="Interactive pen mapping for multi-pen designs",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@vpype_cli.global_processor
def plotty_queue(document, name, priority, interactive, workspace):
    """Queue existing ploTTY job for plotting."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # Queue the job
        plotty.queue_job(name, priority)

        click.echo(f"✓ Queued job '{name}' with priority {priority}")

        if interactive:
            # Check if job has multi-pen design
            job_data = plotty.get_job_status(name)
            job_path = plotty.jobs_dir / name
            svg_path = job_path / "src.svg"

            if svg_path.exists():
                try:
                    # Load the document to check layers
                    loaded_doc = vpype.read_svg(str(svg_path), quantization=0.1)
                    pen_mapping = _interactive_pen_mapping(loaded_doc, name, workspace)

                    # Save pen mapping to job metadata
                    job_data["metadata"]["pen_mapping"] = pen_mapping
                    plotty._save_job_metadata(str(job_path), job_data)

                    click.echo("✓ Pen mapping saved to job metadata")

                except Exception as e:
                    click.echo(
                        f"⚠ Warning: Interactive pen mapping failed: {e}", err=True
                    )
            else:
                click.echo("⚠ Warning: Source SVG not found for pen mapping", err=True)

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--name",
    "-n",
    help="Specific job name (shows all if omitted)",
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "simple"]),
    help="Output format",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@vpype_cli.global_processor
def plotty_status(document, name, output_format, workspace):
    """Check ploTTY job status."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        if name:
            # Show status for specific job
            job_data = plotty.get_job_status(name)
            output = format_job_status(job_data, output_format)
            click.echo(output)
        else:
            # Show status for all jobs
            jobs = plotty.list_jobs()
            if not jobs:
                click.echo("No jobs found.")
            else:
                if output_format == "table":
                    click.echo(format_job_list(jobs, output_format))
                else:
                    for job in jobs:
                        click.echo(format_job_status(job, output_format))

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--state",
    help="Filter by job state",
)
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format",
)
@click.option(
    "--limit",
    type=int,
    help="Limit number of jobs",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@vpype_cli.global_processor
def plotty_list(document, state, output_format, limit, workspace):
    """List ploTTY jobs."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # List jobs
        jobs = plotty.list_jobs(state=state, limit=limit)

        if not jobs:
            click.echo("No jobs found.")
        else:
            output = format_job_list(jobs, output_format)
            click.echo(output)

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))
