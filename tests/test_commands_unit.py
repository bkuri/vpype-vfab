"""Additional unit tests for vpype commands."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import yaml
import numpy as np

try:
    from vpype import Document
    from vpype.model import LineCollection
except ImportError:
    # Mock vpype imports for testing without full vpype installation
    from unittest.mock import MagicMock

    Document = MagicMock()
    LineCollection = MagicMock()
from vpype_vfab.commands import _interactive_pen_mapping


class TestCommandsUnit:
    """Unit tests for command functions."""

    def test_interactive_pen_mapping_multi_layer(self):
        """Test interactive pen mapping with multiple layers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test document with multiple layers
            document = Document()

            # Create layer 1 with paths
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            document.layers[1] = lc1

            # Create layer 2 with paths
            lc2 = LineCollection()
            lc2.append(np.array([[0, 0], [20, 20]]))
            document.layers[2] = lc2

            # Mock user input for pen selection
            with patch("click.prompt", side_effect=[1, 2]):
                pen_mapping = _interactive_pen_mapping(document, "test_job", temp_dir)

                assert pen_mapping == {1: 1, 2: 2}

                # Check that pen mapping file was created
                pen_mapping_file = Path(temp_dir) / "pen_mappings.yaml"
                assert pen_mapping_file.exists()

    def test_interactive_pen_mapping_with_existing_mappings(self):
        """Test interactive pen mapping with existing mappings file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing mappings file
            pen_mapping_file = Path(temp_dir) / "pen_mappings.yaml"
            existing_mappings = {"test_job_layer_1": 3, "other_job_layer_1": 2}
            with open(pen_mapping_file, "w") as f:
                yaml.dump(existing_mappings, f)

            # Create a test document with MULTIPLE layers to trigger interactive mode
            document = Document()
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            document.layers[1] = lc1

            lc2 = LineCollection()
            lc2.append(np.array([[20, 20], [30, 30]]))
            document.layers[2] = lc2

            # Mock user input to accept suggested mapping for first layer
            with patch("click.prompt", side_effect=[3, 1]):
                pen_mapping = _interactive_pen_mapping(document, "test_job", temp_dir)

                assert pen_mapping == {1: 3, 2: 1}

    def test_interactive_pen_mapping_invalid_pen_number(self):
        """Test interactive pen mapping with invalid pen number input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create document with multiple layers to trigger interactive mode
            document = Document()
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            document.layers[1] = lc1

            lc2 = LineCollection()
            lc2.append(np.array([[20, 20], [30, 30]]))
            document.layers[2] = lc2

            # Mock user input: invalid number, then valid number
            with patch("click.prompt", side_effect=[5, 2, 1]):
                with patch("click.echo") as mock_echo:
                    pen_mapping = _interactive_pen_mapping(
                        document, "test_job", temp_dir
                    )

                    assert pen_mapping == {1: 2, 2: 1}
                    # Check that warning was displayed
                    mock_echo.assert_any_call("⚠ Pen number must be between 1 and 4")

    def test_interactive_pen_mapping_keyboard_interrupt(self):
        """Test interactive pen mapping with keyboard interrupt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create document with multiple layers to trigger interactive mode
            document = Document()
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            document.layers[1] = lc1

            lc2 = LineCollection()
            lc2.append(np.array([[20, 20], [30, 30]]))
            document.layers[2] = lc2

            # Mock keyboard interrupt
            with patch("click.prompt", side_effect=KeyboardInterrupt()):
                with patch("click.echo") as mock_echo:
                    pen_mapping = _interactive_pen_mapping(
                        document, "test_job", temp_dir
                    )

                    assert pen_mapping == {}
                    mock_echo.assert_any_call("\n❌ Pen mapping cancelled")

    def test_interactive_pen_mapping_corrupted_file(self):
        """Test interactive pen mapping with corrupted mappings file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create corrupted mappings file
            pen_mapping_file = Path(temp_dir) / "pen_mappings.yaml"
            with open(pen_mapping_file, "w") as f:
                f.write("invalid: yaml: content: [")

            document = Document()
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            document.layers[1] = lc1

            with patch("click.prompt", return_value=1):
                with patch("click.echo") as mock_echo:
                    pen_mapping = _interactive_pen_mapping(
                        document, "test_job", temp_dir
                    )

                    assert pen_mapping == {1: 1}
                    # Check that warning was displayed
                    mock_echo.assert_any_call(
                        "⚠ Warning: Could not load existing pen mappings", err=True
                    )

    def test_interactive_pen_mapping_single_layer(self):
        """Test interactive pen mapping with single layer document."""
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()

            pen_mapping = _interactive_pen_mapping(document, "test_job", temp_dir)

            # Should return default mapping for single layer (layer 0 when no layers)
            assert pen_mapping == {0: 1}

    def test_generate_job_name_function(self):
        """Test job name generation function."""
        from vpype_vfab.utils import generate_job_name
        from vpype import Document

        # Test basic name generation (requires document parameter)
        document = Document()
        name1 = generate_job_name(document)
        assert name1.startswith("vpype_job_")

        # Test with prefix (prefix is used as fallback_name parameter)
        name2 = generate_job_name(document, fallback_name="test")
        assert name2 == "test"  # When fallback_name is provided, it's used directly

        # Test that function returns a string
        assert isinstance(name1, str)
        assert len(name1) > 0

    def test_validate_preset_function(self):
        """Test preset validation function."""
        from vpype_vfab.utils import validate_preset
        import click

        # Test valid presets
        validate_preset("fast")
        validate_preset("default")
        validate_preset("hq")

        # Test invalid preset
        with pytest.raises(click.BadParameter):
            validate_preset("invalid")

    def test_format_job_list_function(self):
        """Test job list formatting function."""
        from vpype_vfab.utils import format_job_list

        jobs = [
            {"id": "job1", "name": "Job 1", "state": "QUEUED"},
            {"id": "job2", "name": "Job 2", "state": "RUNNING"},
        ]

        # Test table format (default)
        table_output = format_job_list(jobs)
        assert "Job 1" in table_output
        assert "QUEUED" in table_output
        assert "Name" in table_output  # Header

        # Test JSON format
        json_output = format_job_list(jobs, output_format="json")
        import json

        parsed = json.loads(json_output)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "job1"

    def test_format_job_status_function(self):
        """Test job status formatting function."""
        from vpype_vfab.utils import format_job_status

        job_data = {
            "id": "test_job",
            "name": "Test Job",
            "state": "RUNNING",
            "created_at": "2024-01-01T12:00:00Z",
        }

        # Test table format (default)
        table_output = format_job_status(job_data)
        assert "Test Job" in table_output
        assert "RUNNING" in table_output

        # Test JSON format
        json_output = format_job_status(job_data, output_format="json")
        import json

        parsed = json.loads(json_output)
        assert parsed["id"] == "test_job"
        assert parsed["state"] == "RUNNING"
