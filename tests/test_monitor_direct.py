"""Comprehensive monitor tests using direct import to avoid Qt issues."""

import importlib
import os
import sys
from unittest.mock import MagicMock, patch


# Set environment variables to avoid Qt display issues
os.environ["DISPLAY"] = ""  # Empty display to avoid Qt issues
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Use offscreen Qt platform

# Mock all external dependencies before any imports
mock_click = MagicMock()
mock_click.clear = MagicMock()
mock_click.echo = MagicMock()
sys.modules["click"] = mock_click

# Mock database module
mock_database = MagicMock()


class MockPlottyIntegration:
    def __init__(self, workspace=None):
        self.workspace = workspace or "/mock/workspace"

    def list_jobs(self):
        return []

    def get_job_stats(self):
        return {"total": 0, "active": 0}


mock_database.PlottyIntegration = MockPlottyIntegration
sys.modules["src.database"] = mock_database

# Import monitor module directly using importlib
import importlib.util

spec = importlib.util.spec_from_file_location(
    "src.monitor", "/home/bk/source/vpype-plotty/src/monitor.py"
)
monitor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor_module)

# Get classes and functions we need to test
SimplePlottyMonitor = monitor_module.SimplePlottyMonitor
plotty_monitor = monitor_module.plotty_monitor


class TestSimplePlottyMonitor:
    """Test cases for SimplePlottyMonitor class."""

    def test_init_default_values(self):
        """Test monitor initialization with default values."""
        monitor = SimplePlottyMonitor()

        assert monitor.workspace is None
        assert monitor.poll_rate == 1.0
        assert isinstance(monitor.plotty_integration, MockPlottyIntegration)
        assert monitor.last_job_states == {}

    def test_init_custom_values(self):
        """Test monitor initialization with custom values."""
        workspace = "/custom/workspace"
        poll_rate = 2.5

        monitor = SimplePlottyMonitor(workspace, poll_rate)

        assert monitor.workspace == workspace
        assert monitor.poll_rate == 2.5
        assert monitor.plotty_integration.workspace == workspace

    def test_init_poll_rate_clamping_minimum(self):
        """Test poll rate clamping at minimum."""
        monitor = SimplePlottyMonitor(poll_rate=0.05)  # Below minimum

        assert monitor.poll_rate == 0.1  # Should be clamped to minimum

    def test_init_poll_rate_clamping_maximum(self):
        """Test poll rate clamping at maximum."""
        monitor = SimplePlottyMonitor(poll_rate=15.0)  # Above maximum

        assert monitor.poll_rate == 10.0  # Should be clamped to maximum

    def test_format_job_status_complete(self):
        """Test formatting complete job status."""
        monitor = SimplePlottyMonitor()

        job = {
            "id": "1234567890abcdef",
            "name": "test_job",
            "state": "running",
            "progress": 75.5,
            "created_at": "2024-01-01T12:00:00Z",
        }

        result = monitor.format_job_status(job)

        assert "test_job" in result
        assert "12345678" in result  # Short ID
        assert "(75.5%)" in result
        assert "[12:00:00]" in result
        assert "🟢" in result  # Running state icon
        assert "running" in result

    def test_format_job_status_minimal(self):
        """Test formatting minimal job status."""
        monitor = SimplePlottyMonitor()

        job = {"name": "minimal_job"}

        result = monitor.format_job_status(job)

        assert "Unnamed" not in result
        assert "minimal_job" in result
        assert "unknown" in result
        assert "❓" in result  # Unknown state icon

    def test_format_job_status_all_states(self):
        """Test formatting all possible job states."""
        monitor = SimplePlottyMonitor()

        states_and_icons = {
            "pending": "🟡",
            "queued": "🔵",
            "running": "🟢",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️",
        }

        for state, icon in states_and_icons.items():
            job = {"name": f"job_{state}", "state": state}
            result = monitor.format_job_status(job)

            assert icon in result
            assert state in result

    def test_format_device_status_complete(self):
        """Test formatting complete device status."""
        monitor = SimplePlottyMonitor()

        device = {"name": "axidraw", "type": "AxiDraw", "status": "connected"}

        result = monitor.format_device_status(device)

        assert "axidraw" in result
        assert "AxiDraw" in result
        assert "connected" in result
        assert "🟢" in result  # Connected status icon

    def test_format_device_status_minimal(self):
        """Test formatting minimal device status."""
        monitor = SimplePlottyMonitor()

        device = {}

        result = monitor.format_device_status(device)

        assert "Unknown" in result
        assert "unknown" in result
        assert "❓" in result  # Unknown status icon

    def test_format_device_status_all_statuses(self):
        """Test formatting all possible device statuses."""
        monitor = SimplePlottyMonitor()

        statuses_and_icons = {
            "connected": "🟢",
            "disconnected": "🔴",
            "busy": "🟡",
            "error": "❌",
            "offline": "⚫",
        }

        for status, icon in statuses_and_icons.items():
            device = {"name": f"device_{status}", "status": status}
            result = monitor.format_device_status(device)

            assert icon in result
            assert status in result

    @patch("click.echo")
    def test_update_display_with_jobs(self, mock_echo):
        """Test display update with jobs present."""
        # Mock the plotty integration to return test jobs
        mock_integration = MagicMock()
        mock_integration.list_jobs.return_value = [
            {
                "id": "job1",
                "name": "test_job_1",
                "state": "running",
                "created_at": "2024-01-01T12:00:00Z",
            },
            {"id": "job2", "name": "test_job_2", "state": "completed"},
        ]
        mock_integration.workspace = "/test/workspace"

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        monitor.update_display()

        # Verify job status was printed
        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any("test_job_1" in call for call in echo_calls)
        assert any("test_job_2" in call for call in echo_calls)
        assert any("running" in call for call in echo_calls)
        assert any("completed" in call for call in echo_calls)
        assert any("📋 Jobs:" in call for call in echo_calls)
        assert any("🖊️  Devices:" in call for call in echo_calls)
        assert any("test_job_2" in call for call in echo_calls)

        # Verify devices section
        assert any("🖊️  Devices:" in call for call in echo_calls)
        assert any("axidraw:auto" in call for call in echo_calls)

    @patch("click.echo")
    def test_update_display_no_jobs(self, mock_echo):
        """Test display update with no jobs."""
        mock_integration = MagicMock()
        mock_integration.list_jobs.return_value = []
        mock_integration.workspace = "/test/workspace"

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        monitor.update_display()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any("📋 No jobs found" in call for call in echo_calls)
        assert any("🖊️  Devices:" in call for call in echo_calls)
        assert any("🟢 axidraw:auto" in call for call in echo_calls)

    @patch("click.echo")
    def test_update_display_with_state_change(self, mock_echo):
        """Test display update detects state changes."""
        mock_integration = MagicMock()
        job = {"id": "job1", "name": "test_job", "state": "running"}
        mock_integration.list_jobs.return_value = [job]
        mock_integration.workspace = "/test/workspace"

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        # First update - establish baseline
        monitor.update_display()

        # Change job state
        job["state"] = "completed"

        # Second update - should detect change
        monitor.update_display()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        # Should show state change message
        state_change_calls = [
            call
            for call in echo_calls
            if "🔄 State changed: running → completed" in call
        ]
        assert len(state_change_calls) >= 1
        # Should also show the updated job status
        assert any("✅ test_job (job1) - completed" in call for call in echo_calls)

    @patch("click.echo")
    def test_update_display_error_handling(self, mock_echo):
        """Test display update error handling."""
        mock_integration = MagicMock()
        mock_integration.list_jobs.side_effect = Exception("Connection error")

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        monitor.update_display()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any(
            "❌ Error updating display: Connection error" in call for call in echo_calls
        )

    @patch("time.sleep")
    @patch("click.echo")
    def test_start_monitoring_keyboard_interrupt(self, mock_echo, mock_sleep):
        """Test monitoring stops on keyboard interrupt."""
        mock_integration = MagicMock()
        mock_integration.list_jobs.return_value = []

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        # Simulate keyboard interrupt after first update
        with patch.object(monitor, "update_display", side_effect=KeyboardInterrupt):
            monitor.start_monitoring()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any("🚀 Starting ploTTY monitor" in call for call in echo_calls)
        assert any("Press Ctrl+C to stop monitoring" in call for call in echo_calls)
        assert any("👋 Monitor stopped by user" in call for call in echo_calls)

    @patch("time.sleep")
    @patch("click.echo")
    def test_start_monitoring_general_error(self, mock_echo, mock_sleep):
        """Test monitoring handles general errors."""
        mock_integration = MagicMock()
        mock_integration.list_jobs.return_value = []

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        # Simulate general error after first update
        with patch.object(
            monitor, "update_display", side_effect=Exception("Monitor error")
        ):
            monitor.start_monitoring()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any("❌ Monitor error: Monitor error" in call for call in echo_calls)

    @patch("click.echo")
    def test_static_snapshot(self, mock_echo):
        """Test static snapshot functionality."""
        mock_integration = MagicMock()
        mock_integration.list_jobs.return_value = []
        mock_integration.workspace = "/test/workspace"

        monitor = SimplePlottyMonitor()
        monitor.plotty_integration = mock_integration

        monitor.static_snapshot()

        echo_calls = [call.args[0] for call in mock_echo.call_args_list if call.args]
        assert any("📊 ploTTY Job Status" in call for call in echo_calls)
        assert any("=" * 40 in call for call in echo_calls)
        assert any("=" * 40 in call for call in echo_calls)


class TestPlottyMonitorCommand:
    """Test cases for plotty_monitor command function."""

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_default_static(self, mock_monitor_class):
        """Test command with default static behavior."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        # Call command with no arguments
        plotty_monitor(None, False, 1.0, False, False)

        mock_monitor_class.assert_called_once_with(None, 1.0)
        mock_monitor.static_snapshot.assert_called_once()
        mock_monitor.start_monitoring.assert_not_called()

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_follow_default_rate(self, mock_monitor_class):
        """Test command with follow and default rate."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor(None, True, 1.0, False, False)

        mock_monitor_class.assert_called_once_with(None, 1.0)
        mock_monitor.static_snapshot.assert_not_called()
        mock_monitor.start_monitoring.assert_called_once()

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_custom_poll_rate(self, mock_monitor_class):
        """Test command with custom poll rate."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor("/workspace", True, 2.5, False, False)

        mock_monitor_class.assert_called_once_with("/workspace", 2.5)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_fast_preset(self, mock_monitor_class):
        """Test command with fast preset."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor(None, True, 1.0, True, False)

        mock_monitor_class.assert_called_once_with(None, 0.1)  # Fast preset rate
        mock_monitor.start_monitoring.assert_called_once()

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_slow_preset(self, mock_monitor_class):
        """Test command with slow preset."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor(None, True, 1.0, False, True)

        mock_monitor_class.assert_called_once_with(None, 5.0)  # Slow preset rate
        mock_monitor.start_monitoring.assert_called_once()

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_poll_rate_clamping(self, mock_monitor_class):
        """Test command poll rate clamping."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        # Test below minimum
        plotty_monitor(None, True, 0.05, False, False)
        mock_monitor_class.assert_called_with(None, 0.1)

        # Reset mock
        mock_monitor_class.reset_mock()

        # Test above maximum
        plotty_monitor(None, True, 15.0, False, False)
        mock_monitor_class.assert_called_with(None, 10.0)

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_fast_overrides_slow(self, mock_monitor_class):
        """Test that fast preset overrides slow preset."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor(None, True, 1.0, True, True)

        # Fast should take precedence
        mock_monitor_class.assert_called_once_with(None, 0.1)

    @patch("src.monitor.SimplePlottyMonitor")
    def test_command_custom_overrides_presets(self, mock_monitor_class):
        """Test that custom rate overrides presets."""
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor

        plotty_monitor("/custom", True, 3.0, True, True)

        # Custom rate should be used, not presets
        mock_monitor_class.assert_called_once_with("/custom", 3.0)
