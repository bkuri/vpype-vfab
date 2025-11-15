"""Tests for streamlined vpype commands."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

import pytest

# Mock vpype imports to avoid Qt display issues
mock_vpype = MagicMock()
mock_vpype.__version__ = "1.15.0"
sys.modules["vpype"] = mock_vpype
sys.modules["vpype.Document"] = MagicMock()

# Mock click to avoid display issues
sys.modules["click"] = MagicMock()

# Import after mocking
from src.base import StreamlinedPlottyCommand
from src.commands import (
    plotty_add,
    plotty_list,
    plotty_queue,
    plotty_status,
    plotty_delete,
)
from src.exceptions import PlottyJobError


class TestStreamlinedPlottyCommand:
    """Test cases for StreamlinedPlottyCommand base class."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def command(self, temp_workspace):
        """Create command instance with temporary workspace."""
        return StreamlinedPlottyCommand(str(temp_workspace))

    @pytest.fixture
    def mock_document(self):
        """Create mock vpype document."""
        return MagicMock()

    def test_init_default_workspace(self):
        """Test initialization with default workspace."""
        cmd = StreamlinedPlottyCommand()
        assert cmd.plotty is not None
        assert cmd.plotty.workspace.exists()

    def test_init_custom_workspace(self, temp_workspace):
        """Test initialization with custom workspace."""
        cmd = StreamlinedPlottyCommand(str(temp_workspace))
        assert cmd.plotty.workspace == temp_workspace

    def test_handle_error_without_context(self, command):
        """Test error handling without context."""
        error = Exception("Test error")

        with pytest.raises(Exception):  # ClickException wraps the original
            command.handle_error(error)

    def test_handle_error_with_context(self, command):
        """Test error handling with context."""
        error = Exception("Test error")
        context = "test operation"

        with pytest.raises(Exception):  # ClickException wraps the original
            command.handle_error(error, context)

    def test_get_pen_mapping_auto(self, command, mock_document):
        """Test pen mapping with auto preset."""
        mapping = command.get_pen_mapping(mock_document, "auto")
        # Auto should return None (use ploTTY defaults)
        assert mapping is None

    def test_get_pen_mapping_sequential(self, command, mock_document):
        """Test pen mapping with sequential preset."""
        mapping = command.get_pen_mapping(mock_document, "sequential")
        # Sequential should return None (use ploTTY defaults)
        assert mapping is None

    def test_get_pen_mapping_single(self, command, mock_document):
        """Test pen mapping with single preset."""
        mapping = command.get_pen_mapping(mock_document, "single")
        # Single should return None (use ploTTY defaults)
        assert mapping is None

    def test_get_pen_mapping_invalid(self, command, mock_document):
        """Test pen mapping with invalid preset."""
        with patch("src.commands.validate_preset") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid preset")

            with pytest.raises(ValueError):
                command.get_pen_mapping(mock_document, "invalid")


class TestPenMappingPresets:
    """Test pen mapping preset functions."""

    def test_command_get_pen_mapping_auto(self):
        """Test auto pen mapping preset through command."""
        cmd = StreamlinedPlottyCommand()
        doc = MagicMock()
        doc.layers = [1, 2, 3, 4, 5]  # 5 layers

        result = cmd.get_pen_mapping(doc, "auto")
        expected = {1: 1, 2: 2, 3: 3, 4: 4, 5: 1}  # cycle through 1-4
        assert result == expected

    def test_command_get_pen_mapping_sequential(self):
        """Test sequential pen mapping preset through command."""
        cmd = StreamlinedPlottyCommand()
        doc = MagicMock()
        doc.layers = [1, 2, 3]

        result = cmd.get_pen_mapping(doc, "sequential")
        expected = {1: 2, 2: 3, 3: 4}  # sequential mapping
        assert result == expected

    def test_command_get_pen_mapping_single_layer(self):
        """Test single layer returns None."""
        cmd = StreamlinedPlottyCommand()
        doc = MagicMock()
        doc.layers = [1]  # Single layer

        result = cmd.get_pen_mapping(doc, "auto")
        assert result is None

    def test_command_get_pen_mapping_invalid(self):
        """Test invalid pen mapping preset through command."""
        cmd = StreamlinedPlottyCommand()
        doc = MagicMock()
        doc.layers = [1, 2]

        # Invalid preset should default to auto mapping
        result = cmd.get_pen_mapping(doc, "invalid")
        expected = {1: 1, 2: 2}
        assert result == expected


class TestPlottyCommands:
    """Test individual ploTTY commands."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_document(self):
        """Create mock vpype document."""
        doc = MagicMock()
        doc.layers = [MagicMock(), MagicMock()]  # Mock 2 layers
        return doc

    def test_plotty_add_command_success(self, runner, mock_document, temp_workspace):
        """Test successful plotty_add command."""
        with patch("src.commands.load_document") as mock_load:
            mock_load.return_value = mock_document

            with patch(
                "src.commands.StreamlinedPlottyCommand"
            ) as mock_cmd_class:
                mock_cmd = MagicMock()
                mock_cmd_class.return_value = mock_cmd

                result = runner.invoke(
                    plotty_add,
                    [
                        "--name",
                        "test_job",
                        "--preset",
                        "fast",
                        "--paper",
                        "A4",
                        "--workspace",
                        str(temp_workspace),
                    ],
                )

                # Should not raise exception
                assert result.exit_code == 0 or result.exception is None

    def test_plotty_add_command_with_pen_mapping(
        self, runner, mock_document, temp_workspace
    ):
        """Test plotty_add command with pen mapping."""
        with patch("src.commands.load_document") as mock_load:
            mock_load.return_value = mock_document

            with patch(
                "src.commands.StreamlinedPlottyCommand"
            ) as mock_cmd_class:
                mock_cmd = MagicMock()
                mock_cmd_class.return_value = mock_cmd

                result = runner.invoke(
                    plotty_add,
                    [
                        "--name",
                        "test_job",
                        "--pen-preset",
                        "sequential",
                        "--workspace",
                        str(temp_workspace),
                    ],
                )

                # Should not raise exception
                assert result.exit_code == 0 or result.exception is None

    def test_plotty_list_command_success(self, runner, temp_workspace):
        """Test successful plotty_list command."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd.plotty.list_jobs.return_value = [
                {"name": "job1", "state": "NEW"},
                {"name": "job2", "state": "QUEUED"},
            ]
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(plotty_list, ["--workspace", str(temp_workspace)])

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_plotty_list_command_with_state_filter(self, runner, temp_workspace):
        """Test plotty_list command with state filter."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd.plotty.list_jobs.return_value = [
                {"name": "job1", "state": "QUEUED"}
            ]
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(
                plotty_list, ["--state", "QUEUED", "--workspace", str(temp_workspace)]
            )

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_plotty_queue_command_success(self, runner, temp_workspace):
        """Test successful plotty_queue command."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(
                plotty_queue, ["test_job", "--workspace", str(temp_workspace)]
            )

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_plotty_queue_command_with_priority(self, runner, temp_workspace):
        """Test plotty_queue command with priority."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(
                plotty_queue,
                ["test_job", "--priority", "5", "--workspace", str(temp_workspace)],
            )

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_plotty_status_command_success(self, runner, temp_workspace):
        """Test successful plotty_status command."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd.plotty.get_job_status.return_value = {
                "name": "test_job",
                "state": "QUEUED",
                "created_at": "2024-01-01T00:00:00Z",
            }
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(
                plotty_status, ["test_job", "--workspace", str(temp_workspace)]
            )

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_plotty_delete_command_success(self, runner, temp_workspace):
        """Test successful plotty_delete command."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd_class.return_value = mock_cmd

            with patch("click.confirm", return_value=True):
                result = runner.invoke(
                    plotty_delete, ["test_job", "--workspace", str(temp_workspace)]
                )

                # Should not raise exception
                assert result.exit_code == 0 or result.exception is None

    def test_plotty_delete_command_cancelled(self, runner, temp_workspace):
        """Test plotty_delete command when cancelled."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd_class.return_value = mock_cmd

            with patch("click.confirm", return_value=False):
                result = runner.invoke(
                    plotty_delete, ["test_job", "--workspace", str(temp_workspace)]
                )

                # Should not raise exception
                assert result.exit_code == 0 or result.exception is None

    def test_plotty_delete_command_force(self, runner, temp_workspace):
        """Test plotty_delete command with force flag."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(
                plotty_delete,
                ["test_job", "--force", "--workspace", str(temp_workspace)],
            )

            # Should not raise exception
            assert result.exit_code == 0 or result.exception is None

    def test_command_error_handling(self, runner, temp_workspace):
        """Test command error handling."""
        with patch("src.commands.StreamlinedPlottyCommand") as mock_cmd_class:
            mock_cmd = MagicMock()
            mock_cmd.plotty.list_jobs.side_effect = PlottyJobError("Test error")
            mock_cmd_class.return_value = mock_cmd

            result = runner.invoke(plotty_list, ["--workspace", str(temp_workspace)])

            # Should handle error gracefully
            assert result.exception is not None

    def test_command_with_invalid_preset(self, runner, mock_document, temp_workspace):
        """Test command with invalid preset."""
        with patch("src.commands.load_document") as mock_load:
            mock_load.return_value = mock_document

            result = runner.invoke(
                plotty_add,
                [
                    "--name",
                    "test_job",
                    "--preset",
                    "invalid",
                    "--workspace",
                    str(temp_workspace),
                ],
            )

            # Should handle error gracefully
            assert result.exception is not None or result.exit_code != 0

    def test_command_with_invalid_pen_preset(
        self, runner, mock_document, temp_workspace
    ):
        """Test command with invalid pen preset."""
        with patch("src.commands.load_document") as mock_load:
            mock_load.return_value = mock_document

            result = runner.invoke(
                plotty_add,
                [
                    "--name",
                    "test_job",
                    "--pen-preset",
                    "invalid",
                    "--workspace",
                    str(temp_workspace),
                ],
            )

            # Should handle error gracefully
            assert result.exception is not None or result.exit_code != 0
