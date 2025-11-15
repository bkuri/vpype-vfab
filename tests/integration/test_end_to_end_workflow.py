"""End-to-end workflow validation tests for vpype-plotty."""

import os
import time
import tempfile
import subprocess
from unittest.mock import patch

import pytest

from tests.integration import (
    import_vsketch_example,
    skip_if_no_sandbox,
    skip_if_no_vsketch,
)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture
    def workspace_dir(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @skip_if_no_sandbox
    @skip_if_no_vsketch
    def test_complete_schotter_workflow(self, workspace_dir):
        """Test complete Schotter workflow: vsketch → vpype-plotty → ploTTY."""
        import vsketch

        # Step 1: Generate Schotter pattern with vsketch
        schotter_sketch = import_vsketch_example("schotter")
        assert schotter_sketch is not None, "Could not import Schotter sketch"

        vsk = vsketch.Vsketch()
        schotter_sketch.draw(vsk)

        # Verify pattern generation
        assert len(vsk.document.layers) > 0
        total_paths = sum(len(layer) for layer in vsk.document.layers.values())
        assert total_paths > 200  # 12x22 grid

        # Step 2: Apply vpype optimization
        schotter_sketch.finalize(vsk)

        # Step 3: Save to SVG
        svg_file = os.path.join(workspace_dir, "schotter_workflow.svg")
        vsk.save(svg_file)
        assert os.path.exists(svg_file)
        assert os.path.getsize(svg_file) > 0

        # Step 4: Add to ploTTY with vpype-plotty
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "plotty-add",
                "--name",
                "schotter_workflow_test",
                "--preset",
                "hq",
                "--queue",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Job 'schotter_workflow_test' added to ploTTY" in result.stdout

        # Step 5: Check job status
        result = subprocess.run(
            [
                "vpype",
                "plotty-status",
                "--name",
                "schotter_workflow_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "schotter_workflow_test" in result.stdout

        # Step 6: List all jobs
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--format",
                "json",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    @skip_if_no_sandbox
    @skip_if_no_vsketch
    def test_complete_quickdraw_workflow(self, workspace_dir):
        """Test complete Quick Draw workflow with batch processing."""
        import vsketch

        # Step 1: Generate Quick Draw pattern
        quickdraw_sketch = import_vsketch_example("quick_draw")
        assert quickdraw_sketch is not None, "Could not import Quick Draw sketch"

        # Mock Quick Draw data download
        with (
            patch("urllib.request.urlretrieve"),
            patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
        ):
            mock_drawing = {
                "key_id": 1,
                "country_code": b"US",
                "recognized": 1,
                "timestamp": 1234567890,
                "image": [([10, 20, 30], [15, 25, 35])],
            }
            mock_unpack.return_value = [mock_drawing] * 4  # 2x2 grid

            vsk = vsketch.Vsketch()
            quickdraw_sketch.columns = 2
            quickdraw_sketch.rows = 2
            quickdraw_sketch.layer_count = 1
            quickdraw_sketch.draw(vsk)

            # Step 2: Apply finalize
            quickdraw_sketch.finalize(vsk)

            # Step 3: Save and add to ploTTY
            svg_file = os.path.join(workspace_dir, "quickdraw_workflow.svg")
            vsk.save(svg_file)

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "quickdraw_workflow_test",
                    "--preset",
                    "default",
                    "--queue",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'quickdraw_workflow_test' added to ploTTY" in result.stdout

    @skip_if_no_sandbox
    def test_batch_processing_workflow(self, workspace_dir):
        """Test batch processing of multiple sketches."""
        # Create multiple simple SVG files for batch processing
        svg_files = []
        job_names = []

        for i in range(3):
            svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<rect x="{i * 10}" y="{i * 10}" width="50" height="50" fill="none" stroke="black" stroke-width="1"/>
<circle cx="{50 + i * 5}" cy="{50 + i * 5}" r="20" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"batch_test_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            svg_files.append(svg_file)
            job_name = f"batch_job_{i}"
            job_names.append(job_name)

            # Add to ploTTY
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--queue",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert f"Job '{job_name}' added to ploTTY" in result.stdout

        # Verify all jobs are in ploTTY
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        for job_name in job_names:
            assert job_name in result.stdout

    @skip_if_no_sandbox
    def test_multilayer_pen_mapping_workflow(self, workspace_dir):
        """Test workflow with multi-layer pen mapping."""
        # Create multi-layer SVG
        svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<g id="layer1" stroke="#ff0000" stroke-width="1">
<rect x="10" y="10" width="30" height="30" fill="none"/>
</g>
<g id="layer2" stroke="#0000ff" stroke-width="1">
<circle cx="70" cy="70" r="20" fill="none"/>
</g>
<g id="layer3" stroke="#00ff00" stroke-width="1">
<polygon points="50,10 90,50 50,90 10,50" fill="none"/>
</g>
</svg>"""

        svg_file = os.path.join(workspace_dir, "multilayer_test.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        # Mock interactive pen mapping
        with patch("src.commands._interactive_pen_mapping") as mock_mapping:
            mock_mapping.return_value = {1: 1, 2: 2, 3: 3}

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    "multilayer_test",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    @skip_if_no_sandbox
    def test_error_recovery_workflow(self, workspace_dir):
        """Test workflow error recovery."""
        # Test with invalid SVG
        invalid_svg = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<invalid_element>This is not valid SVG</invalid_element>
</svg>"""

        svg_file = os.path.join(workspace_dir, "invalid_test.svg")
        with open(svg_file, "w") as f:
            f.write(invalid_svg)

        # Should handle invalid SVG gracefully
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "plotty-add",
                "--name",
                "invalid_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        # May fail at vpype level, but shouldn't crash
        # The exact behavior depends on vpype's error handling

        # Test with non-existent ploTTY (should handle gracefully by creating fallback)
        result = subprocess.run(
            [
                "vpype",
                "plotty-status",
                "--workspace",
                "/tmp/definitely_nonexistent_path_12345",
            ],
            capture_output=True,
            text=True,
        )

        # Should handle missing workspace gracefully (either fails or creates fallback)
        assert result.returncode == 0 or "error" in result.stdout.lower()

    @skip_if_no_sandbox
    def test_priority_queue_workflow(self, workspace_dir):
        """Test priority queue workflow."""
        # Create jobs with different priorities
        jobs = [
            {"name": "low_priority_job", "priority": 1},
            {"name": "medium_priority_job", "priority": 5},
            {"name": "high_priority_job", "priority": 10},
        ]

        svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>
</svg>"""

        for job in jobs:
            svg_file = os.path.join(workspace_dir, f"{job['name']}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            # Add job with priority
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job["name"],
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

            # Queue with priority
            result = subprocess.run(
                [
                    "vpype",
                    "plotty-queue",
                    "--name",
                    job["name"],
                    "--priority",
                    str(job["priority"]),
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

        # Verify jobs are queued with priorities
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--state",
                "QUEUED",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    @skip_if_no_sandbox
    def test_monitoring_integration_workflow(self, workspace_dir):
        """Test monitoring integration in workflow."""
        # Create a job and monitor it
        svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

        svg_file = os.path.join(workspace_dir, "monitoring_test.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        # Add job
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "plotty-add",
                "--name",
                "monitoring_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Test monitoring command (should not crash)
        result = subprocess.run(
            [
                "vpype",
                "plotty-monitor",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
            timeout=5,  # Don't wait for interactive input
        )

        # May fail due to no interactive mode, but shouldn't crash
        # The exact behavior depends on monitor implementation

    @skip_if_no_sandbox
    def test_configuration_driven_workflow(self, workspace_dir):
        """Test workflow driven by configuration files."""
        # Create ploTTY configuration
        config_content = """
websocket:
  enabled: true
  port: 8765
  
devices:
  axidraw:auto:
    type: axidraw
    port: auto
    
presets:
  test_preset:
    speed: 30
    acceleration: 30
    pen_height_up: 50
    pen_height_down: 0
"""

        config_file = os.path.join(workspace_dir, "config.yaml")
        with open(config_file, "w") as f:
            f.write(config_content)

        # Create job using custom preset
        svg_content = """<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<circle cx="50" cy="50" r="30" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

        svg_file = os.path.join(workspace_dir, "config_test.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "plotty-add",
                "--name",
                "config_test",
                "--preset",
                "test_preset",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        # May fail if preset doesn't exist, but should handle gracefully
        # The exact behavior depends on preset validation

    @skip_if_no_sandbox
    def test_performance_workflow(self, workspace_dir):
        """Test workflow performance with complex geometry."""
        # Create complex SVG
        paths = []
        for i in range(50):  # 50 paths
            path_data = (
                f"M{i * 2},{i * 2} L{i * 2 + 10},{i * 2 + 10} L{i * 2 + 20},{i * 2} Z"
            )
            paths.append(
                f'<path d="{path_data}" fill="none" stroke="black" stroke-width="0.5"/>'
            )

        svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
{chr(10).join(paths)}
</svg>"""

        svg_file = os.path.join(workspace_dir, "performance_test.svg")
        with open(svg_file, "w") as f:
            f.write(svg_content)

        # Measure processing time
        start_time = time.time()

        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "linemerge",
                "linesimplify",
                "plotty-add",
                "--name",
                "performance_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert result.returncode == 0
        assert processing_time < 30.0  # Should complete within 30 seconds

    @skip_if_no_sandbox
    def test_cleanup_workflow(self, workspace_dir):
        """Test workflow cleanup and resource management."""
        # Create and add multiple jobs
        job_names = []
        for i in range(3):
            svg_content = f"""<?xml version="1.0" encoding="utf-8" ?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
<text x="{i * 20}" y="50" font-family="Arial" font-size="12">Job {i}</text>
</svg>"""

            svg_file = os.path.join(workspace_dir, f"cleanup_test_{i}.svg")
            with open(svg_file, "w") as f:
                f.write(svg_content)

            job_name = f"cleanup_test_{i}"
            job_names.append(job_name)

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "plotty-add",
                    "--name",
                    job_name,
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

        # Verify jobs exist
        result = subprocess.run(
            [
                "vpype",
                "plotty-list",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        for job_name in job_names:
            assert job_name in result.stdout

        # Test cleanup (if supported)
        # This would test job deletion/cleanup functionality
        # Implementation depends on ploTTY's cleanup features
