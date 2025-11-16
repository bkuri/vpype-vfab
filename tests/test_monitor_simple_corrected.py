"""Direct monitor testing without Qt dependencies - updated for actual methods."""

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Mock all dependencies before importing monitor
mock_click = MagicMock()
mock_click.command = lambda: lambda f: f  # Simple pass-through decorator
mock_click.option = lambda *args, **kwargs: lambda f: f  # Pass-through decorator
mock_click.pass_context = lambda f: f  # Pass-through decorator
mock_click.clear = MagicMock()
mock_click.echo = MagicMock()

sys.modules["click"] = mock_click

# Mock vpype and related modules
mock_vpype = MagicMock()
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

# Now import monitor directly
import importlib.util

spec = importlib.util.spec_from_file_location(
    "monitor", "/home/bk/source/vpype-vfab/src/monitor.py"
)
monitor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor_module)

SimplePlottyMonitor = monitor_module.SimplePlottyMonitor


class TestSimplePlottyMonitor:
    """Test SimplePlottyMonitor functionality."""

    def test_monitor_initialization(self):
        """Test monitor initialization with default parameters."""
        monitor = SimplePlottyMonitor()

        assert monitor.poll_rate == 1.0
        assert monitor.workspace is None
        assert monitor.last_job_states == {}
        assert monitor.plotty_integration is not None
        assert monitor.formatter is not None

    def test_monitor_initialization_with_workspace(self):
        """Test monitor initialization with custom workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = SimplePlottyMonitor(workspace=temp_dir, poll_rate=2.5)

            assert monitor.poll_rate == 2.5
            assert monitor.workspace == temp_dir
            assert str(monitor.plotty_integration.workspace) == temp_dir

    def test_poll_rate_clamping(self):
        """Test that poll rate is properly clamped."""
        # Test minimum clamp
        monitor_low = SimplePlottyMonitor(poll_rate=0.05)
        assert monitor_low.poll_rate == 0.1

        # Test maximum clamp
        monitor_high = SimplePlottyMonitor(poll_rate=15.0)
        assert monitor_high.poll_rate == 10.0

        # Test normal values
        monitor_normal = SimplePlottyMonitor(poll_rate=5.0)
        assert monitor_normal.poll_rate == 5.0

    def test_format_job_status(self):
        """Test job status formatting."""
        monitor = SimplePlottyMonitor()
        job = {
            "id": "job1",
            "state": "queued",
            "name": "Test Job 1",
            "created_at": "2024-01-01T10:00:00Z",
        }

        with patch.object(
            monitor.formatter,
            "format_job_status_monitor",
            return_value="formatted_status",
        ):
            result = monitor.format_job_status(job)
            assert result == "formatted_status"

    def test_format_device_status(self):
        """Test device status formatting."""
        monitor = SimplePlottyMonitor()
        device = {"id": "axidraw:auto", "name": "AxiDraw", "state": "connected"}

        with patch.object(
            monitor.formatter, "format_device_status", return_value="device_status"
        ):
            result = monitor.format_device_status(device)
            assert result == "device_status"

    def test_update_display_with_jobs(self):
        """Test display update with jobs present."""
        monitor = SimplePlottyMonitor()
        jobs = [
            {
                "id": "job1",
                "state": "queued",
                "name": "Test Job 1",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        with (
            patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs),
            patch.object(
                monitor.formatter,
                "format_job_status_monitor",
                return_value="formatted_job",
            ),
            patch("click.clear"),
            patch("click.echo") as mock_echo,
        ):
            monitor.update_display()

            # Should have called echo multiple times (header, jobs, devices, etc.)
            assert mock_echo.call_count > 5

    def test_update_display_no_jobs(self):
        """Test display update with no jobs."""
        monitor = SimplePlottyMonitor()

        with (
            patch.object(monitor.plotty_integration, "list_jobs", return_value=[]),
            patch("click.clear"),
            patch("click.echo") as mock_echo,
        ):
            monitor.update_display()

            # Should have called echo including "No jobs found"
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("No jobs found" in call for call in echo_calls)

    def test_update_display_with_state_change(self):
        """Test display update detects state changes."""
        monitor = SimplePlottyMonitor()
        monitor.last_job_states = {"job1": "queued"}

        jobs = [
            {
                "id": "job1",
                "state": "running",
                "name": "Test Job 1",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        with (
            patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs),
            patch.object(
                monitor.formatter,
                "format_job_status_monitor",
                return_value="formatted_job",
            ),
            patch("click.clear"),
            patch("click.echo") as mock_echo,
        ):
            monitor.update_display()

            # Should detect state change and update last_job_states
            assert monitor.last_job_states["job1"] == "running"

            # Should show state change message
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("State changed" in call for call in echo_calls)

    def test_update_display_error_handling(self):
        """Test display update error handling."""
        monitor = SimplePlottyMonitor()

        with (
            patch.object(
                monitor.plotty_integration,
                "list_jobs",
                side_effect=Exception("Test error"),
            ),
            patch("click.clear"),
            patch("click.echo") as mock_echo,
        ):
            monitor.update_display()

            # Should handle error gracefully
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Error updating display" in call for call in echo_calls)

    def test_static_snapshot(self):
        """Test static snapshot functionality."""
        monitor = SimplePlottyMonitor()

        with (
            patch.object(monitor, "update_display") as mock_update,
            patch("click.echo") as mock_echo,
        ):
            monitor.static_snapshot()

            # Should print header and call update_display
            mock_update.assert_called_once()
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("vfab Job Status" in call for call in echo_calls)

    def test_start_monitoring_keyboard_interrupt(self):
        """Test monitoring interruption with Ctrl+C."""
        monitor = SimplePlottyMonitor(poll_rate=0.1)  # Fast polling for testing

        with (
            patch.object(monitor, "update_display", side_effect=KeyboardInterrupt()),
            patch("click.echo") as mock_echo,
        ):
            monitor.start_monitoring()

            # Should print interruption message
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Monitor stopped by user" in call for call in echo_calls)

    def test_start_monitoring_general_error(self):
        """Test monitoring with general error."""
        monitor = SimplePlottyMonitor(poll_rate=0.1)

        with (
            patch.object(
                monitor, "update_display", side_effect=Exception("Test error")
            ),
            patch("click.echo") as mock_echo,
        ):
            monitor.start_monitoring()

            # Should handle error gracefully
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Monitor error" in call for call in echo_calls)
