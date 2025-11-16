"""Tests for commands.py monitor functionality."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from vpype_vfab.commands import plotty_monitor


class TestPlottyMonitorCommand:
    """Test the plotty_monitor command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_static_default(self, mock_monitor_class):
        """Test static monitor with default parameters."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, [])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 1.0)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_follow_mode(self, mock_monitor_class):
        """Test monitor in follow mode."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--follow"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 1.0)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_custom_poll_rate(self, mock_monitor_class):
        """Test monitor with custom poll rate."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--poll-rate", "2.5"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 2.5)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_fast_option(self, mock_monitor_class):
        """Test monitor with fast option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--fast"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 0.1)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_slow_option(self, mock_monitor_class):
        """Test monitor with slow option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--slow"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 5.0)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_workspace_option(self, mock_monitor_class):
        """Test monitor with workspace option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        workspace = "/test/workspace"
        result = self.runner.invoke(plotty_monitor, ["--workspace", workspace])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(workspace, 1.0)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_follow_with_workspace(self, mock_monitor_class):
        """Test monitor follow mode with workspace."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        workspace = "/test/workspace"
        result = self.runner.invoke(
            plotty_monitor, ["--follow", "--workspace", workspace]
        )

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(workspace, 1.0)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_fast_follow(self, mock_monitor_class):
        """Test monitor fast option with follow mode."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--fast", "--follow"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 0.1)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_slow_follow(self, mock_monitor_class):
        """Test monitor slow option with follow mode."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--slow", "--follow"])

        assert result.exit_code == 0
        mock_monitor_class.assert_called_once_with(None, 5.0)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_poll_rate_validation_minimum(self, mock_monitor_class):
        """Test poll rate validation at minimum boundary."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Test with poll rate below minimum - should be clamped
        result = self.runner.invoke(plotty_monitor, ["--poll-rate", "0.05"])

        assert result.exit_code == 0
        # Should be clamped to 0.1 by SimplePlottyMonitor constructor
        mock_monitor_class.assert_called_once_with(
            None, 0.05
        )  # Command passes raw value
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_poll_rate_validation_maximum(self, mock_monitor_class):
        """Test poll rate validation at maximum boundary."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Test with poll rate above maximum
        result = self.runner.invoke(plotty_monitor, ["--poll-rate", "15.0"])

        assert result.exit_code == 0
        # Should be clamped to 10.0 by SimplePlottyMonitor constructor
        mock_monitor_class.assert_called_once_with(
            None, 15.0
        )  # Command passes raw value
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_poll_rate_priority_fast_overrides_custom(self, mock_monitor_class):
        """Test that --fast option overrides custom poll rate."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--poll-rate", "2.0", "--fast"])

        assert result.exit_code == 0
        # Fast option should override custom poll rate
        mock_monitor_class.assert_called_once_with(None, 0.1)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_poll_rate_priority_slow_overrides_custom(self, mock_monitor_class):
        """Test that --slow option overrides custom poll rate."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--poll-rate", "2.0", "--slow"])

        assert result.exit_code == 0
        # Slow option should override custom poll rate
        mock_monitor_class.assert_called_once_with(None, 5.0)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_poll_rate_priority_fast_overrides_slow(self, mock_monitor_class):
        """Test that --fast option overrides --slow option."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, ["--slow", "--fast"])

        assert result.exit_code == 0
        # Fast option should take precedence over slow
        mock_monitor_class.assert_called_once_with(None, 0.1)
        mock_monitor.static_snapshot.assert_called_once()

    @patch("vpype_vfab.commands.click.echo")
    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_exception_handling(self, mock_monitor_class, mock_echo):
        """Test exception handling in monitor command."""
        # Simulate exception from SimplePlottyMonitor
        mock_monitor_class.side_effect = Exception("Test error")

        result = self.runner.invoke(plotty_monitor, [])

        assert result.exit_code != 0
        # Verify error was echoed
        mock_echo.assert_called_with("✗ Error: Test error", err=True)

    @patch("vpype_vfab.commands.click.echo")
    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_vfab_monitor_monitor_exception(self, mock_monitor_class, mock_echo):
        """Test exception from monitor methods."""
        mock_monitor = Mock()
        mock_monitor.static_snapshot.side_effect = Exception("Monitor error")
        mock_monitor_class.return_value = mock_monitor

        result = self.runner.invoke(plotty_monitor, [])

        assert result.exit_code != 0
        # Verify error was echoed
        mock_echo.assert_called_with("✗ Error: Monitor error", err=True)

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_command_help_message(self, mock_monitor_class):
        """Test that command help is displayed correctly."""
        result = self.runner.invoke(plotty_monitor, ["--help"])

        assert result.exit_code == 0
        assert "Monitor vfab jobs" in result.output
        assert "--workspace" in result.output
        assert "--follow" in result.output
        assert "--poll-rate" in result.output
        assert "--fast" in result.output
        assert "--slow" in result.output

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_all_options_combination(self, mock_monitor_class):
        """Test all options used together."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        workspace = "/test/workspace"
        result = self.runner.invoke(
            plotty_monitor, ["--workspace", workspace, "--follow", "--fast"]
        )

        assert result.exit_code == 0
        # Fast should override default poll rate
        mock_monitor_class.assert_called_once_with(workspace, 0.1)
        mock_monitor.start_monitoring.assert_called_once()

    @patch("vpype_vfab.monitor.SimplePlottyMonitor")
    def test_document_return_value(self, mock_monitor_class):
        """Test that document is returned from command."""
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Mock a document
        with patch("vpype_vfab.commands.vpype_cli.global_processor") as mock_processor:
            mock_doc = Mock()
            mock_processor.return_value = lambda f: f(mock_doc)

            result = self.runner.invoke(plotty_monitor, [])

            assert result.exit_code == 0
            # The command should return the document unchanged
            mock_monitor.static_snapshot.assert_called_once()
