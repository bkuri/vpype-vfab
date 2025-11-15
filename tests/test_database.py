"""Test vfab database integration."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from vpype import Document

from src.exceptions import PlottyJobError


class TestPlottyIntegration:
    """Test vfab integration."""

    def test_init_with_workspace_path(self):
        """Test initialization with explicit workspace path."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)
            assert plotty.workspace == Path(temp_dir)
            assert plotty.jobs_dir == Path(temp_dir) / "jobs"

    def test_vfab_available_true(self):
        """Test vfab availability when installed."""
        from src.database import PlottyIntegration

        with patch.dict(
            "sys.modules",
            {
                "plotty": Mock(),
                "plotty.fsm": Mock(),
                "plotty.models": Mock(),
            },
        ):
            plotty = PlottyIntegration()
            assert plotty._plotty_available() is True

    def test_add_job_with_plotty(self):
        """Test adding job with vfab integration."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)
            document = Document()
            job_id = plotty.add_job(document, "test_job", "fast", "A4")

            assert job_id == "test_job"

            # Verify job was created
            job_path = plotty.jobs_dir / "test_job"
            assert job_path.exists()
            assert (job_path / "src.svg").exists()
            assert (job_path / "job.json").exists()

            # Verify job metadata
            with open(job_path / "job.json", "r", encoding="utf-8") as f:
                job_data = json.load(f)

            assert job_data["name"] == "test_job"
            assert job_data["paper"] == "A4"
            assert job_data["state"] == "NEW"
            assert "created_at" in job_data
            assert "updated_at" in job_data

    def test_queue_job(self):
        """Test queuing existing job."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            # First create a job
            document = Document()
            plotty.add_job(document, "test_job", "fast", "A4")

            # Queue the job
            plotty.queue_job("test_job", priority=2)

            # Verify job state was updated
            job_data = plotty.get_job_status("test_job")
            assert job_data["state"] == "QUEUED"
            assert job_data["priority"] == 2
            assert "queued_at" in job_data

    def test_queue_nonexistent_job(self):
        """Test queuing non-existent job."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            with pytest.raises(PlottyJobError):
                plotty.queue_job("nonexistent_job")

    def test_get_job_status(self):
        """Test getting job status."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            # First create a job
            document = Document()
            plotty.add_job(document, "test_job", "fast", "A4")

            # Get job status
            job_data = plotty.get_job_status("test_job")
            assert job_data["name"] == "test_job"
            assert job_data["state"] == "NEW"
            assert job_data["paper"] == "A4"

    def test_get_job_status_nonexistent(self):
        """Test getting status of non-existent job."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            with pytest.raises(PlottyJobError):
                plotty.get_job_status("nonexistent_job")

    def test_list_jobs(self):
        """Test listing jobs."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            # Create multiple jobs
            for i in range(3):
                document = Document()
                plotty.add_job(document, f"job_{i}", "fast", "A4")

            # List jobs
            jobs = plotty.list_jobs()
            assert len(jobs) == 3
            job_names = [job["name"] for job in jobs]
            assert "job_0" in job_names
            assert "job_1" in job_names
            assert "job_2" in job_names

    def test_list_jobs_empty(self):
        """Test listing jobs when none exist."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            jobs = plotty.list_jobs()
            assert jobs == []

    def test_delete_job(self):
        """Test deleting existing job."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            # First create a job
            document = Document()
            plotty.add_job(document, "test_job", "fast", "A4")

            # Verify job exists
            job_path = plotty.jobs_dir / "test_job"
            assert job_path.exists()

            # Delete the job
            plotty.delete_job("test_job")

            # Verify job was deleted
            assert not job_path.exists()

    def test_delete_nonexistent_job(self):
        """Test deleting non-existent job."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)

            with pytest.raises(PlottyJobError):
                plotty.delete_job("nonexistent_job")

    def test_save_job_metadata(self):
        """Test saving job metadata."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)
            job_path = plotty.jobs_dir / "test_job"

            job_data = {
                "id": "test_job",
                "name": "test_job",
                "state": "NEW",
                "metadata": {"test": "value"},
            }

            # Save metadata
            plotty._save_job_metadata(str(job_path), job_data)

            # Verify metadata was saved
            job_json_path = job_path / "job.json"
            assert job_json_path.exists()

            with open(job_json_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data["id"] == "test_job"
            assert saved_data["name"] == "test_job"
            assert saved_data["state"] == "NEW"
            assert saved_data["metadata"]["test"] == "value"

    def test_save_job_metadata_creates_directory(self):
        """Test that _save_job_metadata creates directory if needed."""
        from src.database import PlottyIntegration

        with tempfile.TemporaryDirectory() as temp_dir:
            plotty = PlottyIntegration(temp_dir)
            job_path = plotty.jobs_dir / "subdir" / "test_job"

            job_data = {"id": "test_job", "name": "test_job"}

            # Save metadata (should create directory)
            plotty._save_job_metadata(str(job_path), job_data)

            # Verify directory and file were created
            assert job_path.exists()
            assert (job_path / "job.json").exists()
