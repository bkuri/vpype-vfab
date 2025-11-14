"""Shared utilities for vpype-plotty."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import vpype
from vpype import Document

from vpype_plotty.exceptions import PlottyJobError


class JobFormatter:
    """Unified job and list formatting with consistent output."""

    def __init__(self):
        """Initialize formatter with state color mappings."""
        self.state_colors = {
            "pending": "🟡",
            "queued": "🔵",
            "running": "🟢",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️",
        }

        self.device_status_icons = {
            "connected": "🟢",
            "disconnected": "🔴",
            "busy": "🟡",
            "error": "❌",
            "offline": "⚫",
        }

    def format(self, data, output_format="table", data_type="single"):
        """Unified formatting for jobs and lists.

        Args:
            data: Job data (dict) or list of jobs
            output_format: Output format (table, json, simple, csv)
            data_type: Type of data ("single" or "list")

        Returns:
            Formatted string
        """
        if output_format == "json":
            if data_type == "list" and not data:
                return "No jobs found."
            return json.dumps(data, indent=2)

        elif output_format == "simple" and data_type == "single":
            return f"{data['name']}: {data['state']}"

        elif output_format == "csv" and data_type == "list":
            return self._format_csv(data)

        else:  # table format
            return self._format_table(data, data_type)

    def _format_csv(self, jobs):
        """Format jobs as CSV."""
        import csv
        import io

        if not jobs:
            return "No jobs found."

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
        return output.getvalue().strip()

    def _format_table(self, data, data_type):
        """Format data as table."""
        if data_type == "single":
            return self._format_single_table(data)
        else:
            return self._format_list_table(data)

    def _format_single_table(self, job):
        """Format single job as table row."""
        created = job.get("created_at", "Unknown")
        state = job.get("state", "Unknown")
        paper = job.get("paper", "Unknown")
        return f"{job['name']:<20} {state:<10} {paper:<8} {created}"

    def _format_list_table(self, jobs):
        """Format list of jobs as table."""
        if not jobs:
            return "No jobs found."

        lines = [f"{'Name':<20} {'State':<10} {'Paper':<8} {'Created':<20}"]
        lines.append("-" * 65)
        for job in jobs:
            created = job.get("created_at", "Unknown")[:19]  # Remove timezone info
            state = job.get("state", "Unknown")
            paper = job.get("paper", "Unknown")
            lines.append(f"{job['name']:<20} {state:<10} {paper:<8} {created}")
        return "\n".join(lines)

    def format_job_status_monitor(self, job: dict) -> str:
        """Format job status for monitor display with enhanced details.

        Args:
            job: Job data dictionary

        Returns:
            Formatted status string with progress and timing
        """
        name = job.get("name", "Unnamed")
        state = job.get("state", "unknown")
        job_id = job.get("id", "unknown")[:8]  # Short ID

        # Add progress if available
        progress = ""
        if "progress" in job:
            progress_pct = job["progress"]
            progress = f" ({progress_pct:.1f}%)"

        # Add timing if available
        timing = ""
        if "created_at" in job:
            created = datetime.fromisoformat(job["created_at"]).strftime("%H:%M:%S")
            timing = f" [{created}]"

        icon = self.state_colors.get(state, "❓")
        return f"{icon} {name} ({job_id}){progress}{timing} - {state}"

    def format_device_status(self, device: dict) -> str:
        """Format device status for display.

        Args:
            device: Device data dictionary

        Returns:
            Formatted device string
        """
        name = device.get("name", "Unknown Device")
        status = device.get("status", "unknown")
        device_type = device.get("type", "")

        icon = self.device_status_icons.get(status, "❓")

        # Include device type if available
        if device_type:
            return f"{icon} {name} - {status} ({device_type})"
        else:
            return f"{icon} {name} - {status}"


def save_document_for_plotty(
    document: Document, job_path: Path, name: str
) -> tuple[Path, Path]:
    """Save vpype document as ploTTY-compatible job.

    Args:
        document: vpype document to save
        job_path: Path to job directory
        name: Job name

    Returns:
        Tuple of (svg_path, job_json_path)

    Raises:
        PlottyJobError: If document cannot be saved
    """
    try:
        # Ensure job directory exists
        job_path.mkdir(parents=True, exist_ok=True)

        # Save optimized SVG
        svg_path = job_path / "src.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            vpype.write_svg(f, document)

        # Create job metadata
        job_data = {
            "id": name,
            "name": name,
            "paper": "A4",
            "state": "NEW",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "created_by": "vpype-plotty",
                "source": "vpype document",
            },
        }

        # Save job.json
        job_json_path = job_path / "job.json"
        with open(job_json_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2)

        return svg_path, job_json_path

    except Exception as e:
        raise PlottyJobError(f"Failed to save document for ploTTY: {e}")


def generate_job_name(document: Document, fallback_name: Optional[str] = None) -> str:
    """Generate job name from document metadata.

    Args:
        document: vpype document
        fallback_name: Optional fallback name

    Returns:
        Generated job name
    """
    # Try to extract name from document properties
    if hasattr(document, "metadata") and document.metadata:
        if "name" in document.metadata:
            return document.metadata["name"]
        if "title" in document.metadata:
            return document.metadata["title"]

    # Use fallback name or generate timestamp-based name
    if fallback_name:
        return fallback_name

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"vpype_job_{timestamp}"


def validate_preset(preset: str) -> str:
    """Validate optimization preset.

    Args:
        preset: Preset name to validate

    Returns:
        Validated preset name

    Raises:
        click.BadParameter: If preset is invalid
    """
    valid_presets = ["fast", "default", "hq"]
    if preset not in valid_presets:
        raise click.BadParameter(
            f"Invalid preset '{preset}'. Valid options: {', '.join(valid_presets)}"
        )
    return preset


# Global formatter instance for backward compatibility
_job_formatter = JobFormatter()


def format_job_status(job_data: dict, output_format: str = "table") -> str:
    """Format job status for display.

    Args:
        job_data: Job data dictionary
        output_format: Output format (table, json, simple)

    Returns:
        Formatted status string
    """
    return _job_formatter.format(job_data, output_format, "single")


def format_job_list(jobs: list[dict], output_format: str = "table") -> str:
    """Format list of jobs for display.

    Args:
        jobs: List of job data dictionaries
        output_format: Output format (table, json, csv)

    Returns:
        Formatted jobs string
    """
    return _job_formatter.format(jobs, output_format, "list")
