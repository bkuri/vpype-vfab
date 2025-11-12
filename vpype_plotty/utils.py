"""Shared utilities for vpype-plotty."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import vpype
from vpype import Document

from vpype_plotty.exceptions import PlottyJobError


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


def format_job_status(job_data: dict, output_format: str = "table") -> str:
    """Format job status for display.

    Args:
        job_data: Job data dictionary
        output_format: Output format (table, json, simple)

    Returns:
        Formatted status string
    """
    if output_format == "json":
        return json.dumps(job_data, indent=2)

    elif output_format == "simple":
        return f"{job_data['name']}: {job_data['state']}"

    else:  # table format
        created = job_data.get("created_at", "Unknown")
        state = job_data.get("state", "Unknown")
        paper = job_data.get("paper", "Unknown")
        return f"{job_data['name']:<20} {state:<10} {paper:<8} {created}"


def format_job_list(jobs: list[dict], output_format: str = "table") -> str:
    """Format list of jobs for display.

    Args:
        jobs: List of job data dictionaries
        output_format: Output format (table, json, csv)

    Returns:
        Formatted jobs string
    """
    if not jobs:
        return "No jobs found."

    if output_format == "json":
        return json.dumps(jobs, indent=2)

    elif output_format == "csv":
        import csv
        import io

        output = io.StringIO()
        if jobs:
            writer = csv.DictWriter(output, fieldnames=jobs[0].keys())
            writer.writeheader()
            writer.writerows(jobs)
        return output.getvalue().strip()

    else:  # table format
        lines = [f"{'Name':<20} {'State':<10} {'Paper':<8} {'Created':<20}"]
        lines.append("-" * 65)
        for job in jobs:
            created = job.get("created_at", "Unknown")[:19]  # Remove timezone info
            state = job.get("state", "Unknown")
            paper = job.get("paper", "Unknown")
            lines.append(f"{job['name']:<20} {state:<10} {paper:<8} {created}")
        return "\n".join(lines)
