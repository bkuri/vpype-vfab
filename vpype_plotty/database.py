"""ploTTY database integration."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import vpype
from vpype import Document

from vpype_plotty.config import PlottyConfig
from vpype_plotty.exceptions import (
    PlottyJobError,
    handle_plotty_errors,
    retry_on_failure,
)


class PlottyIntegration:
    """Handles integration with ploTTY system."""

    def __init__(self, workspace_path: Optional[str] = None) -> None:
        """Initialize ploTTY integration.

        Args:
            workspace_path: Optional path to ploTTY workspace directory
        """
        self.config_manager = PlottyConfig(workspace_path)
        self.workspace = self.config_manager.workspace_path
        self.jobs_dir = self.workspace / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def _plotty_available(self) -> bool:
        """Check if ploTTY is available.

        Returns:
            True if ploTTY is installed and available
        """
        try:
            import plotty  # noqa: F401
            import plotty.fsm  # noqa: F401
            import plotty.models  # noqa: F401

            return True
        except ImportError:
            return False

    @handle_plotty_errors
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def add_job(
        self,
        document: Document,
        name: str,
        preset: str = "fast",
        paper: str = "A4",
        priority: int = 1,
        pen_mapping: dict | None = None,
    ) -> str:
        """Add job to ploTTY system.

        Args:
            document: vpype document to add
            name: Job name
            preset: Optimization preset
            paper: Paper size
            priority: Job priority (1=highest)
            pen_mapping: Optional layer-to-pen mapping

        Returns:
            Job ID

        Raises:
            PlottyJobError: If job creation fails
        """
        if self._plotty_available():
            return self._add_job_plotty(
                document, name, preset, paper, priority, pen_mapping
            )
        else:
            return self._add_job_standalone(
                document, name, preset, paper, priority, pen_mapping
            )

    def _add_job_plotty(
        self,
        document: Document,
        name: str,
        preset: str,
        paper: str,
        priority: int = 1,
        pen_mapping: dict | None = None,
    ) -> str:
        """Add job using ploTTY integration.

        Args:
            document: vpype document to add
            name: Job name
            preset: Optimization preset
            paper: Paper size

        Returns:
            Job ID

        Raises:
            PlottyJobError: If ploTTY job creation fails
        """
        try:
            import plotty.fsm
            import plotty.models

            # Create job directory
            job_path = self.jobs_dir / name
            job_path.mkdir(parents=True, exist_ok=True)

            # Save document
            svg_path = job_path / "src.svg"
            with open(svg_path, "w", encoding="utf-8") as f:
                vpype.write_svg(f, document)

            # Create job using ploTTY models
            job_data = {
                "id": name,
                "name": name,
                "paper": paper,
                "state": "NEW",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "created_by": "vpype-plotty",
                    "source": "vpype document",
                    "preset": preset,
                },
            }

            # Save job metadata
            job_json_path = job_path / "job.json"
            with open(job_json_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2)

            # Use ploTTY FSM to process job
            fsm = plotty.fsm.JobFSM(str(job_path))
            fsm.create_job(job_data)

            return name

        except Exception as e:
            raise PlottyJobError(f"Failed to create ploTTY job: {e}")

    def _add_job_standalone(
        self,
        document: Document,
        name: str,
        preset: str,
        paper: str,
        priority: int = 1,
        pen_mapping: dict | None = None,
    ) -> str:
        """Add job in standalone mode without ploTTY.

        Args:
            document: vpype document to add
            name: Job name
            preset: Optimization preset
            paper: Paper size

        Returns:
            Job ID
        """
        # Create job directory
        job_path = self.jobs_dir / name
        job_path.mkdir(parents=True, exist_ok=True)

        # Save document
        svg_path = job_path / "src.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            vpype.write_svg(f, document)

        # Create job metadata
        job_data = {
            "id": name,
            "name": name,
            "paper": paper,
            "state": "NEW",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "created_by": "vpype-plotty",
                "source": "vpype document",
                "preset": preset,
                "standalone": True,
            },
        }

        # Save job metadata
        job_json_path = job_path / "job.json"
        with open(job_json_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2)

        return name

    @handle_plotty_errors
    @retry_on_failure(max_retries=2, base_delay=0.5)
    def queue_job(self, name: str, priority: int = 1) -> None:
        """Queue existing job for plotting.

        Args:
            name: Job name to queue
            priority: Job priority

        Raises:
            PlottyJobError: If job queuing fails
        """
        job_path = self.jobs_dir / name
        if not job_path.exists():
            raise PlottyJobError(f"Job '{name}' not found")

        job_json_path = job_path / "job.json"
        if not job_json_path.exists():
            raise PlottyJobError(f"Job metadata for '{name}' not found")

        try:
            # Load job metadata
            with open(job_json_path, encoding="utf-8") as f:
                job_data = json.load(f)

            # Update job state
            job_data["state"] = "QUEUED"
            job_data["queued_at"] = datetime.now(timezone.utc).isoformat()
            job_data["priority"] = priority

            # Save updated metadata
            with open(job_json_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2)

            # Use ploTTY FSM if available
            if self._plotty_available():
                import plotty.fsm

                fsm = plotty.fsm.JobFSM(str(job_path))
                fsm.queue_job(priority)

        except Exception as e:
            raise PlottyJobError(f"Failed to queue job '{name}': {e}")

    @handle_plotty_errors
    def get_job_status(self, name: str) -> Dict[str, Any]:
        """Get status of a specific job.

        Args:
            name: Job name

        Returns:
            Job status dictionary

        Raises:
            PlottyJobError: If job not found
        """
        job_path = self.jobs_dir / name
        if not job_path.exists():
            raise PlottyJobError(f"Job '{name}' not found")

        job_json_path = job_path / "job.json"
        if not job_json_path.exists():
            raise PlottyJobError(f"Job metadata for '{name}' not found")

        try:
            with open(job_json_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise PlottyJobError(f"Failed to read job status for '{name}': {e}")

    def list_jobs(
        self,
        state: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List ploTTY jobs.

        Args:
            state: Filter by job state
            limit: Limit number of jobs returned

        Returns:
            List of job dictionaries
        """
        jobs = []

        for job_path in sorted(self.jobs_dir.iterdir()):
            if not job_path.is_dir():
                continue

            job_json_path = job_path / "job.json"
            if not job_json_path.exists():
                continue

            try:
                with open(job_json_path, encoding="utf-8") as f:
                    job_data = json.load(f)

                # Filter by state if specified
                if state and job_data.get("state") != state:
                    continue

                jobs.append(job_data)

                # Apply limit if specified
                if limit and len(jobs) >= limit:
                    break

            except (json.JSONDecodeError, OSError):
                # Skip invalid job files
                continue

        return jobs

    @handle_plotty_errors
    @retry_on_failure(max_retries=2, base_delay=0.5)
    def delete_job(self, name: str) -> None:
        """Delete a job from ploTTY system.

        Args:
            name: Job name to delete

        Raises:
            PlottyJobError: If job deletion fails
        """
        job_path = self.jobs_dir / name
        if not job_path.exists():
            raise PlottyJobError(f"Job '{name}' not found")

        try:
            # Use ploTTY FSM if available to properly clean up
            if self._plotty_available():
                import plotty.fsm

                fsm = plotty.fsm.JobFSM(str(job_path))
                fsm.delete_job()

            # Remove job directory and all its contents
            import shutil

            shutil.rmtree(job_path)

        except Exception as e:
            raise PlottyJobError(f"Failed to delete job '{name}': {e}")

    def _save_job_metadata(self, job_path: str, job_data: Dict[str, Any]) -> None:
        """Save job metadata to JSON file.

        Args:
            job_path: Path to job directory
            job_data: Job metadata dictionary

        Raises:
            PlottyJobError: If metadata saving fails
        """
        from pathlib import Path

        job_dir = Path(job_path)
        job_json_path = job_dir / "job.json"

        try:
            # Ensure job directory exists
            job_dir.mkdir(parents=True, exist_ok=True)

            # Save metadata with proper formatting
            with open(job_json_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)

        except (OSError, json.JSONDecodeError) as e:
            raise PlottyJobError(f"Failed to save job metadata: {e}")

    def find_job(self, name: str) -> str:
        """Find job ID by name.

        Args:
            name: Job name

        Returns:
            Job ID

        Raises:
            PlottyJobError: If job not found
        """
        job_path = self.jobs_dir / name
        if not job_path.exists():
            raise PlottyJobError(f"Job '{name}' not found")

        job_json_path = job_path / "job.json"
        if not job_json_path.exists():
            raise PlottyJobError(f"Job metadata for '{name}' not found")

        try:
            with open(job_json_path, encoding="utf-8") as f:
                job_data = json.load(f)
                return job_data.get("id", name)
        except (json.JSONDecodeError, OSError) as e:
            raise PlottyJobError(f"Failed to read job ID for '{name}': {e}")

    def get_job(self, name: str) -> Dict[str, Any]:
        """Get complete job data by name.

        Args:
            name: Job name

        Returns:
            Complete job dictionary

        Raises:
            PlottyJobError: If job not found
        """
        return self.get_job_status(name)
