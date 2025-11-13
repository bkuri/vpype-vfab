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
        # Get the single layer ID, or use 0 if no layers
        if document.layers:
            layer_id = next(iter(document.layers.keys()))
        else:
            layer_id = 0
        click.echo("Document has only one layer. Using pen 1.")
        return {layer_id: 1}

    # Display layer information
    click.echo(f"Found {len(document.layers)} layers:")
    for layer_id, layer in document.layers.items():
        path_count = len(layer)
        click.echo(f"  Layer {layer_id}: {path_count} paths")

    click.echo()

    # Map each layer to a pen
    for i, (layer_id, layer) in enumerate(document.layers.items()):
        path_count = len(layer)

        # Check for existing mapping
        mapping_key = f"{job_name}_layer_{layer_id}"
        if mapping_key in existing_mappings:
            suggested_pen = existing_mappings[mapping_key]
        else:
            suggested_pen = (i % 4) + 1  # Cycle through pens 1-4

        # Get user input
        while True:
            try:
                pen_input = click.prompt(
                    f"Layer {layer_id} ({path_count} paths) → Pen number",
                    default=suggested_pen,
                    type=int,
                )
                if 1 <= pen_input <= 4:  # Assuming 4 pens max
                    pen_mapping[layer_id] = pen_input
                    break
                else:
                    click.echo("⚠ Pen number must be between 1 and 4")
            except (click.Abort, KeyboardInterrupt):
                click.echo("\n❌ Pen mapping cancelled")
                return {}

    # Save mappings for future use
    for layer_id, pen_num in pen_mapping.items():
        mapping_key = f"{job_name}_layer_{layer_id}"
        existing_mappings[mapping_key] = pen_num

    try:
        with open(pen_mapping_file, "w") as f:
            yaml.dump(existing_mappings, f, default_flow_style=False)
        click.echo(f"\n💾 Pen mappings saved to {pen_mapping_file}")
    except OSError as e:
        click.echo(f"⚠ Warning: Could not save pen mappings: {e}", err=True)

    return pen_mapping


@click.command()
@click.option(
    "--name",
    "-n",
    help="Job name (auto-generated if not provided)",
)
@click.option(
    "--preset",
    "-p",
    default="default",
    help="Optimization preset (fast, default, hq)",
    type=click.Choice(["fast", "default", "hq"]),
)
@click.option(
    "--queue",
    "-q",
    is_flag=True,
    help="Add job to queue after creation",
)
@click.option(
    "--priority",
    type=int,
    default=1,
    help="Job priority (1=highest)",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@click.option(
    "--pen-mapping",
    is_flag=True,
    help="Interactive pen mapping for multi-layer designs",
)
@vpype_cli.global_processor
def plotty_add(
    document,
    name,
    preset,
    queue,
    priority,
    workspace,
    pen_mapping,
):
    """Add document to ploTTY job system."""
    try:
        # Validate preset
        validate_preset(preset)

        # Generate job name if not provided
        if not name:
            name = generate_job_name(document)

        # Handle pen mapping for multi-layer designs
        if pen_mapping and len(document.layers) > 1:
            pen_map = _interactive_pen_mapping(document, name, workspace)
            if not pen_map:
                click.echo("❌ Pen mapping failed - aborting job creation")
                return document
        else:
            pen_map = None

        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # Add job to ploTTY
        job_id = plotty.add_job(
            document=document,
            name=name,
            preset=preset,
            priority=priority,
            pen_mapping=pen_map,
        )

        click.echo(f"✅ Job '{name}' added to ploTTY (ID: {job_id[:8]})")

        # Try to broadcast to ploTTY WebSocket if available
        try:
            # Import WebSocket client
            from .websocket.client import PlottyWebSocketClient
            from .websocket.schemas import VpypePlottyMessage

            # Create WebSocket client
            ws_client = PlottyWebSocketClient()

            # Try to connect and broadcast
            import asyncio

            async def broadcast_job_creation():
                if await ws_client.connect():
                    try:
                        # Create job creation message (for future WebSocket broadcasting)
                        _ = VpypePlottyMessage(
                            job_id=job_id,
                            from_state="new",
                            to_state="created",
                            reason=f"Created by vpype-plotty with preset '{preset}'",
                            source="vpype-plotty",
                            vpype_version=(
                                vpype.__version__
                                if hasattr(vpype, "__version__")
                                else "unknown"
                            ),
                            layer_count=len(document.layers),
                            total_distance=sum(
                                (
                                    sum(
                                        layer.geometry.length()
                                        for layer in document.layers
                                    )
                                    if hasattr(layer, "geometry")
                                    else 0
                                )
                                for layer in document.layers
                            ),
                            metadata={
                                "name": name,
                                "preset": preset,
                                "priority": priority,
                                "pen_mapping": pen_map is not None,
                                "workspace": workspace,
                            },
                        )

                        # Subscribe to jobs channel
                        await ws_client.subscribe(["jobs"])

                        # Broadcast message (note: this would need server-side broadcasting)
                        # For now, just indicate WebSocket is available
                        click.echo(
                            "📡 ploTTY WebSocket connected - real-time monitoring available"
                        )

                        await ws_client.disconnect()

                    except Exception as ws_e:
                        # Don't fail the command if WebSocket broadcast fails
                        click.echo(f"⚠ WebSocket broadcast failed: {ws_e}")
                else:
                    click.echo(
                        "ℹ ploTTY WebSocket not available - use 'plotty-monitor' for status"
                    )

            # Run broadcast in background
            asyncio.run(broadcast_job_creation())

        except ImportError:
            # WebSocket not available
            click.echo("ℹ ploTTY WebSocket integration not available")
        except Exception as ws_e:
            # Any other WebSocket error
            click.echo(f"⚠ WebSocket integration error: {ws_e}")

        # Queue job if requested
        if queue:
            plotty.queue_job(job_id, priority)
            click.echo(f"🚀 Job queued with priority {priority}")

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--name",
    "-n",
    required=True,
    help="Job name or ID",
)
@click.option(
    "--priority",
    "-p",
    type=int,
    default=1,
    help="Job priority (1=highest)",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive pen mapping for multi-layer designs",
)
@vpype_cli.global_processor
def plotty_queue(document, name, priority, workspace, interactive):
    """Queue existing ploTTY job."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # Handle interactive pen mapping if requested
        if interactive:
            click.echo("⚠ Interactive pen mapping requires document access")
            click.echo("   This feature is not yet available in queue mode")
            click.echo("   Use plotty-add --pen-mapping instead")

        # Find job by name or ID
        job_id = plotty.find_job(name)
        if not job_id:
            click.echo(f"✗ Job '{name}' not found")
            return document

        # Queue job
        plotty.queue_job(name, priority)
        click.echo(f"🚀 Job '{name}' queued with priority {priority}")

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--name",
    "-n",
    help="Job name or ID",
)
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "yaml"]),
    help="Output format",
)
@click.option(
    "--workspace",
    help="ploTTY workspace path",
)
@vpype_cli.global_processor
def plotty_status(document, name, format, workspace):
    """Check ploTTY job status."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        if name:
            # Get specific job status
            job = plotty.get_job(name)
            if not job:
                click.echo(f"✗ Job '{name}' not found")
                return document

            output = format_job_status(job, format)
        else:
            # Get all jobs status
            jobs = plotty.list_jobs()
            if not jobs:
                click.echo("No jobs found.")
                return document

            output = format_job_list(jobs, format)

        click.echo(output)
        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--state",
    "-s",
    help="Filter by job state",
)
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json", "yaml"]),
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
def plotty_list(document, state, format, limit, workspace):
    """List ploTTY jobs."""
    try:
        # Initialize ploTTY integration
        plotty = PlottyIntegration(workspace)

        # List jobs
        jobs = plotty.list_jobs(state=state, limit=limit)

        if not jobs:
            click.echo("No jobs found.")
        else:
            output = format_job_list(jobs, format)
            click.echo(output)

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))


@click.command()
@click.option(
    "--workspace", "-w", help="ploTTY workspace path (default: XDG data directory)"
)
@click.option("--follow", "-f", is_flag=True, help="Follow job progress in real-time")
@vpype_cli.global_processor
def plotty_monitor(document, workspace, follow):
    """Monitor ploTTY jobs with real-time updates."""
    try:
        # Import monitor here to avoid circular imports
        try:
            from .websocket.monitor import PlottyMonitor
        except ImportError:
            click.echo("⚠️ WebSocket monitoring requires ploTTY v1.1.0+")
            click.echo("   Using basic monitoring mode...")

            # Fallback to basic status check
            from .database import PlottyIntegration

            plotty = PlottyIntegration(workspace)
            jobs = plotty.list_jobs()

            if not jobs:
                click.echo("No jobs found.")
            else:
                click.echo("📊 ploTTY Jobs:")
                for job in jobs:
                    click.echo(
                        f"  {job.get('name', 'Unnamed')}: {job.get('state', 'unknown')}"
                    )

            return document

        # Use enhanced monitor
        monitor = PlottyMonitor(workspace)

        if follow:
            click.echo("🔍 Starting ploTTY monitor (real-time mode)")
            click.echo("   Press Ctrl+C to stop monitoring")
            click.echo()

            monitor.start_monitoring()
        else:
            click.echo("📊 ploTTY Job Status")
            click.echo("=" * 50)

            # Static snapshot
            layout = monitor.update_display()
            monitor.console.print(layout)

        return document

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.ClickException(str(e))
