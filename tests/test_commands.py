"""Test vpype commands."""

import os
import subprocess
import tempfile


def create_test_svg() -> str:
    """Create a simple test SVG file."""
    return """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""


class TestCommands:
    """Test vpype commands."""

    def test_plotty_add_basic(self):
        """Test basic plotty-add command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'test_job' added to ploTTY" in result.stdout

    def test_plotty_add_with_queue(self):
        """Test plotty-add command with queue option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--queue",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'test_job' added to ploTTY" in result.stdout
            assert "queued" in result.stdout.lower()

    def test_plotty_add_auto_name(self):
        """Test plotty-add command with auto-generated name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            result = subprocess.run(
                ["vpype", "read", svg_file, "plotty-add", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'vpype_job_" in result.stdout

    def test_plotty_add_invalid_preset(self):
        """Test plotty-add command with invalid preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--preset",
                    "invalid",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode != 0

    def test_plotty_queue_basic(self):
        """Test basic plotty-queue command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a job
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            # Add job first
            subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            # Then queue it
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-queue",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'test_job' queued" in result.stdout

    def test_plotty_queue_with_priority(self):
        """Test plotty-queue command with priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            # Add job first
            subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            # Then queue with priority
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-queue",
                    "--name",
                    "test_job",
                    "--priority",
                    "5",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_status_specific_job(self):
        """Test plotty-status command for specific job."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            # Add job first
            subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            # Check status
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-status",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_status_all_jobs(self):
        """Test plotty-status command for all jobs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["vpype", "plotty-status", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_list_basic(self):
        """Test basic plotty-list command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["vpype", "plotty-list", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_list_with_state_filter(self):
        """Test plotty-list command with state filter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["vpype", "plotty-list", "--state", "QUEUED", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_list_with_limit(self):
        """Test plotty-list command with limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["vpype", "plotty-list", "--limit", "5", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_plotty_list_json_format(self):
        """Test plotty-list command with JSON output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["vpype", "plotty-list", "--format", "json", "--workspace", temp_dir],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_interactive_pen_mapping_function(self):
        """Test the _interactive_pen_mapping function directly."""
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import numpy as np
        import vpype
        from vpype import Document
        from vpype.model import LineCollection
        from vpype_plotty.commands import _interactive_pen_mapping

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test document with multiple layers
            document = Document()

            # Create layer 1 with red color
            lc1 = LineCollection()
            lc1.append(np.array([[0, 0], [10, 10]]))
            lc1.set_property(vpype.METADATA_FIELD_COLOR, "#ff0000")  # Red
            document.layers[1] = lc1

            # Create layer 2 with green color
            lc2 = LineCollection()
            lc2.append(np.array([[0, 0], [20, 20]]))
            lc2.set_property(vpype.METADATA_FIELD_COLOR, "#00ff00")  # Green
            document.layers[2] = lc2

            # Mock user input for pen selection
            with patch("click.prompt", side_effect=[1, 2]):
                pen_mapping = _interactive_pen_mapping(document, "test_job", temp_dir)

                assert pen_mapping == {1: 1, 2: 2}

                # Check that pen mapping file was created
                pen_mapping_file = Path(temp_dir) / "pen_mappings.yaml"
                assert pen_mapping_file.exists()

    def test_interactive_pen_mapping_single_layer(self):
        """Test interactive pen mapping with single layer document."""
        import tempfile
        from vpype import Document
        from vpype_plotty.commands import _interactive_pen_mapping

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a document with single layer
            document = Document()

            pen_mapping = _interactive_pen_mapping(document, "test_job", temp_dir)

            # Should return default mapping for single layer (layer 0 when no layers)
            assert pen_mapping == {0: 1}

    def test_plotty_queue_with_interactive_pen_mapping(self):
        """Test plotty-queue command after adding job with interactive pen mapping."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(create_test_svg())

            # Mock the interactive pen mapping to avoid user input
            with patch(
                "vpype_plotty.commands._interactive_pen_mapping"
            ) as mock_mapping:
                mock_mapping.return_value = {1: 1}

                # Add job with interactive pen mapping
                add_result = subprocess.run(
                    [
                        "vpype",
                        "read",
                        svg_file,
                        "plotty-add",
                        "--name",
                        "test_job",
                        "--pen-mapping",
                        "interactive",
                        "--workspace",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                )
                assert add_result.returncode == 0

            # Queue the job (no interactive option needed for queue)
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-queue",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
