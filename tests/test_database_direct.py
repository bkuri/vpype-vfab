"""Direct tests for streamlined ploTTY database integration."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to sys.path to import directly
sys.path.insert(0, "/home/bk/source/vpype-plotty")

# Mock vpype imports to avoid Qt display issues
mock_vpype = MagicMock()
mock_vpype.__version__ = "1.15.0"
sys.modules["vpype"] = mock_vpype
sys.modules["vpype.Document"] = MagicMock()

# Import database module directly
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
            # Create temporary files for mock return
            temp_svg = integration.jobs_dir / "test_job" / "test.svg"
            temp_json = integration.jobs_dir / "test_job" / "job.json"
            temp_svg.parent.mkdir(parents=True, exist_ok=True)

            # Create mock job.json content
            mock_job_data = {"layers": [{"id": 1, "color": "black"}]}
            temp_json.write_text(json.dumps(mock_job_data))

            mock_save.return_value = (temp_svg, temp_json)

            job_id = integration.add_job(
                mock_document, "test_job", preset="fast", paper="A4", priority=1
            )

            assert job_id == "test_job"

            # Check job directory was created
            job_dir = integration.jobs_dir / "test_job"
            assert job_dir.exists()

            # Check job.json exists and has correct metadata
            job_json = job_dir / "job.json"
            assert job_json.exists()

            job_data = json.loads(job_json.read_text())
            assert job_data["id"] == "test_job"
            assert job_data["name"] == "test_job"
            assert job_data["paper"] == "A4"
            assert job_data["state"] == "NEW"
            assert job_data["priority"] == 1
            assert job_data["metadata"]["preset"] == "fast"
            assert job_data["metadata"]["version"] == "streamlined"

    def test_load_job_success(self, integration):
        """Test successful job loading."""
        # Create a job first
        job_data = {"name": "load_test", "state": "NEW", "id": "load_test"}
        integration.save_job("load_test", job_data)

        # Load the job
        loaded_data = integration.load_job("load_test")

        assert loaded_data["name"] == "load_test"
        assert loaded_data["state"] == "NEW"

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

    def test_list_jobs_with_jobs(self, integration):
        """Test listing jobs when jobs exist."""
        # Create multiple jobs
        for i in range(3):
            job_data = {"name": f"job{i}", "state": "NEW", "id": f"job{i}"}
            integration.save_job(f"job{i}", job_data)

        jobs = integration.list_jobs()
        assert len(jobs) == 3
        job_names = [job["name"] for job in jobs]
        assert "job0" in job_names
        assert "job1" in job_names
        assert "job2" in job_names

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

    def test_get_job_status_success(self, integration):
        """Test getting job status successfully."""
        job_data = {"name": "status_test", "state": "NEW"}
        integration.save_job("status_test", job_data)

        status = integration.get_job_status("status_test")

        assert status["name"] == "status_test"
        assert status["state"] == "NEW"

    def test_get_job_status_not_found(self, integration):
        """Test getting status of non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.get_job_status("nonexistent")

    def test_find_job_success(self, integration):
        """Test finding job successfully."""
        job_data = {"name": "find_test", "id": "found_id", "state": "NEW"}
        integration.save_job("find_test", job_data)

        job_id = integration.find_job("find_test")

        assert job_id == "found_id"

    def test_find_job_not_found(self, integration):
        """Test finding non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.find_job("nonexistent")

    def test_get_job_success(self, integration):
        """Test getting complete job data successfully."""
        job_data = {"name": "get_test", "state": "NEW", "metadata": {"test": True}}
        integration.save_job("get_test", job_data)

        retrieved_data = integration.get_job("get_test")

        assert retrieved_data["name"] == "get_test"
        assert retrieved_data["metadata"]["test"] is True

    def test_get_job_not_found(self, integration):
        """Test getting non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.get_job("nonexistent")

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

    def test_list_jobs_with_limit(self, integration):
        """Test listing jobs with limit."""
        # Create multiple jobs
        for i in range(5):
            job_data = {"name": f"job{i}", "state": "NEW", "id": f"job{i}"}
            integration.save_job(f"job{i}", job_data)

        # List with limit
        jobs = integration.list_jobs(limit=3)

        assert len(jobs) == 3

    def test_list_jobs_skip_invalid(self, integration):
        """Test listing jobs skips invalid job directories."""
        # Create invalid job directory (no job.json)
        invalid_dir = integration.jobs_dir / "invalid"
        invalid_dir.mkdir(parents=True, exist_ok=True)

        # Create valid job
        job_data = {"name": "valid", "state": "NEW", "id": "valid"}
        integration.save_job("valid", job_data)

        jobs = integration.list_jobs()

        # Should only return valid job
        assert len(jobs) == 1
        assert jobs[0]["name"] == "valid"
