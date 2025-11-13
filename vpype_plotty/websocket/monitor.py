"""Enhanced monitoring with ploTTY WebSocket integration."""

from __future__ import annotations

from typing import Optional
from datetime import datetime

import click
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

try:
    from ..database import PlottyIntegration
except ImportError:
    # Fallback for when module structure isn't complete
    from vpype_plotty.database import PlottyIntegration


class PlottyMonitor:
    """Enhanced ploTTY monitor with WebSocket integration."""

    def __init__(self, workspace: Optional[str] = None):
        """Initialize ploTTY monitor.

        Args:
            workspace: ploTTY workspace path
        """
        self.workspace = workspace
        self.plotty_integration = PlottyIntegration(workspace)
        self.console = Console()
        self.live = None
        self.jobs_data = {}
        self.devices_data = {}
        self.system_alerts = []
        self.connection_status = "Disconnected"

    def create_display(self) -> Layout:
        """Create the main display layout."""
        layout = Layout()

        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="jobs", ratio=2),
            Layout(name="devices", ratio=1),
            Layout(name="alerts", ratio=1),
        )

        return layout

    def create_header(self) -> Panel:
        """Create header panel."""
        header_text = Text()
        header_text.append("vpype-plotty Monitor", style="bold blue")
        header_text.append(" | ploTTY Integration", style="dim")
        header_text.append(
            f" | {self.connection_status}",
            style="green" if self.connection_status == "Connected" else "red",
        )

        return Panel(header_text, style="bold")

    def create_jobs_table(self) -> Table:
        """Create jobs monitoring table."""
        table = Table(title="ploTTY Jobs", show_header=True, header_style="bold blue")
        table.add_column("Job ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("State", style="green")
        table.add_column("Progress", style="yellow")
        table.add_column("Created", style="dim")

        # Get jobs from ploTTY database
        try:
            jobs = self.plotty_integration.list_jobs()
            for job in jobs:
                job_id = job.get("id", "unknown")[:8]  # Short ID
                name = job.get("name", "Unnamed")
                state = job.get("state", "unknown")
                created = job.get("created_at", "unknown")

                # Format created time
                if created != "unknown":
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        created = dt.strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        created = str(created)[:8]

                table.add_row(job_id, name, state, "N/A", created)

        except Exception as e:
            table.add_row("Error", str(e), "", "", "")

        if not self.jobs_data and not table.rows:
            table.add_row("No jobs found", "", "", "", "")

        return table

    def create_devices_table(self) -> Table:
        """Create devices monitoring table."""
        table = Table(title="Devices", show_header=True, header_style="bold blue")
        table.add_column("Device", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Type", style="green")

        # Add default device info
        table.add_row("axidraw:auto", "Ready", "AxiDraw")

        return table

    def create_alerts_panel(self) -> Panel:
        """Create system alerts panel."""
        if not self.system_alerts:
            alerts_text = "No system alerts"
        else:
            alerts_text = "\\n".join(
                f"• {alert.get('title', 'Alert')}: {alert.get('message', '')}"
                for alert in self.system_alerts[-5:]  # Show last 5 alerts
            )

        return Panel(alerts_text, title="System Alerts", style="yellow")

    def create_footer(self) -> Panel:
        """Create footer panel."""
        footer_text = (
            "Press Ctrl+C to exit | WebSocket: Disabled (ploTTY v1.1.0+ required)"
        )
        return Panel(footer_text, style="dim")

    def update_display(self) -> Layout:
        """Update the complete display."""
        layout = self.create_display()

        layout["header"].update(self.create_header())
        layout["jobs"].update(self.create_jobs_table())
        layout["devices"].update(self.create_devices_table())
        layout["alerts"].update(self.create_alerts_panel())
        layout["footer"].update(self.create_footer())

        return layout

    def start_monitoring(self) -> None:
        """Start the ploTTY monitoring display."""
        try:
            with Live(
                self.update_display(), refresh_per_second=1, screen=True
            ) as self.live:
                while True:
                    try:
                        # Update display
                        if self.live:
                            self.live.update(self.update_display())
                        import time

                        time.sleep(1)  # Update every second

                    except KeyboardInterrupt:
                        break

        except KeyboardInterrupt:
            self.console.print("\\nMonitor stopped by user")
        except Exception as e:
            self.console.print(f"Monitor error: {e}", style="red")


@click.command()
@click.option(
    "--workspace", "-w", help="ploTTY workspace path (default: XDG data directory)"
)
@click.option("--follow", "-f", is_flag=True, help="Follow job progress in real-time")
def plotty_monitor(workspace: Optional[str], follow: bool) -> None:
    """Monitor ploTTY jobs with real-time updates."""

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
