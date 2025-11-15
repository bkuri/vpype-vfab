"""Simple tests for streamlined ploTTY database integration."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Mock vpype imports to avoid Qt display issues
import sys

sys.modules["vpype"] = MagicMock()
sys.modules["vpype.Document"] = MagicMock()

from src.database import StreamlinedPlottyIntegration
from src.exceptions import PlottyJobError


class TestStreamlinedPlottyIntegration:
    """Test cases for StreamlinedPlottyIntegration."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def integration(self, temp_workspace):
        """Create integration instance with temporary workspace."""
        return StreamlinedPlottyIntegration(str(temp_workspace))

    @pytest.fixture
    def mock_document(self):
        """Create mock vpype document for testing."""
        return MagicMock()

    def test_init_default_workspace(self):
        """Test initialization with default workspace."""
        integration = StreamlinedPlottyIntegration()
        assert integration.workspace.exists()
        assert integration.jobs_dir.exists()
        assert integration.queue_dir.exists()

    def test_init_custom_workspace(self, temp_workspace):
        """Test initialization with custom workspace."""
        integration = StreamlinedPlottyIntegration(str(temp_workspace))
        assert integration.workspace == temp_workspace
        assert integration.jobs_dir == temp_workspace / "jobs"
        assert integration.queue_dir == temp_workspace / "queue"

    def test_add_job_success(self, integration, mock_document):
        """Test successful job addition."""
        # Mock the save_document_for_plotty function
        with patch("src.database.save_document_for_plotty") as mock_save:
            mock_save.return_value = (Path("/fake/test.svg"), Path("/fake/job.json"))
            # Mock the job.json content
            with open(mock_save.return_value[1], "w") as f:
                json.dump({"layers": []}, f)

            job_id = integration.add_job(
                mock_document, "test_job", preset="fast", paper="A4", priority=1
            )

            assert job_id == "test_job"

            # Check job directory was created
            job_dir = integration.jobs_dir / "test_job"
            assert job_dir.exists()

    def test_load_job_not_found(self, integration):
        """Test loading non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.load_job("nonexistent")

    def test_save_job_success(self, integration):
        """Test successful job saving."""
        job_data = {
            "id": "save_test",
            "name": "save_test",
            "state": "SAVED",
            "metadata": {"test": True},
        }

        integration.save_job("save_test", job_data)

        # Verify job was saved
        loaded_data = integration.load_job("save_test")
        assert loaded_data == job_data

    def test_remove_job_success(self, integration):
        """Test successful job removal."""
        # Create a job directory first
        job_path = integration.jobs_dir / "remove_test"
        job_path.mkdir(parents=True, exist_ok=True)

        # Verify job exists
        assert job_path.exists()

        # Remove the job
        integration.remove_job("remove_test")

        # Verify job was removed
        assert not job_path.exists()

    def test_remove_job_not_found(self, integration):
        """Test removing non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.remove_job("nonexistent")

    def test_list_jobs_empty(self, integration):
        """Test listing jobs when none exist."""
        jobs = integration.list_jobs()
        assert jobs == []

    def test_list_jobs_with_state_filter(self, integration):
        """Test listing jobs filtered by state."""
        # Create mock job data
        job_data = {"name": "test_job", "state": "NEW"}
        integration.save_job("test_job", job_data)

        # Filter by state
        new_jobs = integration.list_jobs(state="NEW")
        queued_jobs = integration.list_jobs(state="QUEUED")

        assert len(new_jobs) == 1
        assert new_jobs[0]["name"] == "test_job"

        assert len(queued_jobs) == 0

    def test_get_job_status_not_found(self, integration):
        """Test getting status of non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.get_job_status("nonexistent")

    def test_find_job_not_found(self, integration):
        """Test finding non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.find_job("nonexistent")

    def test_create_job_metadata(self, integration):
        """Test job metadata creation."""
        metadata = integration._create_job_metadata("test", "fast", "A3", 5)

        assert metadata["id"] == "test"
        assert metadata["name"] == "test"
        assert metadata["paper"] == "A3"
        assert metadata["state"] == "NEW"
        assert metadata["priority"] == 5
        assert metadata["metadata"]["preset"] == "fast"
        assert metadata["metadata"]["version"] == "streamlined"
        assert metadata["metadata"]["created_by"] == "vpype-plotty"
        assert metadata["metadata"]["source"] == "vpype document"
        assert "created_at" in metadata

    def test_notify_plotty_success(self, integration):
        """Test ploTTY notification success."""
        job_data = {"state": "QUEUED", "name": "test"}

        integration._notify_plotty("test", job_data)

        # Check notification file was created
        notify_file = integration.queue_dir / "test.notify"
        assert notify_file.exists()

        notification = json.loads(notify_file.read_text())
        assert notification["job"] == "test"
        assert notification["state"] == "QUEUED"
        assert notification["action"] == "update"
        assert "timestamp" in notification

    def test_notify_plotty_failure(self, integration):
        """Test ploTTY notification failure (should not raise)."""
        # Mock queue_dir to cause permission error
        integration.queue_dir = Path("/nonexistent/directory")

        # This should not raise an exception
        integration._notify_plotty("test", {"state": "QUEUED"})

    def test_backward_compatibility_alias(self):
        """Test that PlottyIntegration alias works."""
        from src.database import PlottyIntegration

        # Should be the same class
        assert PlottyIntegration is StreamlinedPlottyIntegration

    def test_queue_job_success(self, integration):
        """Test successful job queuing."""
        # Create a job first
        job_data = {"name": "queue_test", "state": "NEW"}
        integration.save_job("queue_test", job_data)

        # Then queue it
        integration.queue_job("queue_test", priority=1)

        # Check job state was updated
        updated_job_data = integration.load_job("queue_test")
        assert updated_job_data["state"] == "QUEUED"
        assert updated_job_data["priority"] == 1
        assert "queued_at" in updated_job_data

    def test_queue_job_not_found(self, integration):
        """Test queuing non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.queue_job("nonexistent")
