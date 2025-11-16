"""Comprehensive tests for the streamlined monitor module."""

from unittest.mock import Mock, patch

from vpype_vfab.monitor import SimplePlottyMonitor, plotty_monitor


class TestSimplePlottyMonitor:
    """Test the SimplePlottyMonitor class."""

    def test_init_default_values(self):
        """Test monitor initialization with default values."""
        monitor = SimplePlottyMonitor()
        assert monitor.workspace is None
        assert monitor.poll_rate == 1.0
        assert monitor.last_job_states == {}

    def test_init_custom_values(self):
        """Test monitor initialization with custom values."""
        monitor = SimplePlottyMonitor(workspace="/tmp/test", poll_rate=2.5)
        assert monitor.workspace == "/tmp/test"
        assert monitor.poll_rate == 2.5

    def test_init_poll_rate_clamping(self):
        """Test poll rate clamping to valid range."""
        # Test minimum clamping
        monitor = SimplePlottyMonitor(poll_rate=0.05)
        assert monitor.poll_rate == 0.1

        # Test maximum clamping
        monitor = SimplePlottyMonitor(poll_rate=15.0)
        assert monitor.poll_rate == 10.0

        # Test boundary values
        monitor = SimplePlottyMonitor(poll_rate=0.1)
        assert monitor.poll_rate == 0.1

        monitor = SimplePlottyMonitor(poll_rate=10.0)
        assert monitor.poll_rate == 10.0

    @patch("vpype_vfab.monitor.PlottyIntegration")
    def test_init_plotty_integration(self, mock_integration):
        """Test that PlottyIntegration is properly initialized."""
        workspace = "/test/workspace"
        monitor = SimplePlottyMonitor(workspace=workspace)
        mock_integration.assert_called_once_with(workspace)

    def test_format_job_status_basic(self):
        """Test basic job status formatting."""
        monitor = SimplePlottyMonitor()
        job = {"name": "test_job", "state": "running", "id": "1234567890abcdef"}
        status = monitor.format_job_status(job)
        assert "test_job" in status
        assert "12345678" in status  # Short ID
        assert "running" in status
        assert "🟢" in status  # State icon

    def test_format_job_status_with_progress(self):
        """Test job status formatting with progress."""
        monitor = SimplePlottyMonitor()
        job = {
            "name": "test_job",
            "state": "running",
            "id": "1234567890abcdef",
            "progress": 75.5,
        }
        status = monitor.format_job_status(job)
        assert "75.5%" in status

    def test_format_job_status_with_timing(self):
        """Test job status formatting with creation time."""
        monitor = SimplePlottyMonitor()
        job = {
            "name": "test_job",
            "state": "running",
            "id": "1234567890abcdef",
            "created_at": "2024-01-01T12:00:00",
        }
        status = monitor.format_job_status(job)
        assert "[12:00:00]" in status

    def test_format_job_status_all_fields(self):
        """Test job status formatting with all fields."""
        monitor = SimplePlottyMonitor()
        job = {
            "name": "complex_job",
            "state": "running",
            "id": "1234567890abcdef",
            "progress": 42.5,
            "created_at": "2024-01-01T12:00:00",
        }
        status = monitor.format_job_status(job)
        assert "complex_job" in status
        assert "12345678" in status
        assert "42.5%" in status
        assert "[12:00:00]" in status
        assert "running" in status

    def test_format_job_status_missing_fields(self):
        """Test job status formatting with missing fields."""
        monitor = SimplePlottyMonitor()
        job = {}  # Empty job
        status = monitor.format_job_status(job)
        assert "Unnamed" in status
        assert "unknown" in status
        assert "unknown"[:8] in status  # Short ID
        assert "❓" in status  # Unknown state icon

    def test_format_job_status_all_states(self):
        """Test job status formatting for all possible states."""
        monitor = SimplePlottyMonitor()
        states = {
            "pending": "🟡",
            "queued": "🔵",
            "running": "🟢",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⏹️",
        }

        for state, icon in states.items():
            job = {"name": "test_job", "state": state, "id": "1234567890abcdef"}
            status = monitor.format_job_status(job)
            assert icon in status

    def test_format_device_status_basic(self):
        """Test basic device status formatting."""
        monitor = SimplePlottyMonitor()
        device = {"name": "axidraw", "status": "connected", "type": "AxiDraw"}
        status = monitor.format_device_status(device)
        assert "axidraw" in status
        assert "connected" in status
        assert "AxiDraw" in status
        assert "🟢" in status  # Status icon

    def test_format_device_status_missing_fields(self):
        """Test device status formatting with missing fields."""
        monitor = SimplePlottyMonitor()
        device = {}  # Empty device
        status = monitor.format_device_status(device)
        assert "Unknown" in status
        assert "unknown" in status
        assert "❓" in status  # Unknown status icon

    def test_format_device_status_all_statuses(self):
        """Test device status formatting for all possible statuses."""
        monitor = SimplePlottyMonitor()
        statuses = {
            "connected": "🟢",
            "disconnected": "🔴",
            "busy": "🟡",
            "error": "❌",
            "offline": "⚫",
        }

        for status_val, icon in statuses.items():
            device = {"name": "test_device", "status": status_val, "type": "TestType"}
            status = monitor.format_device_status(device)
            assert icon in status

    @patch("vpype_vfab.monitor.PlottyIntegration")
    @patch("vpype_vfab.monitor.click.clear")
    @patch("vpype_vfab.monitor.click.echo")
    @patch("vpype_vfab.monitor.datetime")
    def test_update_display_with_jobs(
        self, mock_datetime, mock_echo, mock_clear, mock_integration
    ):
        """Test display update with jobs present."""
        # Mock current time
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        # Mock plotty integration to return jobs
        mock_plotty = Mock()
        mock_jobs = [
            {
                "id": "1234567890abcdef",
                "name": "test_job_1",
                "state": "running",
                "progress": 50.0,
            },
            {"id": "fedcba0987654321", "name": "test_job_2", "state": "completed"},
        ]
        mock_plotty.list_jobs.return_value = mock_jobs
        mock_integration.return_value = mock_plotty

        monitor = SimplePlottyMonitor(poll_rate=1.0)
        monitor.update_display()

        # Verify screen was cleared
        mock_clear.assert_called_once()

        # Verify header was printed
        mock_echo.assert_any_call(
            "🔍 vfab Monitor - 2024-01-01 12:00:00 (updates every 1.0s)"
        )
        mock_echo.assert_any_call("=" * 60)

        # Verify jobs section was printed
        mock_echo.assert_any_call("\n📋 Jobs:")

        # Verify job statuses were printed
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("test_job_1" in call for call in calls)
        assert any("test_job_2" in call for call in calls)

    @patch("vpype_vfab.monitor.PlottyIntegration")
    @patch("vpype_vfab.monitor.click.clear")
    @patch("vpype_vfab.monitor.click.echo")
    @patch("vpype_vfab.monitor.datetime")
    def test_update_display_no_jobs(
        self, mock_datetime, mock_echo, mock_clear, mock_integration
    ):
        """Test display update with no jobs."""
        # Mock current time
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00:00"

        mock_plotty = Mock()
        mock_plotty.list_jobs.return_value = []
        mock_integration.return_value = mock_plotty

        monitor = SimplePlottyMonitor()
        monitor.update_display()

        # Verify no jobs message
        mock_echo.assert_any_call("\n📋 No jobs found")

    @patch("vpype_vfab.monitor.PlottyIntegration")
    @patch("vpype_vfab.monitor.click.clear")
    @patch("vpype_vfab.monitor.click.echo")
    def test_update_display_state_change_detection(
        self, mock_echo, mock_clear, mock_integration
    ):
        """Test state change detection in display update."""
        mock_plotty = Mock()
        mock_integration.return_value = mock_plotty

        monitor = SimplePlottyMonitor()

        # First call - no previous state
        job1 = {"id": "1234567890abcdef", "name": "test_job", "state": "running"}
        mock_plotty.list_jobs.return_value = [job1]
        monitor.update_display()

        # Second call - state changed
        job1_changed = {
            "id": "1234567890abcdef",
            "name": "test_job",
            "state": "completed",
        }
        mock_plotty.list_jobs.return_value = [job1_changed]
        monitor.update_display()

        # Verify state change was detected and reported
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("State changed: running → completed" in call for call in calls)

    @patch("vpype_vfab.monitor.PlottyIntegration")
    @patch("vpype_vfab.monitor.click.clear")
    @patch("vpype_vfab.monitor.click.echo")
    def test_update_display_error_handling(
        self, mock_echo, mock_clear, mock_integration
    ):
        """Test error handling in display update."""
        mock_plotty = Mock()
        mock_plotty.list_jobs.side_effect = Exception("Database error")
        mock_integration.return_value = mock_plotty

        monitor = SimplePlottyMonitor()
        monitor.update_display()

        # Verify error was reported
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Error updating display: Database error" in call for call in calls)

    @patch("vpype_vfab.monitor.click.echo")
    def test_static_snapshot(self, mock_echo):
        """Test static snapshot functionality."""
        monitor = SimplePlottyMonitor()

        with patch.object(monitor, "update_display") as mock_update:
            monitor.static_snapshot()

            # Verify header was printed
            mock_echo.assert_any_call("📊 vfab Job Status")
            mock_echo.assert_any_call("=" * 40)

            # Verify update_display was called
            mock_update.assert_called_once()

    @patch("vpype_vfab.monitor.click.echo")
    @patch("time.sleep")
    def test_start_monitoring_keyboard_interrupt(self, mock_sleep, mock_echo):
        """Test monitoring interruption with Ctrl+C."""
        monitor = SimplePlottyMonitor()

        with patch.object(monitor, "update_display") as mock_update:
            # Simulate KeyboardInterrupt after first update
            mock_update.side_effect = KeyboardInterrupt()

            monitor.start_monitoring()

            # Verify update_display was called once
            mock_update.assert_called_once()

            # Verify stop message was printed
            calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Monitor stopped by user" in call for call in calls)

    @patch("vpype_vfab.monitor.click.echo")
    @patch("time.sleep")
    def test_start_monitoring_general_error(self, mock_sleep, mock_echo):
        """Test monitoring with general error."""
        monitor = SimplePlottyMonitor()

        with patch.object(monitor, "update_display") as mock_update:
            # Simulate general error
            mock_update.side_effect = Exception("General error")

            monitor.start_monitoring()

            # Verify error was reported
            calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Monitor error: General error" in call for call in calls)


class TestPlottyMonitorCommand:
    """Test the plotty_monitor click command."""

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    @patch("vpype_vfab.monitor.click.echo")
    def test_vfab_monitor_static_default(self, mock_echo, mock_monitor_class):
        """Test static monitor with default parameters."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock click runner
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor"):
            result = runner.invoke(plotty_monitor, [])

        assert result.exit_code == 0

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_follow_mode(self, mock_monitor_class):
        """Test monitor in follow mode."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock click runner
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor"):
            result = runner.invoke(plotty_monitor, ["--follow"])

        assert result.exit_code == 0

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_custom_poll_rate(self, mock_monitor_class):
        """Test monitor with custom poll rate."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock click runner
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor"):
            result = runner.invoke(plotty_monitor, ["--poll-rate", "2.5"])

        assert result.exit_code == 0

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_fast_option(self, mock_monitor_class):
        """Test monitor with fast option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock click runner
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor"):
            result = runner.invoke(plotty_monitor, ["--fast"])

        assert result.exit_code == 0

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_slow_option(self, mock_monitor_class):
        """Test monitor with slow option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock click runner
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor"):
            result = runner.invoke(plotty_monitor, ["--slow"])

        assert result.exit_code == 0

    def test_poll_rate_validation(self):
        """Test poll rate validation in command."""
        # Test that invalid poll rates are clamped
        from click.testing import CliRunner

        runner = CliRunner()

        with patch("vpype_vfab.monitor.SimplePlottyMonitor") as mock_class:
            mock_monitor = Mock()
            mock_class.return_value = mock_monitor

            # Test with poll rate below minimum
            result = runner.invoke(plotty_monitor, ["--poll-rate", "0.05"])
            assert result.exit_code == 0
            # Should be clamped to 0.1
            mock_class.assert_called_with(None, 0.1)

            # Test with poll rate above maximum
            result = runner.invoke(plotty_monitor, ["--poll-rate", "15.0"])
            assert result.exit_code == 0
            # Should be clamped to 10.0
            mock_class.assert_called_with(None, 10.0)
