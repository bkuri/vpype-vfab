"""Tests for streamlined vfab database integration."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Mock vpype imports to avoid Qt display issues
sys.modules["vpype"] = MagicMock()
sys.modules["vpype.Document"] = MagicMock()

# Import after mocking
from src.database import StreamlinedPlottyIntegration
from src.exceptions import PlottyJobError


# Create a mock Document class for testing
class MockDocument:
    def __init__(self):
        self.layers = []

    def add(self, line):
        self.layers.append(line)


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
    def sample_document(self):
        """Create sample vpype document for testing."""
        doc = MockDocument()
        doc.add([(0, 0), (10, 10), (20, 0)])
        doc.add([(5, 5), (15, 15)])
        return doc

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

    def test_add_job_success(self, integration, sample_document):
        """Test successful job addition."""
        job_id = integration.add_job(
            sample_document, "test_job", preset="fast", paper="A4", priority=1
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

    def test_add_job_with_pen_mapping(self, integration, sample_document):
        """Test job addition with custom pen mapping."""
        pen_mapping = {"1": "black", "2": "red"}

        job_id = integration.add_job(
            sample_document, "mapped_job", pen_mapping=pen_mapping
        )

        assert job_id == "mapped_job"

        job_data = integration.load_job("mapped_job")
        # Pen mapping should be saved in the job data
        assert "pen_mapping" in job_data or "layers" in job_data

    def test_add_job_failure(self, integration, sample_document):
        """Test job addition failure handling."""
        # Mock save_document_for_plotty to raise an exception
        with patch(
            "src.database.save_document_for_plotty",
            side_effect=Exception("Save failed"),
        ):
            with pytest.raises(PlottyJobError, match="Failed to create job 'test_job'"):
                integration.add_job(sample_document, "test_job")

    def test_queue_job_success(self, integration, sample_document):
        """Test successful job queuing."""
        # First add a job
        integration.add_job(sample_document, "queue_test", priority=2)

        # Then queue it
        integration.queue_job("queue_test", priority=1)

        # Check job state was updated
        job_data = integration.load_job("queue_test")
        assert job_data["state"] == "QUEUED"
        assert job_data["priority"] == 1
        assert "queued_at" in job_data

    def test_queue_job_not_found(self, integration):
        """Test queuing non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.queue_job("nonexistent")

    def test_queue_job_failure(self, integration):
        """Test job queuing failure handling."""
        # Mock load_job to raise an exception
        with patch.object(
            integration, "load_job", side_effect=Exception("Load failed")
        ):
            with pytest.raises(PlottyJobError, match="Failed to queue job 'test'"):
                integration.queue_job("test")

    def test_load_job_success(self, integration, sample_document):
        """Test successful job loading."""
        # Add a job first
        integration.add_job(sample_document, "load_test")

        # Load the job
        job_data = integration.load_job("load_test")

        assert job_data["id"] == "load_test"
        assert job_data["name"] == "load_test"
        assert job_data["state"] == "NEW"

    def test_load_job_not_found(self, integration):
        """Test loading non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.load_job("nonexistent")

    def test_load_job_invalid_json(self, integration):
        """Test loading job with invalid JSON."""
        # Create job directory and invalid JSON file
        job_dir = integration.jobs_dir / "invalid_json"
        job_dir.mkdir(parents=True, exist_ok=True)
        job_json = job_dir / "job.json"
        job_json.write_text("invalid json content")

        with pytest.raises(PlottyJobError, match="Failed to load job 'invalid_json'"):
            integration.load_job("invalid_json")

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

    def test_save_job_failure(self, integration):
        """Test job saving failure handling."""
        job_data = {"id": "fail_test"}

        # Mock open to raise an exception
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(PlottyJobError, match="Failed to save job 'fail_test'"):
                integration.save_job("fail_test", job_data)

    def test_remove_job_success(self, integration, sample_document):
        """Test successful job removal."""
        # Add a job first
        integration.add_job(sample_document, "remove_test")

        # Verify job exists
        job_path = integration.jobs_dir / "remove_test"
        assert job_path.exists()

        # Remove the job
        integration.remove_job("remove_test")

        # Verify job was removed
        assert not job_path.exists()

    def test_remove_job_not_found(self, integration):
        """Test removing non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.remove_job("nonexistent")

    def test_remove_job_failure(self, integration):
        """Test job removal failure handling."""
        # Mock shutil.rmtree to raise an exception
        with patch(
            "src.database.shutil.rmtree",
            side_effect=OSError("Permission denied"),
        ):
            with pytest.raises(PlottyJobError, match="Failed to remove job 'test'"):
                integration.remove_job("test")

    def test_list_jobs_all(self, integration, sample_document):
        """Test listing all jobs."""
        # Add multiple jobs
        integration.add_job(sample_document, "job1", priority=1)
        integration.add_job(sample_document, "job2", priority=2)
        integration.add_job(sample_document, "job3", priority=3)

        jobs = integration.list_jobs()

        assert len(jobs) == 3
        job_names = [job["name"] for job in jobs]
        assert "job1" in job_names
        assert "job2" in job_names
        assert "job3" in job_names

    def test_list_jobs_with_state_filter(self, integration, sample_document):
        """Test listing jobs filtered by state."""
        # Add jobs
        integration.add_job(sample_document, "new_job", priority=1)
        integration.add_job(sample_document, "queue_job", priority=2)

        # Queue one job
        integration.queue_job("queue_job")

        # Filter by state
        new_jobs = integration.list_jobs(state="NEW")
        queued_jobs = integration.list_jobs(state="QUEUED")

        assert len(new_jobs) == 1
        assert new_jobs[0]["name"] == "new_job"

        assert len(queued_jobs) == 1
        assert queued_jobs[0]["name"] == "queue_job"

    def test_list_jobs_with_limit(self, integration, sample_document):
        """Test listing jobs with limit."""
        # Add multiple jobs
        for i in range(5):
            integration.add_job(sample_document, f"job{i}", priority=i)

        # List with limit
        jobs = integration.list_jobs(limit=3)

        assert len(jobs) == 3

    def test_list_jobs_skip_invalid(self, integration):
        """Test listing jobs skips invalid job directories."""
        # Create invalid job directory (no job.json)
        invalid_dir = integration.jobs_dir / "invalid"
        invalid_dir.mkdir(parents=True, exist_ok=True)

        # Create valid job
        doc = Document()
        doc.add(vpype.Line([(0, 0), (1, 1)]))
        integration.add_job(doc, "valid")

        jobs = integration.list_jobs()

        # Should only return valid job
        assert len(jobs) == 1
        assert jobs[0]["name"] == "valid"

    def test_get_job_status(self, integration, sample_document):
        """Test getting job status."""
        integration.add_job(sample_document, "status_test")

        status = integration.get_job_status("status_test")

        assert status["name"] == "status_test"
        assert status["state"] == "NEW"

    def test_get_job_status_not_found(self, integration):
        """Test getting status of non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.get_job_status("nonexistent")

    def test_find_job(self, integration, sample_document):
        """Test finding job by name."""
        integration.add_job(sample_document, "find_test")

        job_id = integration.find_job("find_test")

        assert job_id == "find_test"

    def test_find_job_not_found(self, integration):
        """Test finding non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.find_job("nonexistent")

    def test_get_job(self, integration, sample_document):
        """Test getting complete job data."""
        integration.add_job(sample_document, "get_test", preset="quality")

        job_data = integration.get_job("get_test")

        assert job_data["name"] == "get_test"
        assert job_data["metadata"]["preset"] == "quality"
        assert job_data["metadata"]["version"] == "streamlined"

    def test_get_job_not_found(self, integration):
        """Test getting non-existent job."""
        with pytest.raises(PlottyJobError, match="Job 'nonexistent' not found"):
            integration.get_job("nonexistent")

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
        """Test vfab notification success."""
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
        """Test vfab notification failure (should not raise)."""
        # Mock queue_dir to cause permission error
        integration.queue_dir = Path("/nonexistent/directory")

        # This should not raise an exception
        integration._notify_plotty("test", {"state": "QUEUED"})

    def test_backward_compatibility_alias(self):
        """Test that PlottyIntegration alias works."""
        from src.database import PlottyIntegration

        # Should be the same class
        assert PlottyIntegration is StreamlinedPlottyIntegration

    def test_add_job_with_all_parameters(self, integration, sample_document):
        """Test job addition with all optional parameters."""
        pen_mapping = {"1": "blue", "2": "green"}

        job_id = integration.add_job(
            sample_document,
            "full_test",
            preset="quality",
            paper="A3",
            priority=10,
            pen_mapping=pen_mapping,
        )

        assert job_id == "full_test"

        job_data = integration.load_job("full_test")
        assert job_data["paper"] == "A3"
        assert job_data["priority"] == 10
        assert job_data["metadata"]["preset"] == "quality"

    def test_job_state_transitions(self, integration, sample_document):
        """Test job state transitions."""
        # Add job (should be NEW)
        integration.add_job(sample_document, "state_test")
        assert integration.get_job("state_test")["state"] == "NEW"

        # Queue job (should be QUEUED)
        integration.queue_job("state_test")
        assert integration.get_job("state_test")["state"] == "QUEUED"

        # Verify timestamps
        job_data = integration.get_job("state_test")
        assert "created_at" in job_data
        assert "queued_at" in job_data
