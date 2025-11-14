"""Qt-free tests for vpype_plotty.database module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import shutil
from pathlib import Path
import sys
import os
import tempfile
from datetime import datetime, timezone

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock external dependencies to avoid Qt issues
sys.modules["vpype"] = Mock()
mock_document = Mock()
sys.modules["vpype"].Document = mock_document

# Mock config module
mock_config = Mock()
mock_plotty_config = Mock()
mock_config.PlottyConfig = mock_plotty_config
sys.modules["vpype_plotty.config"] = mock_config

# Mock exceptions module
mock_exceptions = Mock()
mock_plotty_job_error = Exception
mock_exceptions.PlottyJobError = mock_plotty_job_error
sys.modules["vpype_plotty.exceptions"] = mock_exceptions

# Mock utils module
mock_utils = Mock()
mock_save_document = Mock(return_value=("/mock/path.svg", "/mock/path/job.json"))
mock_utils.save_document_for_plotty = mock_save_document
sys.modules["vpype_plotty.utils"] = mock_utils

# Now import the database module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "database", "/home/bk/source/vpype-plotty/vpype_plotty/database.py"
)
if spec is None:
    raise ImportError("Could not load database module")
database = importlib.util.module_from_spec(spec)
sys.modules["database"] = database  # Register in sys.modules for patching
spec.loader.exec_module(database)


class TestDatabaseQtFree:
    """Qt-free test suite for database module."""

    def test_init_with_workspace_path(self):
        """Test StreamlinedPlottyIntegration initialization with explicit workspace."""
        with patch("database.Path") as mock_path_class:
            # Mock workspace setup
            mock_workspace = MagicMock()
            mock_workspace.exists.return_value = True
            mock_workspace.is_dir.return_value = True
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_jobs_dir = MagicMock()
            mock_queue_dir = MagicMock()

            # Configure Path mock to return different values for different calls
            def path_side_effect(path_arg):
                if path_arg == "/test/workspace":
                    return mock_workspace
                elif "jobs" in str(path_arg):
                    return mock_jobs_dir
                elif "queue" in str(path_arg):
                    return mock_queue_dir
                return MagicMock()

            mock_path_class.side_effect = path_side_effect
            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration("/test/workspace")

            assert integration.workspace == mock_workspace
            assert integration.jobs_dir == mock_jobs_dir
            assert integration.queue_dir == mock_queue_dir

    def test_init_without_workspace_path(self):
        """Test StreamlinedPlottyIntegration initialization without explicit workspace."""
        with patch("database.Path") as mock_path_class:
            # Mock workspace setup
            mock_workspace = MagicMock()
            mock_workspace.exists.return_value = True
            mock_workspace.is_dir.return_value = True
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_jobs_dir = MagicMock()
            mock_queue_dir = MagicMock()

            # Configure Path mock
            def path_side_effect(path_arg):
                if "jobs" in str(path_arg):
                    return mock_jobs_dir
                elif "queue" in str(path_arg):
                    return mock_queue_dir
                return mock_workspace

            mock_path_class.side_effect = path_side_effect
            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            assert integration.workspace == mock_workspace
            assert integration.jobs_dir == mock_jobs_dir
            assert integration.queue_dir == mock_queue_dir

    def test_get_file_path_job(self):
        """Test _get_file_path for job files."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_job_file = MagicMock()

            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)
            mock_jobs_dir.__truediv__ = MagicMock(return_value=mock_job_file)
            mock_job_file.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            result = integration._get_file_path("test_job", "job")

            assert result == mock_job_file / "job.json"

    def test_get_file_path_queue(self):
        """Test _get_file_path for queue files."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_queue_dir = MagicMock()

            def path_side_effect(path_arg):
                if "jobs" in str(path_arg):
                    return mock_jobs_dir
                elif "queue" in str(path_arg):
                    return mock_queue_dir
                return mock_workspace

            mock_workspace.__truediv__ = MagicMock(side_effect=path_side_effect)
            mock_queue_dir.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            result = integration._get_file_path("test_job", "queue")

            assert result == mock_queue_dir / "test_job.notify"

    def test_get_file_path_invalid_type(self):
        """Test _get_file_path with invalid file type."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            with pytest.raises(ValueError, match="Unknown file type"):
                integration._get_file_path("test_job", "invalid")

    def test_load_json_file_success(self):
        """Test successful JSON file loading."""
        test_data = {"name": "test_job", "state": "COMPLETED"}

        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            with patch("database.Path") as mock_path_class:
                mock_workspace = MagicMock()
                mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())
                mock_file_path = MagicMock()
                mock_file_path.exists.return_value = True
                mock_file_path.__str__ = lambda: "/test/job.json"

                mock_plotty_config.return_value.workspace_path = mock_workspace

                # Mock _get_file_path to return our mock file path
                integration = database.StreamlinedPlottyIntegration()
                integration._get_file_path = MagicMock(return_value=mock_file_path)

                result = integration._load_json_file("test_job", "job")

                assert result == test_data

    def test_load_json_file_not_found(self):
        """Test JSON file loading when file doesn't exist."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = False

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._get_file_path = MagicMock(return_value=mock_file_path)

            with pytest.raises(Exception):  # PlottyJobError
                integration._load_json_file("test_job", "job")

    def test_load_json_file_json_error(self):
        """Test JSON file loading with invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json content")):
            with patch("database.Path") as mock_path_class:
                mock_workspace = MagicMock()
                mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())
                mock_file_path = MagicMock()
                mock_file_path.exists.return_value = True

                mock_plotty_config.return_value.workspace_path = mock_workspace

                integration = database.StreamlinedPlottyIntegration()
                integration._get_file_path = MagicMock(return_value=mock_file_path)

                with pytest.raises(Exception):  # PlottyJobError
                    integration._load_json_file("test_job", "job")

    def test_save_json_file_success(self):
        """Test successful JSON file saving."""
        test_data = {"name": "test_job", "state": "QUEUED"}

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("database.Path") as mock_path_class:
                mock_workspace = MagicMock()
                mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())
                mock_file_path = MagicMock()
                mock_file_path.parent = MagicMock()

                mock_plotty_config.return_value.workspace_path = mock_workspace

                integration = database.StreamlinedPlottyIntegration()
                integration._get_file_path = MagicMock(return_value=mock_file_path)

                integration._save_json_file("test_job", test_data, "job")

                mock_file.assert_called_once_with(mock_file_path, "w", encoding="utf-8")

    def test_save_json_file_os_error(self):
        """Test JSON file saving with OS error."""
        test_data = {"name": "test_job", "state": "QUEUED"}

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with patch("database.Path") as mock_path_class:
                mock_workspace = MagicMock()
                mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())
                mock_file_path = MagicMock()
                mock_file_path.parent = MagicMock()

                mock_plotty_config.return_value.workspace_path = mock_workspace

                integration = database.StreamlinedPlottyIntegration()
                integration._get_file_path = MagicMock(return_value=mock_file_path)

                with pytest.raises(Exception):  # PlottyJobError
                    integration._save_json_file("test_job", test_data, "job")

    def test_create_job_metadata(self):
        """Test job metadata creation."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            with patch("database.datetime") as mock_datetime:
                mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                result = integration._create_job_metadata("test_job", "fast", "A4", 1)

                assert result["id"] == "test_job"
                assert result["name"] == "test_job"
                assert result["paper"] == "A4"
                assert result["state"] == "NEW"
                assert result["priority"] == 1
                assert result["metadata"]["preset"] == "fast"
                assert result["metadata"]["version"] == "streamlined"

    def test_add_job_success(self):
        """Test successful job addition."""
        test_document = Mock()

        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock internal methods
            integration._create_job_metadata = MagicMock(
                return_value={"id": "test_job"}
            )
            integration._load_json_file = MagicMock(
                return_value={"svg_path": "/test.svg"}
            )
            integration._save_json_file = MagicMock()
            integration._notify_plotty = MagicMock()

            result = integration.add_job(test_document, "test_job", "fast", "A4", 1)

            assert result == "test_job"
            integration._create_job_metadata.assert_called_once_with(
                "test_job", "fast", "A4", 1
            )
            mock_save_document.assert_called_once()
            integration._save_json_file.assert_called_once()
            integration._notify_plotty.assert_called_once()

    def test_add_job_failure(self):
        """Test job addition with failure."""
        test_document = Mock()

        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock failure in _create_job_metadata
            integration._create_job_metadata = MagicMock(
                side_effect=Exception("Creation failed")
            )

            with pytest.raises(Exception):  # PlottyJobError
                integration.add_job(test_document, "test_job", "fast", "A4", 1)

    def test_queue_job_success(self):
        """Test successful job queuing."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock internal methods
            integration.load_job = MagicMock(
                return_value={"id": "test_job", "state": "NEW"}
            )
            integration.save_job = MagicMock()
            integration._notify_plotty = MagicMock()

            with patch("database.datetime") as mock_datetime:
                mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                integration.queue_job("test_job", 1)

                integration.save_job.assert_called_once()
                call_args = integration.save_job.call_args[0]
                assert call_args[0] == "test_job"
                assert call_args[1]["state"] == "QUEUED"
                assert call_args[1]["priority"] == 1

    def test_queue_job_failure(self):
        """Test job queuing with failure."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock failure in load_job
            integration.load_job = MagicMock(side_effect=Exception("Job not found"))

            with pytest.raises(Exception):  # PlottyJobError
                integration.queue_job("test_job", 1)

    def test_load_job(self):
        """Test job loading."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._load_json_file = MagicMock(return_value={"id": "test_job"})

            result = integration.load_job("test_job")

            assert result == {"id": "test_job"}
            integration._load_json_file.assert_called_once_with("test_job", "job")

    def test_save_job(self):
        """Test job saving."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._save_json_file = MagicMock()

            job_data = {"id": "test_job", "state": "COMPLETED"}
            integration.save_job("test_job", job_data)

            integration._save_json_file.assert_called_once_with(
                "test_job", job_data, "job"
            )

    def test_remove_job_success(self):
        """Test successful job removal."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_job_path = MagicMock()
            mock_job_path.exists.return_value = True

            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)
            mock_jobs_dir.__truediv__ = MagicMock(return_value=mock_job_path)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            with patch("database.shutil.rmtree") as mock_rmtree:
                integration = database.StreamlinedPlottyIntegration()
                integration.remove_job("test_job")

                mock_rmtree.assert_called_once_with(mock_job_path)

    def test_remove_job_not_found(self):
        """Test job removal when job doesn't exist."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_job_path = MagicMock()
            mock_job_path.exists.return_value = False

            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)
            mock_jobs_dir.__truediv__ = MagicMock(return_value=mock_job_path)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            with pytest.raises(Exception):  # PlottyJobError
                integration.remove_job("test_job")

    def test_remove_job_os_error(self):
        """Test job removal with OS error."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_job_path = MagicMock()
            mock_job_path.exists.return_value = True

            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)
            mock_jobs_dir.__truediv__ = MagicMock(return_value=mock_job_path)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            with patch(
                "database.shutil.rmtree", side_effect=OSError("Permission denied")
            ):
                integration = database.StreamlinedPlottyIntegration()

                with pytest.raises(Exception):  # PlottyJobError
                    integration.remove_job("test_job")

    def test_list_jobs_empty(self):
        """Test listing jobs when no jobs exist."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()
            mock_jobs_dir.iterdir.return_value = []

            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            result = integration.list_jobs()

            assert result == []

    def test_list_jobs_with_jobs(self):
        """Test listing jobs when jobs exist."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()

            # Mock job directories
            mock_job1_dir = MagicMock()
            mock_job1_dir.is_dir.return_value = True
            mock_job1_dir.name = "job1"

            mock_job2_dir = MagicMock()
            mock_job2_dir.is_dir.return_value = True
            mock_job2_dir.name = "job2"

            mock_jobs_dir.iterdir.return_value = [mock_job1_dir, mock_job2_dir]
            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                side_effect=[
                    {"id": "job1", "state": "COMPLETED"},
                    {"id": "job2", "state": "QUEUED"},
                ]
            )

            result = integration.list_jobs()

            assert len(result) == 2
            assert result[0]["id"] == "job1"
            assert result[1]["id"] == "job2"

    def test_list_jobs_with_state_filter(self):
        """Test listing jobs with state filter."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()

            mock_job1_dir = MagicMock()
            mock_job1_dir.is_dir.return_value = True
            mock_job1_dir.name = "job1"

            mock_job2_dir = MagicMock()
            mock_job2_dir.is_dir.return_value = True
            mock_job2_dir.name = "job2"

            mock_jobs_dir.iterdir.return_value = [mock_job1_dir, mock_job2_dir]
            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                side_effect=[
                    {"id": "job1", "state": "COMPLETED"},
                    {"id": "job2", "state": "QUEUED"},
                ]
            )

            result = integration.list_jobs(state="QUEUED")

            assert len(result) == 1
            assert result[0]["id"] == "job2"

    def test_list_jobs_with_limit(self):
        """Test listing jobs with limit."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_jobs_dir = MagicMock()

            mock_job1_dir = MagicMock()
            mock_job1_dir.is_dir.return_value = True
            mock_job1_dir.name = "job1"

            mock_job2_dir = MagicMock()
            mock_job2_dir.is_dir.return_value = True
            mock_job2_dir.name = "job2"

            mock_jobs_dir.iterdir.return_value = [mock_job1_dir, mock_job2_dir]
            mock_workspace.__truediv__ = MagicMock(return_value=mock_jobs_dir)

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                side_effect=[
                    {"id": "job1", "state": "COMPLETED"},
                    {"id": "job2", "state": "QUEUED"},
                ]
            )

            result = integration.list_jobs(limit=1)

            assert len(result) == 1
            assert result[0]["id"] == "job1"

    def test_get_job_status(self):
        """Test getting job status."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                return_value={"id": "test_job", "state": "RUNNING"}
            )

            result = integration.get_job_status("test_job")

            assert result == {"id": "test_job", "state": "RUNNING"}

    def test_find_job(self):
        """Test finding job by name."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                return_value={"id": "job123", "name": "test_job"}
            )

            result = integration.find_job("test_job")

            assert result == "job123"

    def test_get_job(self):
        """Test getting complete job data."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.load_job = MagicMock(
                return_value={"id": "test_job", "state": "COMPLETED"}
            )

            result = integration.get_job("test_job")

            assert result == {"id": "test_job", "state": "COMPLETED"}

    def test_notify_plotty_success(self):
        """Test successful ploTTY notification."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._save_json_file = MagicMock()

            job_data = {"id": "test_job", "state": "QUEUED"}
            integration._notify_plotty("test_job", job_data)

            integration._save_json_file.assert_called_once()
            call_args = integration._save_json_file.call_args[0]
            assert call_args[0] == "test_job"
            assert call_args[2] == "queue"

    def test_notify_plotty_failure(self):
        """Test ploTTY notification failure (should not raise)."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._save_json_file = MagicMock(
                side_effect=Exception("Queue failed")
            )

            job_data = {"id": "test_job", "state": "QUEUED"}

            # Should not raise exception
            integration._notify_plotty("test_job", job_data)

    def test_plotty_available_true(self):
        """Test ploTTY availability check when available."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock successful import
            with patch.dict("sys.modules", {"plotty": Mock()}):
                result = integration._plotty_available()
                assert result is True

    def test_plotty_available_false(self):
        """Test ploTTY availability check when not available."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()

            # Mock failed import
            with patch.dict("sys.modules", {}, clear=True):
                with patch(
                    "builtins.__import__",
                    side_effect=ImportError("No module named 'plotty'"),
                ):
                    result = integration._plotty_available()
                    assert result is False

    def test_delete_job_alias(self):
        """Test delete_job method (alias for remove_job)."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration.remove_job = MagicMock()

            integration.delete_job("test_job")

            integration.remove_job.assert_called_once_with("test_job")

    def test_save_job_metadata_alias(self):
        """Test _save_job_metadata method (alias for _save_json_file)."""
        with patch("database.Path") as mock_path_class:
            mock_workspace = MagicMock()
            mock_workspace.__truediv__ = MagicMock(return_value=MagicMock())

            mock_plotty_config.return_value.workspace_path = mock_workspace

            integration = database.StreamlinedPlottyIntegration()
            integration._save_json_file = MagicMock()

            job_data = {"id": "test_job", "state": "COMPLETED"}
            integration._save_job_metadata("/test/path/job.json", job_data)

            integration._save_json_file.assert_called_once_with("job", job_data, "job")

    def test_backward_compatibility_alias(self):
        """Test that PlottyIntegration alias exists."""
        assert hasattr(database, "PlottyIntegration")
        assert database.PlottyIntegration == database.StreamlinedPlottyIntegration
