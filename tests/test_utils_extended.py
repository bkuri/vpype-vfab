"""Additional utils coverage tests without Qt dependencies."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Mock all dependencies before importing utils
mock_click = MagicMock()
mock_click.command = lambda: lambda f: f
mock_click.option = lambda *args, **kwargs: lambda f: f
mock_click.echo = MagicMock()
mock_click.secho = MagicMock()
mock_click.style = MagicMock()
mock_click.prompt = MagicMock()
mock_click.confirm = MagicMock()

sys.modules["click"] = mock_click

# Mock vpype and related modules
mock_vpype = MagicMock()
mock_vpype.Document = MagicMock()
mock_vpype.LineCollection = MagicMock()
mock_vpype.METADATA_FIELD_COLOR = "color"
mock_vpype.cli = MagicMock()
mock_vpype.cli.save = MagicMock()
mock_vpype.cli.load = MagicMock()

sys.modules["vpype"] = mock_vpype
sys.modules["vpype.model"] = mock_vpype
sys.modules["vpype.cli"] = mock_vpype.cli

# Mock Qt modules
sys.modules["PySide6"] = MagicMock()
sys.modules["PySide6.QtCore"] = MagicMock()
sys.modules["PySide6.QtWidgets"] = MagicMock()
sys.modules["PySide6.QtGui"] = MagicMock()

# Mock vpype_viewer and vpype_cli
sys.modules["vpype_viewer"] = MagicMock()
sys.modules["vpype_viewer.qtviewer"] = MagicMock()
sys.modules["vpype_viewer.qtviewer.viewer"] = MagicMock()
sys.modules["vpype_cli"] = MagicMock()
sys.modules["vpype_cli.show"] = MagicMock()

# Now import utils directly
import importlib.util

spec = importlib.util.spec_from_file_location(
    "utils", "/home/bk/source/vpype-vfab/src/utils.py"
)
utils_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils_module)

JobFormatter = utils_module.JobFormatter


class TestJobFormatterExtended:
    """Extended tests for JobFormatter to increase coverage."""

    def test_format_job_list_empty_list(self):
        """Test formatting empty job list."""
        formatter = JobFormatter()

        result = formatter.format_job_list([])

        assert result == "No jobs found."

    def test_format_job_list_csv_format(self):
        """Test CSV format for job list."""
        formatter = JobFormatter()
        jobs = [
            {
                "id": "job1",
                "name": "Test Job 1",
                "state": "queued",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        result = formatter.format_job_list(jobs, format="csv")

        assert "id,name,state,created_at" in result
        assert "job1,Test Job 1,queued,2024-01-01T10:00:00Z" in result

    def test_format_job_status_monitor_with_progress(self):
        """Test monitor format with progress information."""
        formatter = JobFormatter()
        job = {
            "id": "job1",
            "name": "Test Job 1",
            "state": "running",
            "progress": 45,
            "created_at": "2024-01-01T10:00:00Z",
        }

        result = formatter.format_job_status_monitor(job)

        assert "job1" in result
        assert "Test Job 1" in result
        assert "running" in result
        assert "45%" in result

    def test_format_job_status_simple_with_error(self):
        """Test simple format with error state."""
        formatter = JobFormatter()
        job = {
            "id": "job1",
            "name": "Test Job 1",
            "state": "error",
            "error": "Connection failed",
            "created_at": "2024-01-01T10:00:00Z",
        }

        result = formatter.format_job_status_simple(job)

        assert "job1" in result
        assert "error" in result
        assert "Connection failed" in result

    def test_format_device_status_disconnected(self):
        """Test device status formatting for disconnected device."""
        formatter = JobFormatter()
        device = {
            "id": "axidraw:auto",
            "name": "AxiDraw",
            "state": "disconnected",
            "last_seen": "2024-01-01T09:30:00Z",
        }

        result = formatter.format_device_status(device)

        assert "axidraw:auto" in result
        assert "AxiDraw" in result
        assert "disconnected" in result

    def test_validate_preset_edge_cases(self):
        """Test preset validation with edge cases."""
        from vpype_vfab.utils import validate_preset

        # Test with None
        assert validate_preset(None) is False

        # Test with empty string
        assert validate_preset("") is False

        # Test with valid preset
        assert validate_preset("axidraw") is True

    def test_generate_job_name_edge_cases(self):
        """Test job name generation with edge cases."""
        from vpype_vfab.utils import generate_job_name

        # Test with empty metadata
        result = generate_job_name({})
        assert result.startswith("job_")
        assert len(result) > 4

    def test_save_document_for_vfab_permission_error(self):
        """Test document saving with permission error."""
        from vpype_vfab.utils import save_document_for_vfab

        document = MagicMock()

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("click.echo") as mock_echo:
                result = save_document_for_vfab(document, "/restricted/path.svg")

                assert result is False
                mock_echo.assert_called()

    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        formatter = JobFormatter()

        result = formatter.format_duration(30)

        assert "30s" in result or "0m30s" in result

    def test_format_duration_minutes(self):
        """Test duration formatting for minutes."""
        formatter = JobFormatter()

        result = formatter.format_duration(90)  # 1 minute 30 seconds

        assert "1m" in result
        assert "30s" in result

    def test_format_duration_hours(self):
        """Test duration formatting for hours."""
        formatter = JobFormatter()

        result = formatter.format_duration(3661)  # 1 hour 1 minute 1 second

        assert "1h" in result
        assert "1m" in result
        assert "1s" in result
