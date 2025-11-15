"""Streamlined vpype commands for vpype-plotty."""

from typing import Optional

import click
from click import Abort

from vpype_vfab.decorators import (
    vfab_command,
    name_option,
    preset_option,
    queue_option,
    priority_option,
    pen_mapping_option,
)
from vpype_vfab.utils import (
    format_job_list,
    format_job_status,
    generate_job_name,
    validate_preset,
)


def _interactive_pen_mapping(
    document, job_name: str, workspace: Optional[str] = None
) -> dict:
    """Interactive pen mapping for multi-pen designs.

    Args:
        document: vpype document with layers
        job_name: Name of the job
        workspace: vfab workspace path

    Returns:
        Dictionary mapping layer IDs to pen numbers
    """
    import yaml
    from pathlib import Path

    pen_mapping = {}

    # Get existing pen mapping file path
    config_dir = Path(workspace or "") or Path.home() / ".vpype-vfab"
    config_dir.mkdir(parents=True, exist_ok=True)
    pen_mapping_file = config_dir / "pen_mappings.yaml"

    # Load existing pen mappings if available
    existing_mappings = {}
    if pen_mapping_file.exists():
        try:
            with open(pen_mapping_file, "r") as f:
                existing_mappings = yaml.safe_load(f) or {}
        except Exception:
            click.echo("⚠ Warning: Could not load existing pen mappings", err=True)

    click.echo(f"\n🎨 Interactive Pen Mapping for Job '{job_name}'")
    click.echo("=" * 50)

    # Check if document has multiple layers
    if len(document.layers) <= 1:
        click.echo("Single layer detected - using pen 1")
        return {0: 1}

    # Display layer information
    click.echo(f"Found {len(document.layers)} layers:")
    for layer_id, layer in document.layers.items():
        line_count = len(layer)
        click.echo(f"  Layer {layer_id}: {line_count} lines")

    click.echo("\nEnter pen number for each layer (1-8):")

    # Get pen mapping for each layer
    for layer_id in document.layers:
        # Check for existing mapping
        layer_key = f"{job_name}_layer_{layer_id}"
        if layer_key in existing_mappings:
            default_pen = existing_mappings[layer_key]
            prompt = f"Layer {layer_id} pen [{default_pen}]: "
        else:
            default_pen = None
            prompt = f"Layer {layer_id} pen: "

        while True:
            try:
                pen_input = click.prompt(prompt, default=default_pen, type=int)
                if 1 <= pen_input <= 8:
                    pen_mapping[layer_id] = pen_input
                    existing_mappings[layer_key] = pen_input
                    break
                else:
                    click.echo("Pen number must be between 1 and 8")
            except Abort:
                click.echo("\nPen mapping cancelled")
                return {}

    # Save pen mappings
    try:
        with open(pen_mapping_file, "w") as f:
            yaml.dump(existing_mappings, f, default_flow_style=False)
    except OSError:
        click.echo("⚠ Warning: Could not save pen mappings", err=True)

    click.echo(f"\n✅ Pen mapping saved: {pen_mapping}")
    return pen_mapping


@vfab_command(
    name_option(),
    preset_option(),
    queue_option(),
    priority_option(),
    pen_mapping_option(),
    error_context="job creation",
)
def vfab_add(cmd, document, name, preset, queue, priority, pen_mapping, workspace):
    """Add document to vfab job system."""
    # Validate preset
    validate_preset(preset)

    # Generate job name if not provided
    if not name:
        name = generate_job_name(document)

    # Get pen mapping for multi-layer designs
    if pen_mapping == "interactive":
        pen_map = _interactive_pen_mapping(document, name, cmd.plotty.workspace)
        if not pen_map:  # User cancelled
            return document
    else:
        pen_map = cmd.get_pen_mapping(document, pen_mapping)

    # Add job to vfab
    job_id = cmd.plotty.add_job(
        document=document,
        name=name,
        preset=preset,
        priority=priority,
        pen_mapping=pen_map,
    )

    click.echo(f"✅ Job '{name}' added to vfab (ID: {job_id[:8]})")
    click.echo("💡 Use 'vfab-monitor --follow' for real-time job tracking")

    # Queue job if requested
    if queue:
        cmd.plotty.queue_job(job_id, priority)
        click.echo(f"🚀 Job queued with priority {priority}")

    return document


@vfab_command(
    name_option(required=True),
    priority_option(),
    error_context="job queuing",
)
def vfab_queue(cmd, document, name, priority, workspace):
    """Queue existing vfab job."""
    # Verify job exists
    try:
        cmd.plotty.load_job(name)
    except Exception:
        click.echo(f"✗ Job '{name}' not found")
        return document

    # Queue job
    cmd.plotty.queue_job(name, priority)
    click.echo(f"🚀 Job '{name}' queued with priority {priority}")

    return document


@vfab_command(
    click.option("--name", "-n", help="Job name or ID"),
    click.option(
        "--format",
        "-f",
        default="table",
        type=click.Choice(["table", "json", "yaml"]),
        help="Output format",
    ),
    error_context="status check",
)
def vfab_status(cmd, document, name, format, workspace):
    """Check vfab job status."""
    if name:
        # Get specific job status
        try:
            job = cmd.plotty.get_job(name)
            output = format_job_status(job, format)
        except Exception:
            click.echo(f"✗ Job '{name}' not found")
            return document
    else:
        # Get all jobs status
        jobs = cmd.plotty.list_jobs()
        if not jobs:
            click.echo("No jobs found.")
            return document

        output = format_job_list(jobs, format)

    click.echo(output)
    return document


@vfab_command(
    click.option("--state", "-s", help="Filter by job state"),
    click.option(
        "--format",
        "-f",
        default="table",
        type=click.Choice(["table", "json", "yaml"]),
        help="Output format",
    ),
    click.option("--limit", type=int, help="Limit number of jobs"),
    error_context="job listing",
)
def vfab_list(cmd, document, state, format, limit, workspace):
    """List vfab jobs."""
    jobs = cmd.plotty.list_jobs()

    # Filter by state
    if state:
        jobs = [job for job in jobs if job.get("state") == state]

    # Limit results
    if limit:
        jobs = jobs[:limit]

    if not jobs:
        click.echo("No jobs found.")
        return document

    output = format_job_list(jobs, format)
    click.echo(output)
    return document


@vfab_command(
    click.option(
        "--follow", "-f", is_flag=True, help="Follow job progress with updates"
    ),
    click.option(
        "--poll-rate",
        "-r",
        type=float,
        default=1.0,
        help="Polling rate in seconds (0.1-10.0, default: 1.0)",
    ),
    click.option("--fast", is_flag=True, help="Fast updates (100ms polling rate)"),
    click.option("--slow", is_flag=True, help="Slow updates (5s polling rate)"),
    error_context="monitoring",
)
def vfab_monitor(cmd, document, follow, poll_rate, fast, slow, workspace):
    """Monitor vfab jobs with configurable real-time updates."""
    # Import streamlined monitor
    from .monitor import SimplePlottyMonitor

    # Handle preset options
    if fast:
        poll_rate = 0.1  # 100ms for industrial use
    elif slow:
        poll_rate = 5.0  # 5s for casual use

    # Create monitor
    monitor = SimplePlottyMonitor(cmd.plotty.workspace, poll_rate)

    if follow:
        monitor.start_monitoring()
    else:
        monitor.static_snapshot()

    return document


@vfab_command(
    name_option(required=True),
    click.option("--force", is_flag=True, help="Force deletion without confirmation"),
    error_context="job deletion",
)
def vfab_delete(cmd, document, name, force, workspace):
    """Delete vfab job."""
    # Verify job exists
    try:
        job = cmd.plotty.get_job(name)
    except Exception:
        click.echo(f"✗ Job '{name}' not found")
        return document

    # Confirm deletion unless forced
    if not force:
        if not click.confirm(f"Delete job '{name}' ({job.get('state', 'unknown')})?"):
            click.echo("Deletion cancelled")
            return document

    # Delete job
    cmd.plotty.remove_job(name)
    click.echo(f"🗑️ Job '{name}' deleted")

    return document
