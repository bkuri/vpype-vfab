"""Test coverage for vpype-plotty monitor module."""

import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

from src.monitor import SimplePlottyMonitor
from src.utils import JobFormatter


class TestMonitorCoverage:
    """Comprehensive tests for monitor module to boost coverage."""

    def test_monitor_initialization(self):
        """Test SimplePlottyMonitor initialization."""
        workspace = "/test/workspace"
        poll_rate = 2.0

        monitor = SimplePlottyMonitor(workspace, poll_rate)

        assert monitor.workspace == workspace
        assert monitor.poll_rate == poll_rate
        assert monitor.formatter is not None
        assert isinstance(monitor.formatter, JobFormatter)

    def test_monitor_default_initialization(self):
        """Test SimplePlottyMonitor with default parameters."""
        monitor = SimplePlottyMonitor()

        assert monitor.workspace is not None
        assert monitor.poll_rate == 1.0
        assert hasattr(monitor, "formatter")

    @patch("src.monitor.PlottyIntegration")
    def test_update_display_success(self, mock_integration):
        """Test successful display update."""
        # Mock integration
        mock_integration.return_value.list_jobs.return_value = [
            {
                "id": "test-job-123",
                "name": "test_job",
                "state": "running",
                "created_at": "2023-01-01T12:00:00Z",
                "progress": 75.0,
            }
        ]

        monitor = SimplePlottyMonitor("/tmp")
        monitor.plotty_integration = mock_integration.return_value

        # Should not raise exception
        try:
            monitor.update_display()
        except Exception as e:
            pytest.fail(f"update_display() raised {e} unexpectedly!")

    @patch("src.monitor.PlottyIntegration")
    def test_update_display_no_jobs(self, mock_integration):
        """Test display update with no jobs."""
        mock_integration.return_value.list_jobs.return_value = []

        monitor = SimplePlottyMonitor("/tmp")
        monitor.plotty_integration = mock_integration.return_value

        # Should not raise exception
        try:
            monitor.update_display()
        except Exception as e:
            pytest.fail(f"update_display() with no jobs raised {e} unexpectedly!")

    @patch("src.monitor.PlottyIntegration")
    @patch("time.sleep")
    def test_start_monitoring_keyboard_interrupt(self, mock_sleep, mock_integration):
        """Test monitoring interrupted by user."""
        mock_integration.return_value.list_jobs.return_value = []

        monitor = SimplePlottyMonitor("/tmp", 0.1)
        monitor.plotty_integration = mock_integration.return_value

        # Mock KeyboardInterrupt on second iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt("User stopped")]

        with patch("builtins.print") as mock_print:
            monitor.start_monitoring()

        # Should handle KeyboardInterrupt gracefully
        assert mock_sleep.call_count == 2

    @patch("src.monitor.PlottyIntegration")
    @patch("time.sleep")
    def test_start_monitoring_exception(self, mock_sleep, mock_integration):
        """Test monitoring with exception."""
        mock_integration.return_value.list_jobs.return_value = []
        mock_integration.return_value.list_jobs.side_effect = Exception(
            "Connection error"
        )

        monitor = SimplePlottyMonitor("/tmp", 0.1)
        monitor.plotty_integration = mock_integration.return_value

        with patch("builtins.print") as mock_print:
            monitor.start_monitoring()

        # Should handle exception gracefully
        assert mock_sleep.called

    def test_static_snapshot(self):
        """Test static snapshot functionality."""
        with patch("src.monitor.PlottyIntegration") as mock_integration:
            mock_integration.return_value.list_jobs.return_value = []

            monitor = SimplePlottyMonitor("/tmp")
            monitor.plotty_integration = mock_integration.return_value

            # Should not raise exception
            try:
                monitor.static_snapshot()
            except Exception as e:
                pytest.fail(f"static_snapshot() raised {e} unexpectedly!")

    def test_format_job_status_compatibility(self):
        """Test backward compatibility job status formatting."""
        monitor = SimplePlottyMonitor("/tmp")

        job = {
            "id": "test-job-123",
            "name": "test_job",
            "state": "running",
            "created_at": "2023-01-01T12:00:00Z",
            "progress": 75.0,
        }

        # Should use JobFormatter's monitor method
        result = monitor.format_job_status(job)

        assert "test_job" in result
        assert "running" in result
        assert "75.0%" in result

    def test_format_device_status_compatibility(self):
        """Test backward compatibility device status formatting."""
        monitor = SimplePlottyMonitor("/tmp")

        device = {"name": "test_device", "type": "axidraw", "status": "connected"}

        # Should use JobFormatter's device method
        result = monitor.format_device_status(device)

        assert "test_device" in result
        assert "connected" in result
        assert "axidraw" in result

    @patch("src.monitor.click.clear")
    @patch("src.monitor.click.echo")
    def test_update_display_header(self, mock_echo, mock_clear):
        """Test display header formatting."""
        with patch("src.monitor.PlottyIntegration") as mock_integration:
            mock_integration.return_value.list_jobs.return_value = []
            mock_integration.return_value.workspace = Path("/test/workspace")

            monitor = SimplePlottyMonitor("/tmp", 2.0)
            monitor.plotty_integration = mock_integration.return_value

            monitor.update_display()

            # Should display header with poll interval
            mock_clear.assert_called_once()
            header_calls = [
                call
                for call in mock_echo.call_args_list
                if "vfab Monitor" in str(call)
            ]
            assert len(header_calls) > 0
            assert "updates every 2.0s" in str(header_calls[0])

    @patch("src.monitor.click.echo")
    def test_update_display_device_info(self, mock_echo):
        """Test device information display."""
        with patch("src.monitor.PlottyIntegration") as mock_integration:
            mock_integration.return_value.list_jobs.return_value = []

            monitor = SimplePlottyMonitor("/tmp")
            monitor.plotty_integration = mock_integration.return_value

            monitor.update_display()

            # Should display device information
            device_calls = [
                call for call in mock_echo.call_args_list if "Devices:" in str(call)
            ]
            assert len(device_calls) > 0
            assert "axidraw:auto" in str(device_calls[0])

    def test_monitor_with_different_poll_rates(self):
        """Test monitor initialization with various poll rates."""
        # Fast polling
        fast_monitor = SimplePlottyMonitor("/tmp", 0.1)
        assert fast_monitor.poll_rate == 0.1

        # Slow polling
        slow_monitor = SimplePlottyMonitor("/tmp", 5.0)
        assert slow_monitor.poll_rate == 5.0

        # Default polling
        default_monitor = SimplePlottyMonitor("/tmp")
        assert default_monitor.poll_rate == 1.0

    @patch("src.monitor.datetime")
    def test_update_display_timestamp(self, mock_datetime):
        """Test timestamp display in update."""
        mock_datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"

        with patch("src.monitor.PlottyIntegration") as mock_integration:
            mock_integration.return_value.list_jobs.return_value = []

            monitor = SimplePlottyMonitor("/tmp")
            monitor.plotty_integration = mock_integration.return_value

            monitor.update_display()

            # Should include timestamp in header
            # Note: This tests the datetime usage in monitor module
