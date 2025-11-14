"""Qt-free tests for vpype_plotty.monitor module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import time
from datetime import datetime
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock external dependencies to avoid Qt issues
sys.modules["click"] = Mock()

# Mock database module
mock_database = Mock()
mock_plotty_integration = Mock()
mock_database.PlottyIntegration = mock_plotty_integration
sys.modules["vpype_plotty.database"] = mock_database

# Mock utils module
mock_utils = Mock()
mock_job_formatter = Mock()
mock_utils.JobFormatter = mock_job_formatter
sys.modules["vpype_plotty.utils"] = mock_utils

# Now import monitor module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "monitor", "/home/bk/source/vpype-plotty/vpype_plotty/monitor.py"
)
if spec is None:
    raise ImportError("Could not load monitor module")
monitor = importlib.util.module_from_spec(spec)
sys.modules["monitor"] = monitor  # Register in sys.modules for patching
spec.loader.exec_module(monitor)


class TestMonitorQtFree:
    """Qt-free test suite for monitor module."""

    def test_init_with_workspace_and_poll_rate(self):
        """Test SimplePlottyMonitor initialization with custom parameters."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            monitor_instance = monitor.SimplePlottyMonitor("/test/workspace", 2.5)

            assert monitor_instance.workspace == "/test/workspace"
            assert monitor_instance.poll_rate == 2.5
            assert monitor_instance.plotty_integration == mock_integration_instance
            assert monitor_instance.formatter == mock_formatter_instance
            assert monitor_instance.last_job_states == {}

    def test_init_poll_rate_clamping_minimum(self):
        """Test poll rate clamping at minimum value."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_job_formatter.return_value = Mock()

            # Test below minimum (0.1)
            monitor_instance = monitor.SimplePlottyMonitor("/test/workspace", 0.05)
            assert monitor_instance.poll_rate == 0.1  # Should be clamped to minimum

    def test_init_poll_rate_clamping_maximum(self):
        """Test poll rate clamping at maximum value."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_job_formatter.return_value = Mock()

            # Test above maximum (10.0)
            monitor_instance = monitor.SimplePlottyMonitor("/test/workspace", 15.0)
            assert monitor_instance.poll_rate == 10.0  # Should be clamped to maximum

    def test_init_default_parameters(self):
        """Test SimplePlottyMonitor initialization with default parameters."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            monitor_instance = monitor.SimplePlottyMonitor()

            assert monitor_instance.workspace is None
            assert monitor_instance.poll_rate == 1.0  # Default poll rate
            assert monitor_instance.plotty_integration == mock_integration_instance
            assert monitor_instance.formatter == mock_formatter_instance
            assert monitor_instance.last_job_states == {}

    def test_format_job_status(self):
        """Test job status formatting (backward compatibility)."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_formatter_instance.format_job_status_monitor.return_value = (
                "🟢 job1: COMPLETED"
            )
            mock_job_formatter.return_value = mock_formatter_instance

            monitor_instance = monitor.SimplePlottyMonitor()

            job_data = {"id": "job1", "state": "COMPLETED"}
            result = monitor_instance.format_job_status(job_data)

            assert result == "🟢 job1: COMPLETED"
            mock_formatter_instance.format_job_status_monitor.assert_called_once_with(
                job_data
            )

    def test_format_device_status(self):
        """Test device status formatting (backward compatibility)."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_formatter_instance.format_device_status.return_value = (
                "🟢 axidraw:auto: connected"
            )
            mock_job_formatter.return_value = mock_formatter_instance

            monitor_instance = monitor.SimplePlottyMonitor()

            device_data = {"name": "axidraw:auto", "status": "connected"}
            result = monitor_instance.format_device_status(device_data)

            assert result == "🟢 axidraw:auto: connected"
            mock_formatter_instance.format_device_status.assert_called_once_with(
                device_data
            )

    def test_update_display_with_jobs(self):
        """Test display update when jobs exist."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance
            mock_integration_instance.workspace = "/test/workspace"

            mock_formatter_instance = Mock()
            mock_formatter_instance.format_job_status_monitor.return_value = (
                "🟢 job1: COMPLETED"
            )
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions
            with patch("monitor.click") as mock_click:
                monitor_instance = monitor.SimplePlottyMonitor()

                # Mock jobs data
                jobs = [
                    {"id": "job1", "state": "COMPLETED"},
                    {"id": "job2", "state": "RUNNING"},
                ]
                mock_integration_instance.list_jobs.return_value = jobs

                monitor_instance.update_display()

                # Verify click was called for display elements
                mock_click.clear.assert_called_once()
                assert mock_click.echo.called

                # Check that job formatting was called
                assert mock_formatter_instance.format_job_status_monitor.call_count == 2

    def test_update_display_no_jobs(self):
        """Test display update when no jobs exist."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance
            mock_integration_instance.workspace = "/test/workspace"

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions
            with patch("monitor.click") as mock_click:
                monitor_instance = monitor.SimplePlottyMonitor()

                # Mock empty jobs list
                mock_integration_instance.list_jobs.return_value = []

                monitor_instance.update_display()

                # Verify "No jobs found" message
                echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                assert any("No jobs found" in call_str for call_str in echo_calls)

    def test_update_display_state_change_detection(self):
        """Test state change detection in display update."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance
            mock_integration_instance.workspace = "/test/workspace"

            mock_formatter_instance = Mock()
            mock_formatter_instance.format_job_status_monitor.return_value = (
                "🟢 job1: COMPLETED"
            )
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions
            with patch("monitor.click") as mock_click:
                monitor_instance = monitor.SimplePlottyMonitor()

                # First update - job is RUNNING
                jobs1 = [{"id": "job1", "state": "RUNNING"}]
                mock_integration_instance.list_jobs.return_value = jobs1
                monitor_instance.update_display()

                # Second update - job is COMPLETED (state change)
                jobs2 = [{"id": "job1", "state": "COMPLETED"}]
                mock_integration_instance.list_jobs.return_value = jobs2
                monitor_instance.update_display()

                # Verify state change was detected and reported
                echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                assert any(
                    "State changed: RUNNING → COMPLETED" in call_str
                    for call_str in echo_calls
                )

    def test_update_display_error_handling(self):
        """Test error handling in display update."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance
            mock_integration_instance.workspace = "/test/workspace"

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions
            with patch("monitor.click") as mock_click:
                monitor_instance = monitor.SimplePlottyMonitor()

                # Mock exception in list_jobs
                mock_integration_instance.list_jobs.side_effect = Exception(
                    "Database error"
                )

                monitor_instance.update_display()

                # Verify error message was displayed
                echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                assert any(
                    "Error updating display: Database error" in call_str
                    for call_str in echo_calls
                )

    def test_start_monitoring_keyboard_interrupt(self):
        """Test monitoring start with keyboard interrupt."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions and time.sleep
            with patch("monitor.click") as mock_click:
                with patch("monitor.time") as mock_time:
                    # Simulate KeyboardInterrupt on second sleep call
                    mock_time.sleep.side_effect = [None, KeyboardInterrupt()]

                    monitor_instance = monitor.SimplePlottyMonitor()

                    # Mock update_display to avoid infinite loop
                    monitor_instance.update_display = Mock()

                    monitor_instance.start_monitoring()

                    # Verify monitoring stopped message
                    echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                    assert any(
                        "Monitor stopped by user" in call_str for call_str in echo_calls
                    )

    def test_start_monitoring_general_exception(self):
        """Test monitoring start with general exception."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions and time.sleep
            with patch("monitor.click") as mock_click:
                with patch("monitor.time") as mock_time:
                    # Simulate general exception
                    mock_time.sleep.side_effect = Exception("System error")

                    monitor_instance = monitor.SimplePlottyMonitor()

                    # Mock update_display to avoid infinite loop
                    monitor_instance.update_display = Mock()

                    monitor_instance.start_monitoring()

                    # Verify error message was displayed
                    echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                    assert any(
                        "Monitor error: System error" in call_str
                        for call_str in echo_calls
                    )

    def test_static_snapshot(self):
        """Test static snapshot functionality."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click functions
            with patch("monitor.click") as mock_click:
                monitor_instance = monitor.SimplePlottyMonitor()

                # Mock update_display
                monitor_instance.update_display = Mock()

                monitor_instance.static_snapshot()

                # Verify header and update_display were called
                echo_calls = [str(call) for call in mock_click.echo.call_args_list]
                assert any("ploTTY Job Status" in call_str for call_str in echo_calls)
                monitor_instance.update_display.assert_called_once()

    def test_plotty_monitor_command_default_options(self):
        """Test plotty_monitor command with default options."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Call with default parameters
                    plotty_monitor(None, False, 1.0, False, False)

                    # Verify monitor was created with default poll rate
                    mock_monitor_class.assert_called_once_with(None, 1.0)
                    mock_monitor_instance.static_snapshot.assert_called_once()

    def test_plotty_monitor_command_follow_mode(self):
        """Test plotty_monitor command with follow mode."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Call with follow mode
                    plotty_monitor("/test/workspace", True, 1.0, False, False)

                    # Verify monitor was created and started
                    mock_monitor_class.assert_called_once_with("/test/workspace", 1.0)
                    mock_monitor_instance.start_monitoring.assert_called_once()

    def test_plotty_monitor_command_fast_option(self):
        """Test plotty_monitor command with fast option."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Call with fast option
                    plotty_monitor(None, True, 1.0, True, False)

                    # Verify monitor was created with fast poll rate (0.1s)
                    mock_monitor_class.assert_called_once_with(None, 0.1)
                    mock_monitor_instance.start_monitoring.assert_called_once()

    def test_plotty_monitor_command_slow_option(self):
        """Test plotty_monitor command with slow option."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Call with slow option
                    plotty_monitor(None, True, 1.0, False, True)

                    # Verify monitor was created with slow poll rate (5.0s)
                    mock_monitor_class.assert_called_once_with(None, 5.0)
                    mock_monitor_instance.start_monitoring.assert_called_once()

    def test_plotty_monitor_command_custom_poll_rate(self):
        """Test plotty_monitor command with custom poll rate."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Call with custom poll rate
                    plotty_monitor(None, True, 2.5, False, False)

                    # Verify monitor was created with custom poll rate
                    mock_monitor_class.assert_called_once_with(None, 2.5)
                    mock_monitor_instance.start_monitoring.assert_called_once()

    def test_plotty_monitor_command_poll_rate_validation(self):
        """Test poll rate validation in command."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Test poll rate below minimum (should be clamped)
                    plotty_monitor(None, True, 0.05, False, False)

                    # Verify poll rate was clamped to minimum
                    mock_monitor_class.assert_called_once_with(None, 0.1)

    def test_plotty_monitor_command_poll_rate_above_maximum(self):
        """Test poll rate above maximum in command."""
        with patch("monitor.PlottyIntegration") as mock_integration_class:
            mock_integration_instance = Mock()
            mock_integration_class.return_value = mock_integration_instance

            mock_formatter_instance = Mock()
            mock_job_formatter.return_value = mock_formatter_instance

            # Mock click and SimplePlottyMonitor
            with patch("monitor.click") as mock_click:
                with patch("monitor.SimplePlottyMonitor") as mock_monitor_class:
                    mock_monitor_instance = Mock()
                    mock_monitor_class.return_value = mock_monitor_instance

                    # Import and call the command function
                    from monitor import plotty_monitor

                    # Test poll rate above maximum (should be clamped)
                    plotty_monitor(None, True, 15.0, False, False)

                    # Verify poll rate was clamped to maximum
                    mock_monitor_class.assert_called_once_with(None, 10.0)
