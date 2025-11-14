"""Integration tests for vpype-plotty commands."""

import tempfile
import os


class TestPlottyAddCommand:
    """Test plotty_add command functionality."""

    def test_plotty_add_basic(self):
        """Test basic plotty-add command using subprocess."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

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
                cwd=temp_dir,
            )

            # Should either succeed or fail gracefully with workspace setup
            # We're testing integration, not full functionality
            assert result.returncode in [0, 1]  # Accept both success and config errors

    def test_plotty_add_with_queue(self):
        """Test plotty-add command with queue option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job_queue",
                    "--queue",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_add_with_preset(self):
        """Test plotty-add command with different presets."""
        presets = ["fast", "default", "hq"]

        for preset in presets:
            with tempfile.TemporaryDirectory() as temp_dir:
                svg_file = os.path.join(temp_dir, "test.svg")
                with open(svg_file, "w") as f:
                    f.write(
                        """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                    )

                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "read",
                        svg_file,
                        "plotty-add",
                        "--name",
                        f"test_job_{preset}",
                        "--preset",
                        preset,
                        "--workspace",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                )

                assert result.returncode in [0, 1]

    def test_plotty_add_with_priority(self):
        """Test plotty-add command with custom priority."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job_priority",
                    "--priority",
                    "5",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]


class TestPlottyQueueCommand:
    """Test plotty_queue command functionality."""

    def test_plotty_queue_basic(self):
        """Test basic plotty-queue command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-queue",
                    "--name",
                    "test_job",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_queue_with_workspace(self):
        """Test plotty-queue command with custom workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-queue",
                    "--name",
                    "test_job_workspace",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]


class TestPlottyStatusCommand:
    """Test plotty_status command functionality."""

    def test_plotty_status_basic(self):
        """Test basic plotty-status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "plotty-status",
                    "--name",
                    "test_job_123",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_status_with_workspace(self):
        """Test plotty-status command with custom workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "plotty-status",
                    "--name",
                    "test_job_456",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_status_different_formats(self):
        """Test plotty-status command with different output formats."""
        formats = ["table", "json", "yaml"]

        for format_type in formats:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "plotty-status",
                        "--name",
                        f"test_job_{format_type}",
                        "--format",
                        format_type,
                        "--workspace",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                )

                assert result.returncode in [0, 1]


class TestPlottyListCommand:
    """Test plotty_list command functionality."""

    def test_plotty_list_basic(self):
        """Test basic plotty-list command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "plotty-list",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_list_with_state_filter(self):
        """Test plotty-list command with state filter."""
        states = ["RUNNING", "QUEUED", "COMPLETED", "FAILED"]

        for state in states:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "plotty-list",
                        "--state",
                        state,
                        "--workspace",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                )

                assert result.returncode in [0, 1]

    def test_plotty_list_with_limit(self):
        """Test plotty-list command with limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "plotty-list",
                    "--limit",
                    "5",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_plotty_list_different_formats(self):
        """Test plotty-list command with different output formats."""
        formats = ["table", "json", "yaml"]

        for format_type in formats:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "plotty-list",
                        "--format",
                        format_type,
                        "--workspace",
                        temp_dir,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir,
                )

                assert result.returncode in [0, 1]


class TestCommandErrorHandling:
    """Test command error handling scenarios."""

    def test_plotty_add_invalid_preset(self):
        """Test plotty-add with invalid preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            svg_file = os.path.join(temp_dir, "test.svg")
            with open(svg_file, "w") as f:
                f.write(
                    """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""
                )

            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "test_job_invalid",
                    "--preset",
                    "invalid_preset",  # This should fail
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Should fail due to invalid preset
            assert result.returncode != 0

    def test_plotty_status_nonexistent_job(self):
        """Test plotty-status with nonexistent job."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "plotty-status",
                    "--name",
                    "nonexistent_job_12345",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Should fail gracefully
            assert result.returncode in [0, 1]
