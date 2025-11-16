"""Enhanced tests for database.py to improve coverage."""

import sys
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Set up Qt mocks before any imports
sys.path.insert(0, "/home/bk/source/vpype-vfab")
from tests.conftest import setup_qt_mocks

setup_qt_mocks()

from vpype_vfab.database import PlottyIntegration


class TestPlottyIntegrationEnhanced:
    """Enhanced tests for PlottyIntegration class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.plotty = PlottyIntegration(str(self.workspace))

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_with_custom_workspace(self):
        """Test initialization with custom workspace path."""
        custom_workspace = Path(self.temp_dir) / "custom_workspace"
        plotty = PlottyIntegration(str(custom_workspace))

        assert plotty.workspace == custom_workspace
        assert plotty.jobs_dir == custom_workspace / "jobs"
        assert plotty.jobs_dir.exists()

    def test_init_with_none_workspace(self):
        """Test initialization with None workspace (uses default)."""
        with patch("vpype_vfab.config.PlottyConfig") as mock_config:
            mock_workspace = Path("/mock/workspace")
            mock_config.return_value.workspace_path = mock_workspace

            plotty = PlottyIntegration(None)

            assert plotty.workspace == mock_workspace

    def test_vfab_available_true(self):
        """Test vfab availability when installed."""
        with patch.dict(
            "sys.modules",
            {
                "plotty": Mock(),
                "plotty.fsm": Mock(),
                "plotty.models": Mock(),
            },
        ):
            plotty = PlottyIntegration()
            assert plotty._vfab_available() is True

    def test_vfab_available_false(self):
        """Test vfab availability when not installed."""
        with patch.dict("sys.modules", {}, clear=True):
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                plotty = PlottyIntegration()
                assert plotty._vfab_available() is False

    def test_add_job_basic(self):
        """Test basic job addition."""
        # Create a simple document
        document = Mock()
        document.layers = {}

        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        assert job_id == "test_job"

        # Verify job directory was created
        job_dir = self.plotty.jobs_dir / job_id
        assert job_dir.exists()
        assert (job_dir / "vpype_vfab.svg").exists()
        assert (job_dir / "job.json").exists()

    def test_add_job_with_pen_mapping(self):
        """Test job addition with pen mapping."""
        document = Mock()
        document.layers = {1: Mock(), 2: Mock()}

        pen_mapping = {1: 1, 2: 2}
        job_id = self.plotty.add_job(
            document, "test_job", "fast", "A4", pen_mapping=pen_mapping
        )

        # Verify job metadata includes pen mapping
        job_file = self.plotty.jobs_dir / job_id / "job.json"
        with open(job_file, "r") as f:
            job_data = json.load(f)

        assert job_data["pen_mapping"] == pen_mapping

    def test_add_job_with_priority(self):
        """Test job addition with priority."""
        document = Mock()
        document.layers = {}

        job_id = self.plotty.add_job(document, "test_job", "fast", "A4", priority=5)

        # Verify job metadata includes priority
        job_file = self.plotty.jobs_dir / job_id / "job.json"
        with open(job_file, "r") as f:
            job_data = json.load(f)

        assert job_data["priority"] == 5

    def test_add_job_duplicate_id(self):
        """Test adding job with duplicate ID."""
        document = Mock()
        document.layers = {}

        # Add first job
        job_id1 = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Add second job with same ID - should handle gracefully
        job_id2 = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Should create unique ID
        assert job_id1 == "test_job"
        assert job_id2 != job_id1

    def test_get_job_exists(self):
        """Test getting existing job."""
        # Create a job first
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Get the job
        job = self.plotty.get_job(job_id)

        assert job is not None
        assert job["id"] == job_id
        assert job["name"] == "test_job"

    def test_get_job_not_exists(self):
        """Test getting non-existing job."""
        job = self.plotty.get_job("nonexistent_job")
        assert job is None

    def test_get_job_corrupted_file(self):
        """Test getting job with corrupted JSON file."""
        # Create job directory and corrupted file
        job_dir = self.plotty.jobs_dir / "corrupted_job"
        job_dir.mkdir(parents=True, exist_ok=True)

        job_file = job_dir / "job.json"
        with open(job_file, "w") as f:
            f.write("invalid json content")

        # Should handle corrupted file gracefully
        job = self.plotty.get_job("corrupted_job")
        assert job is None

    def test_list_jobs_empty(self):
        """Test listing jobs when none exist."""
        jobs = self.plotty.list_jobs()
        assert jobs == []

    def test_list_jobs_with_jobs(self):
        """Test listing jobs when some exist."""
        # Create multiple jobs
        document = Mock()
        document.layers = {}

        job1_id = self.plotty.add_job(document, "job1", "fast", "A4")
        job2_id = self.plotty.add_job(document, "job2", "slow", "A3")

        jobs = self.plotty.list_jobs()

        assert len(jobs) == 2
        job_ids = [job["id"] for job in jobs]
        assert job1_id in job_ids
        assert job2_id in job_ids

    def test_list_jobs_with_state_filter(self):
        """Test listing jobs with state filter."""
        # Create jobs with different states
        document = Mock()
        document.layers = {}

        job1_id = self.plotty.add_job(document, "job1", "fast", "A4")
        job2_id = self.plotty.add_job(document, "job2", "slow", "A3")

        # Modify job states
        self._set_job_state(job1_id, "completed")
        self._set_job_state(job2_id, "running")

        # Filter by state
        running_jobs = self.plotty.list_jobs(state="running")
        assert len(running_jobs) == 1
        assert running_jobs[0]["id"] == job2_id

    def test_list_jobs_with_limit(self):
        """Test listing jobs with limit."""
        # Create multiple jobs
        document = Mock()
        document.layers = {}

        for i in range(5):
            self.plotty.add_job(document, f"job{i}", "fast", "A4")

        # List with limit
        jobs = self.plotty.list_jobs(limit=3)
        assert len(jobs) == 3

    def test_find_job_by_name(self):
        """Test finding job by name."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Find by name
        found_id = self.plotty.find_job("test_job")
        assert found_id == job_id

    def test_find_job_by_id(self):
        """Test finding job by ID."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Find by ID
        found_id = self.plotty.find_job(job_id)
        assert found_id == job_id

    def test_find_job_not_found(self):
        """Test finding non-existing job."""
        found_id = self.plotty.find_job("nonexistent")
        assert found_id is None

    def test_queue_job_exists(self):
        """Test queueing existing job."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Queue the job
        result = self.plotty.queue_job(job_id, priority=2)

        assert result is True

        # Verify state changed
        job = self.plotty.get_job(job_id)
        assert job["state"] == "QUEUED"
        assert job["priority"] == 2

    def test_queue_job_not_exists(self):
        """Test queueing non-existing job."""
        result = self.plotty.queue_job("nonexistent", priority=1)
        assert result is False

    def test_cancel_job_exists(self):
        """Test cancelling existing job."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Cancel the job
        result = self.plotty.cancel_job(job_id)

        assert result is True

        # Verify state changed
        job = self.plotty.get_job(job_id)
        assert job["state"] == "CANCELLED"

    def test_cancel_job_not_exists(self):
        """Test cancelling non-existing job."""
        result = self.plotty.cancel_job("nonexistent")
        assert result is False

    def test_delete_job_exists(self):
        """Test deleting existing job."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Delete the job
        result = self.plotty.delete_job(job_id)

        assert result is True

        # Verify job directory is gone
        job_dir = self.plotty.jobs_dir / job_id
        assert not job_dir.exists()

    def test_delete_job_not_exists(self):
        """Test deleting non-existing job."""
        result = self.plotty.delete_job("nonexistent")
        assert result is False

    def test_update_job_state_exists(self):
        """Test updating state of existing job."""
        # Create a job
        document = Mock()
        document.layers = {}
        job_id = self.plotty.add_job(document, "test_job", "fast", "A4")

        # Update state
        result = self.plotty.update_job_state(job_id, "RUNNING", "Test reason")

        assert result is True

        # Verify state changed
        job = self.plotty.get_job(job_id)
        assert job["state"] == "RUNNING"
        assert job["state_reason"] == "Test reason"

    def test_update_job_state_not_exists(self):
        """Test updating state of non-existing job."""
        result = self.plotty.update_job_state("nonexistent", "RUNNING")
        assert result is False

    def test_get_job_stats_empty(self):
        """Test getting job stats when no jobs exist."""
        stats = self.plotty.get_job_stats()

        assert stats["total"] == 0
        assert stats["pending"] == 0
        assert stats["running"] == 0
        assert stats["completed"] == 0
        assert stats["failed"] == 0

    def test_get_job_stats_with_jobs(self):
        """Test getting job stats with various job states."""
        # Create jobs with different states
        document = Mock()
        document.layers = {}

        job_ids = []
        for i, state in enumerate(["pending", "running", "completed", "failed"]):
            job_id = self.plotty.add_job(document, f"job{i}", "fast", "A4")
            self._set_job_state(job_id, state)
            job_ids.append(job_id)

        # Get stats
        stats = self.plotty.get_job_stats()

        assert stats["total"] == 4
        assert stats["pending"] == 1
        assert stats["running"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 1

    def test_workspace_creation_error(self):
        """Test handling of workspace creation errors."""
        with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError):
                PlottyIntegration("/invalid/path")

    def test_job_file_write_error(self):
        """Test handling of job file write errors."""
        document = Mock()
        document.layers = {}

        with patch("builtins.open", side_effect=OSError("Disk full")):
            with pytest.raises(OSError):
                self.plotty.add_job(document, "test_job", "fast", "A4")

    def test_invalid_preset_validation(self):
        """Test validation of invalid preset."""
        document = Mock()
        document.layers = {}

        # This should be handled by the validate_preset function in utils
        # but we test the integration here
        with patch(
            "vpype_vfab.utils.validate_preset",
            side_effect=ValueError("Invalid preset"),
        ):
            with pytest.raises(ValueError):
                self.plotty.add_job(document, "test_job", "invalid", "A4")

    def _set_job_state(self, job_id: str, state: str):
        """Helper method to set job state for testing."""
        job_file = self.plotty.jobs_dir / job_id / "job.json"
        if job_file.exists():
            with open(job_file, "r") as f:
                job_data = json.load(f)

            job_data["state"] = state
            job_data["updated_at"] = datetime.now(timezone.utc).isoformat()

            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)


class TestPlottyIntegrationEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_document_layers(self):
        """Test handling document with no layers."""
        document = Mock()
        document.layers = {}

        plotty = PlottyIntegration()
        job_id = plotty.add_job(document, "empty_job", "fast", "A4")

        assert job_id == "empty_job"

        # Verify job was created despite empty layers
        job = plotty.get_job(job_id)
        assert job is not None

    def test_very_long_job_name(self):
        """Test handling of very long job names."""
        document = Mock()
        document.layers = {}

        long_name = "a" * 1000  # Very long name
        plotty = PlottyIntegration()
        job_id = plotty.add_job(document, long_name, "fast", "A4")

        assert job_id == long_name

    def test_special_characters_in_job_name(self):
        """Test handling of special characters in job names."""
        document = Mock()
        document.layers = {}

        special_name = "test_job_特殊字符_🎨"
        plotty = PlottyIntegration()
        job_id = plotty.add_job(document, special_name, "fast", "A4")

        assert job_id == special_name

    def test_concurrent_job_creation(self):
        """Test concurrent job creation."""
        import threading

        document = Mock()
        document.layers = {}
        plotty = PlottyIntegration()

        results = []
        errors = []

        def create_job(index):
            try:
                job_id = plotty.add_job(
                    document, f"concurrent_job_{index}", "fast", "A4"
                )
                results.append(job_id)
            except Exception as e:
                errors.append(e)

        # Create multiple jobs concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_job, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all jobs were created successfully
        assert len(errors) == 0
        assert len(results) == 5
        assert len(set(results)) == 5  # All job IDs should be unique
