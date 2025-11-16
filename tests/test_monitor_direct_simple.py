"""Direct monitor testing without Qt dependencies."""

import tempfile
from unittest.mock import MagicMock, patch
import sys

# Mock all dependencies before importing monitor
mock_click = MagicMock()
mock_click.command = lambda: lambda f: f  # Simple pass-through decorator
mock_click.option = lambda *args, **kwargs: lambda f: f  # Pass-through decorator
mock_click.pass_context = lambda f: f  # Pass-through decorator

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
from vpype_vfab.monitor import SimplePlottyMonitor


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

    def test_check_job_changes_no_jobs(self):
        """Test job change detection with no jobs."""
        monitor = SimplePlottyMonitor()

        with patch.object(monitor.plotty_integration, "list_jobs", return_value=[]):
            changes = monitor.check_job_changes()

            assert changes == []
            assert monitor.last_job_states == {}

    def test_check_job_changes_new_job(self):
        """Test job change detection with new job."""
        monitor = SimplePlottyMonitor()
        jobs = [
            {
                "id": "job1",
                "state": "queued",
                "name": "Test Job 1",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        with patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs):
            changes = monitor.check_job_changes()

            assert len(changes) == 1
            assert changes[0]["id"] == "job1"
            assert changes[0]["change_type"] == "new"
            assert "job1" in monitor.last_job_states

    def test_check_job_changes_state_change(self):
        """Test job change detection with state change."""
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

        with patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs):
            changes = monitor.check_job_changes()

            assert len(changes) == 1
            assert changes[0]["id"] == "job1"
            assert changes[0]["change_type"] == "state_change"
            assert changes[0]["old_state"] == "queued"
            assert changes[0]["new_state"] == "running"
            assert monitor.last_job_states["job1"] == "running"

    def test_check_job_changes_no_change(self):
        """Test job change detection with no changes."""
        monitor = SimplePlottyMonitor()
        monitor.last_job_states = {"job1": "queued"}

        jobs = [
            {
                "id": "job1",
                "state": "queued",
                "name": "Test Job 1",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        with patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs):
            changes = monitor.check_job_changes()

            assert changes == []
            assert monitor.last_job_states == {"job1": "queued"}

    def test_check_job_changes_removed_job(self):
        """Test job change detection with removed job."""
        monitor = SimplePlottyMonitor()
        monitor.last_job_states = {"job1": "queued", "job2": "running"}

        jobs = [
            {
                "id": "job1",
                "state": "queued",
                "name": "Test Job 1",
                "created_at": "2024-01-01T10:00:00Z",
            }
        ]

        with patch.object(monitor.plotty_integration, "list_jobs", return_value=jobs):
            changes = monitor.check_job_changes()

            assert len(changes) == 1
            assert changes[0]["id"] == "job2"
            assert changes[0]["change_type"] == "removed"
            assert "job2" not in monitor.last_job_states

    def test_monitor_once_no_jobs(self):
        """Test single monitoring cycle with no jobs."""
        monitor = SimplePlottyMonitor()

        with (
            patch.object(monitor, "check_job_changes", return_value=[]),
            patch("builtins.print") as mock_print,
        ):
            monitor.monitor_once()

            # Should print "No vfab jobs found."
            mock_print.assert_called_with("No vfab jobs found.")

    def test_monitor_once_with_jobs(self):
        """Test single monitoring cycle with jobs."""
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
                monitor.formatter, "format_job_status", return_value="formatted_status"
            ),
            patch("builtins.print") as mock_print,
        ):
            monitor.monitor_once()

            # Should print formatted status
            mock_print.assert_called_with("formatted_status")

    def test_get_monitoring_stats_empty(self):
        """Test monitoring stats with no history."""
        monitor = SimplePlottyMonitor()

        stats = monitor.get_monitoring_stats()

        assert stats["total_jobs"] == 0
        assert stats["job_states"] == {}
        assert stats["last_update"] is not None

    def test_get_monitoring_stats_with_jobs(self):
        """Test monitoring stats with job history."""
        monitor = SimplePlottyMonitor()
        monitor.last_job_states = {"job1": "queued", "job2": "running"}

        with patch.object(
            monitor.plotty_integration,
            "list_jobs",
            return_value=[
                {"id": "job1", "state": "queued"},
                {"id": "job2", "state": "running"},
            ],
        ):
            stats = monitor.get_monitoring_stats()

            assert stats["total_jobs"] == 2
            assert stats["job_states"]["queued"] == 1
            assert stats["job_states"]["running"] == 1
            assert stats["last_update"] is not None
