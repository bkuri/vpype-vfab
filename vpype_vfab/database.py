"""Streamlined vfab database integration."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vpype import Document

from vpype_vfab.config import VfabConfig
from vpype_vfab.exceptions import VfabJobError
from vpype_vfab.utils import save_document_for_plotty


class StreamlinedVfabIntegration:
    """Streamlined vfab integration with simplified job management."""

    def __init__(self, workspace_path: Optional[str] = None) -> None:
        """Initialize streamlined vfab integration.

        Args:
            workspace_path: Optional path to vfab workspace directory
        """
        self.config_manager = VfabConfig(workspace_path)
        self.workspace = self.config_manager.workspace_path
        self.jobs_dir = self.workspace / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.queue_dir = self.workspace / "queue"
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, name: str, file_type: str = "job") -> Path:
        """Get standardized file path for job or queue files.

        Args:
            name: Job or file name
            file_type: Type of file ("job" or "queue")

        Returns:
            Path to the file
        """
        if file_type == "job":
            return self.jobs_dir / name / "job.json"
        elif file_type == "queue":
            return self.queue_dir / f"{name}.notify"
        else:
            raise ValueError(f"Unknown file type: {file_type}")

    def _load_json_file(self, name: str, file_type: str = "job") -> Dict[str, Any]:
        """Generic JSON file loader with error handling.

        Args:
            name: File name
            file_type: Type of file ("job" or "queue")

        Returns:
            Loaded JSON data

        Raises:
            VfabJobError: If file cannot be loaded
        """
        file_path = self._get_file_path(name, file_type)

        if not file_path.exists():
            raise VfabJobError(f"{file_type.title()} '{name}' not found")

        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise VfabJobError(f"Failed to load {file_type} '{name}': {e}")

    def _save_json_file(
        self, name: str, data: Dict[str, Any], file_type: str = "job"
    ) -> None:
        """Generic JSON file saver with error handling.

        Args:
            name: File name
            data: Data to save
            file_type: Type of file ("job" or "queue")

        Raises:
            VfabJobError: If file cannot be saved
        """
        file_path = self._get_file_path(name, file_type)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, json.JSONDecodeError) as e:
            raise VfabJobError(f"Failed to save {file_type} '{name}': {e}")

    def add_job(
        self,
        document: Document,
        name: str,
        preset: str = "fast",
        paper: str = "A4",
        priority: int = 1,
        pen_mapping: Optional[Dict] = None,
    ) -> str:
        """Add job to vfab system with unified approach.

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
            VfabJobError: If job creation fails
        """
        try:
            # Create unified job metadata
            job_data = self._create_job_metadata(name, preset, paper, priority)

            # Save job files using existing utility
            svg_path, job_json_path = save_document_for_plotty(
                document, self.jobs_dir / name, name
            )

            # Update job.json with additional metadata
            existing_job_data = self._load_json_file(name, "job")
            job_data.update(existing_job_data)
            self._save_json_file(name, job_data, "job")

            # Notify vfab via simple file system queue
            self._notify_plotty(name, job_data)

            return name

        except Exception as e:
            raise VfabJobError(f"Failed to create job '{name}': {e}")

    def queue_job(self, name: str, priority: int = 1) -> None:
        """Queue existing job for plotting.

        Args:
            name: Job name to queue
            priority: Job priority

        Raises:
            VfabJobError: If job queuing fails
        """
        try:
            job_data = self.load_job(name)

            # Update job state
            job_data["state"] = "QUEUED"
            job_data["queued_at"] = datetime.now(timezone.utc).isoformat()
            job_data["priority"] = priority

            # Save updated metadata
            self.save_job(name, job_data)

            # Notify vfab
            self._notify_plotty(name, job_data)

        except Exception as e:
            raise VfabJobError(f"Failed to queue job '{name}': {e}")

    def load_job(self, name: str) -> Dict[str, Any]:
        """Load job data by name.

        Args:
            name: Job name

        Returns:
            Job data dictionary

        Raises:
            VfabJobError: If job not found
        """
        return self._load_json_file(name, "job")

    def save_job(self, name: str, job_data: Dict[str, Any]) -> None:
        """Save job data.

        Args:
            name: Job name
            job_data: Job data dictionary

        Raises:
            VfabJobError: If save fails
        """
        self._save_json_file(name, job_data, "job")

    def remove_job(self, name: str) -> None:
        """Remove job from vfab system.

        Args:
            name: Job name to remove

        Raises:
            VfabJobError: If job removal fails
        """
        job_path = self.jobs_dir / name

        if not job_path.exists():
            raise VfabJobError(f"Job '{name}' not found")

        try:
            shutil.rmtree(job_path)
        except OSError as e:
            raise VfabJobError(f"Failed to remove job '{name}': {e}")

    def list_jobs(
        self, state: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List vfab jobs.

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

            try:
                job_data = self.load_job(job_path.name)

                # Filter by state if specified
                if state and job_data.get("state") != state:
                    continue

                jobs.append(job_data)

                # Apply limit if specified
                if limit and len(jobs) >= limit:
                    break

            except VfabJobError:
                # Skip invalid jobs
                continue

        return jobs

    def get_job_status(self, name: str) -> Dict[str, Any]:
        """Get status of a specific job.

        Args:
            name: Job name

        Returns:
            Job status dictionary

        Raises:
            VfabJobError: If job not found
        """
        return self.load_job(name)

    def find_job(self, name: str) -> str:
        """Find job ID by name.

        Args:
            name: Job name

        Returns:
            Job ID

        Raises:
            VfabJobError: If job not found
        """
        job_data = self.load_job(name)
        return job_data.get("id", name)

    def get_job(self, name: str) -> Dict[str, Any]:
        """Get complete job data by name.

        Args:
            name: Job name

        Returns:
            Complete job dictionary

        Raises:
            VfabJobError: If job not found
        """
        return self.load_job(name)

    def _create_job_metadata(
        self, name: str, preset: str, paper: str, priority: int
    ) -> Dict[str, Any]:
        """Create standardized job metadata.

        Args:
            name: Job name
            preset: Optimization preset
            paper: Paper size
            priority: Job priority

        Returns:
            Job metadata dictionary
        """
        return {
            "id": name,
            "name": name,
            "paper": paper,
            "state": "NEW",
            "priority": priority,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "created_by": "vpype-plotty",
                "source": "vpype document",
                "preset": preset,
                "version": "streamlined",
            },
        }

    def _notify_plotty(self, name: str, job_data: Dict[str, Any]) -> None:
        """Notify vfab about job changes via simple file system queue.

        Args:
            name: Job name
            job_data: Job data
        """
        try:
            notification = {
                "job": name,
                "state": job_data.get("state"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "update",
            }

            self._save_json_file(name, notification, "queue")

        except VfabJobError:
            # Queue notification is optional - don't fail if it doesn't work
            pass

    def _plotty_available(self) -> bool:
        """Check if vfab is available (for backward compatibility)."""
        try:
            import plotty  # noqa: F401

            return True
        except ImportError:
            return False

    def delete_job(self, name: str) -> None:
        """Delete job by name (alias for remove_job for backward compatibility)."""
        self.remove_job(name)

    def _save_job_metadata(self, job_path: str, job_data: Dict[str, Any]) -> None:
        """Save job metadata (alias for _save_json_file for backward compatibility)."""
        from pathlib import Path

        # Extract job name from path for compatibility with abstracted methods
        path = Path(job_path)
        job_name = path.name

        # Check if this is an absolute path or contains subdirectories
        if path.is_absolute():
            # This is an absolute path - use it directly
            full_path = path
        elif "/" in str(path) or "\\" in str(path):
            # This contains subdirectories - treat as relative to jobs_dir
            full_path = self.jobs_dir / path
        else:
            # This is just a job name - use the abstracted save method
            self._save_json_file(job_name, job_data, "job")
            return

        # Create the full directory structure
        full_path.mkdir(parents=True, exist_ok=True)
        file_path = full_path / "job.json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2)
        except (OSError, json.JSONDecodeError) as e:
            raise VfabJobError(f"Failed to save job '{job_name}': {e}")


# Maintain backward compatibility
PlottyIntegration = StreamlinedVfabIntegration
