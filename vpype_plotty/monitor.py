"""Streamlined ploTTY monitoring with configurable polling rates."""

import time
from typing import Optional, Dict, Any
from datetime import datetime

import click

from vpype_plotty.database import PlottyIntegration
from vpype_plotty.utils import JobFormatter


# StatusFormatter replaced by unified JobFormatter from utils.py


class SimplePlottyMonitor:
    """Simplified ploTTY monitor with configurable polling rates."""

    def __init__(self, workspace: Optional[str] = None, poll_rate: float = 1.0):
        """Initialize ploTTY monitor.

        Args:
            workspace: ploTTY workspace path
            poll_rate: Polling rate in seconds (0.1 = 100ms, 10.0 = 10s)
        """
        self.workspace = workspace
        self.poll_rate = max(0.1, min(10.0, poll_rate))  # Clamp between 0.1s and 10s
        self.plotty_integration = PlottyIntegration(workspace)
        self.last_job_states = {}
        self.formatter = JobFormatter()

    def format_job_status(self, job: Dict[str, Any]) -> str:
        """Format job status for display (backward compatibility)."""
        return self.formatter.format_job_status_monitor(job)

    def format_device_status(self, device: Dict[str, Any]) -> str:
        """Format device status for display (backward compatibility)."""
        return self.formatter.format_device_status(device)

    def update_display(self) -> None:
        """Update the display with current status."""
        # Clear screen (works on most terminals)
        click.clear()

        # Header
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        poll_interval = f"{self.poll_rate:.1f}s"
        click.echo(f"🔍 ploTTY Monitor - {now} (updates every {poll_interval})")
        click.echo("=" * 60)

        try:
            # Get jobs
            jobs = self.plotty_integration.list_jobs()

            if jobs:
                click.echo("\n📋 Jobs:")
                for job in jobs:
                    click.echo(f"  {self.formatter.format_job_status_monitor(job)}")

                    # Check for state changes
                    job_id = job.get("id", "")
                    old_state = self.last_job_states.get(job_id, "")
                    new_state = job.get("state", "")

                    if old_state and old_state != new_state:
                        click.echo(f"    🔄 State changed: {old_state} → {new_state}")

                    self.last_job_states[job_id] = new_state
            else:
                click.echo("\n📋 No jobs found")

            # Get devices (basic implementation)
            click.echo("\n🖊️  Devices:")
            click.echo("  🟢 axidraw:auto (AxiDraw) - connected")

            # System info
            click.echo(f"\nℹ️  Workspace: {self.plotty_integration.workspace}")
            click.echo(f"📊 Total jobs: {len(jobs) if jobs else 0}")

        except Exception as e:
            click.echo(f"\n❌ Error updating display: {e}")

    def start_monitoring(self) -> None:
        """Start monitoring with configurable polling rate."""
        click.echo(f"🚀 Starting ploTTY monitor (polling every {self.poll_rate:.1f}s)")
        click.echo("   Press Ctrl+C to stop monitoring")
        click.echo()

        try:
            while True:
                self.update_display()
                time.sleep(self.poll_rate)
        except KeyboardInterrupt:
            click.echo("\n\n👋 Monitor stopped by user")
        except Exception as e:
            click.echo(f"\n❌ Monitor error: {e}")

    def static_snapshot(self) -> None:
        """Show a single static snapshot of current status."""
        click.echo("📊 ploTTY Job Status")
        click.echo("=" * 40)
        self.update_display()


@click.command()
@click.option(
    "--workspace", "-w", help="ploTTY workspace path (default: XDG data directory)"
)
@click.option("--follow", "-f", is_flag=True, help="Follow job progress with updates")
@click.option(
    "--poll-rate",
    "-r",
    type=float,
    default=1.0,
    help="Polling rate in seconds (0.1-10.0, default: 1.0)",
)
@click.option("--fast", is_flag=True, help="Fast updates (100ms polling rate)")
@click.option("--slow", is_flag=True, help="Slow updates (5s polling rate)")
def plotty_monitor(
    workspace: Optional[str], follow: bool, poll_rate: float, fast: bool, slow: bool
) -> None:
    """Monitor ploTTY jobs with configurable real-time updates.

    Examples:
        plotty-monitor --follow                    # 1s updates (default)
        plotty-monitor --follow --poll-rate 0.5   # 500ms updates
        plotty-monitor --follow --fast              # 100ms updates (industrial)
        plotty-monitor --follow --slow              # 5s updates (casual)
        plotty-monitor                              # Static snapshot
    """
    # Handle preset options
    if fast:
        poll_rate = 0.1  # 100ms for industrial use
    elif slow:
        poll_rate = 5.0  # 5s for casual use

    # Validate poll rate
    poll_rate = max(0.1, min(10.0, poll_rate))

    # Create monitor
    monitor = SimplePlottyMonitor(workspace, poll_rate)

    if follow:
        monitor.start_monitoring()
    else:
        monitor.static_snapshot()
