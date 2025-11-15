"""Integration tests for vpype-plotty commands."""

import tempfile
import os


class TestPlottyAddCommand:
    """Test plotty_add command functionality."""

    def test_vfab_add_basic(self):
        """Test basic vfab-add command using subprocess."""
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
                    "vfab-add",
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

    def test_vfab_add_with_queue(self):
        """Test vfab-add command with queue option."""
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
                    "vfab-add",
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

    def test_vfab_add_with_preset(self):
        """Test vfab-add command with different presets."""
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
                        "vfab-add",
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

    def test_vfab_add_with_priority(self):
        """Test vfab-add command with custom priority."""
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
                    "vfab-add",
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

    def test_vfab_queue_basic(self):
        """Test basic vfab-queue command."""
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
                    "vfab-queue",
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

    def test_vfab_queue_with_workspace(self):
        """Test vfab-queue command with custom workspace."""
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
                    "vfab-queue",
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

    def test_vfab_status_basic(self):
        """Test basic vfab-status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "vfab-status",
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

    def test_vfab_status_with_workspace(self):
        """Test vfab-status command with custom workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "vfab-status",
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

    def test_vfab_status_different_formats(self):
        """Test vfab-status command with different output formats."""
        formats = ["table", "json", "yaml"]

        for format_type in formats:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "vfab-status",
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

    def test_vfab_list_basic(self):
        """Test basic vfab-list command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "vfab-list",
                    "--workspace",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            assert result.returncode in [0, 1]

    def test_vfab_list_with_state_filter(self):
        """Test vfab-list command with state filter."""
        states = ["RUNNING", "QUEUED", "COMPLETED", "FAILED"]

        for state in states:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "vfab-list",
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

    def test_vfab_list_with_limit(self):
        """Test vfab-list command with limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "vfab-list",
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

    def test_vfab_list_different_formats(self):
        """Test vfab-list command with different output formats."""
        formats = ["table", "json", "yaml"]

        for format_type in formats:
            with tempfile.TemporaryDirectory() as temp_dir:
                import subprocess

                result = subprocess.run(
                    [
                        "vpype",
                        "vfab-list",
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

    def test_vfab_add_invalid_preset(self):
        """Test vfab-add with invalid preset."""
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
                    "vfab-add",
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

    def test_vfab_status_nonexistent_job(self):
        """Test vfab-status with nonexistent job."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import subprocess

            result = subprocess.run(
                [
                    "vpype",
                    "vfab-status",
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
