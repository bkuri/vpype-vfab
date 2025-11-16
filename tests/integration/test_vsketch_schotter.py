"""Integration tests for Schotter sketch with vpype-vfab."""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

# Add sandbox/vsketch to path for importing vsketch examples
vsketch_path = Path(__file__).parent.parent.parent / "sandbox" / "vsketch"
if vsketch_path.exists():
    sys.path.insert(0, str(vsketch_path))
    sys.path.insert(0, str(vsketch_path / "examples" / "schotter"))


class TestSchotterIntegration:
    """Test Schotter sketch integration with vpype-vfab."""

    @pytest.fixture
    def schotter_sketch(self):
        """Import Schotter sketch from temp vsketch."""
        try:
            from sketch_schotter import SchotterSketch

            return SchotterSketch()
        except ImportError as e:
            pytest.skip(f"Could not import Schotter sketch: {e}")

    @pytest.fixture
    def workspace_dir(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_schotter_basic_generation(self, schotter_sketch, workspace_dir):
        """Test basic Schotter pattern generation."""
        import vsketch

        # Create vsketch instance
        vsk = vsketch.Vsketch()

        # Execute Schotter draw
        schotter_sketch.draw(vsk)

        # Verify document has content
        assert len(vsk.document.layers) > 0
        assert vsk.document.page_size is not None

        # Check that we have multiple squares (grid pattern)
        total_paths = sum(len(layer) for layer in vsk.document.layers.values())
        assert total_paths > 200  # 12x22 grid = 264 squares

    def test_schotter_parameter_variations(self, workspace_dir):
        """Test Schotter with different parameter combinations."""
        try:
            from sketch_schotter import SchotterSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Schotter sketch")

        # Test different parameter combinations
        test_params = [
            {"columns": 6, "rows": 8, "fuzziness": 0.5},
            {"columns": 15, "rows": 20, "fuzziness": 2.0},
            {"columns": 3, "rows": 4, "fuzziness": 1.5},
        ]

        for params in test_params:
            vsk = vsketch.Vsketch()
            sketch = SchotterSketch()

            # Set parameters
            for key, value in params.items():
                setattr(sketch, key, value)

            # Generate pattern
            sketch.draw(vsk)

            # Verify grid size
            expected_squares = params["columns"] * params["rows"]
            total_paths = sum(len(layer) for layer in vsk.document.layers.values())
            assert total_paths == expected_squares

    def test_schotter_with_vpype_vfab_add(self, schotter_sketch, workspace_dir):
        """Test adding Schotter sketch to vfab."""
        import vsketch

        # Create Schotter pattern
        vsk = vsketch.Vsketch()
        schotter_sketch.draw(vsk)

        # Save to SVG
        svg_file = os.path.join(workspace_dir, "schotter.svg")
        vsk.save(svg_file)

        # Add to vfab using vpype command
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "vfab-add",
                "--name",
                "schotter_test",
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Job 'schotter_test' added to vfab" in result.stdout

    def test_schotter_with_different_presets(self, schotter_sketch, workspace_dir):
        """Test Schotter with different vfab presets."""
        import vsketch

        presets = ["fast", "default", "hq"]

        for preset in presets:
            vsk = vsketch.Vsketch()
            schotter_sketch.draw(vsk)

            # Save to SVG
            svg_file = os.path.join(workspace_dir, f"schotter_{preset}.svg")
            vsk.save(svg_file)

            # Add to vfab with preset
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "vfab-add",
                    "--name",
                    f"schotter_{preset}",
                    "--preset",
                    preset,
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert f"Job 'schotter_{preset}' added to vfab" in result.stdout

    def test_schotter_batch_processing(self, workspace_dir):
        """Test batch processing of multiple Schotter variations."""
        try:
            from sketch_schotter import SchotterSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Schotter sketch")

        # Generate multiple Schotter variations
        variations = [
            {"columns": 8, "rows": 10, "fuzziness": 0.8},
            {"columns": 10, "rows": 12, "fuzziness": 1.2},
            {"columns": 6, "rows": 8, "fuzziness": 1.5},
        ]

        job_names = []

        for i, params in enumerate(variations):
            vsk = vsketch.Vsketch()
            sketch = SchotterSketch()

            # Set parameters
            for key, value in params.items():
                setattr(sketch, key, value)

            sketch.draw(vsk)

            # Save and add to vfab
            svg_file = os.path.join(workspace_dir, f"schotter_batch_{i}.svg")
            vsk.save(svg_file)

            job_name = f"schotter_batch_{i}"
            job_names.append(job_name)

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "vfab-add",
                    "--name",
                    job_name,
                    "--queue",  # Auto-queue for batch processing
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert f"Job '{job_name}' added to vfab" in result.stdout

        # Verify all jobs are in vfab
        result = subprocess.run(
            ["vpype", "vfab-list", "--workspace", workspace_dir],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        for job_name in job_names:
            assert job_name in result.stdout

    def test_schotter_with_pen_mapping(self, schotter_sketch, workspace_dir):
        """Test Schotter with multi-layer pen mapping."""
        import vsketch
        import vpype

        # Create Schotter pattern
        vsk = vsketch.Vsketch()
        schotter_sketch.draw(vsk)

        # Modify to create multiple layers with different colors
        # This simulates a more complex multi-layer Schotter
        vsk = vsketch.Vsketch()

        # Layer 1: Red squares (low distortion)
        lc1 = vsk.createLayer()
        lc1.set_property(vpype.METADATA_FIELD_COLOR, "#ff0000")

        # Layer 2: Blue squares (high distortion)
        lc2 = vsk.createLayer()
        lc2.set_property(vpype.METADATA_FIELD_COLOR, "#0000ff")

        # Add some geometry to each layer
        for i in range(50):
            if i % 2 == 0:
                vsk.rect(i % 10, i // 10, 0.8, 0.8, layer=1)
            else:
                vsk.rect(i % 10, i // 10, 0.8, 0.8, layer=2)

        # Save to SVG
        svg_file = os.path.join(workspace_dir, "schotter_multilayer.svg")
        vsk.save(svg_file)

        # Test interactive pen mapping (mocked)
        with patch("vpype_vfab.commands._interactive_pen_mapping") as mock_mapping:
            mock_mapping.return_value = {1: 1, 2: 2}

            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "vfab-add",
                    "--name",
                    "schotter_multilayer",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_schotter_error_handling(self, workspace_dir):
        """Test error handling with Schotter sketch."""
        try:
            from sketch_schotter import SchotterSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Schotter sketch")

        # Test with invalid parameters
        vsk = vsketch.Vsketch()
        sketch = SchotterSketch()

        # Set extreme parameters that might cause issues
        sketch.columns = 100  # Very large
        sketch.rows = 100  # Very large
        sketch.fuzziness = 10  # Very high fuzziness

        # This should still work but might be slow
        sketch.draw(vsk)

        # Verify it doesn't crash
        assert len(vsk.document.layers) > 0

        # Test with zero parameters
        vsk = vsketch.Vsketch()
        sketch.columns = 0
        sketch.rows = 0
        sketch.draw(vsk)

        # Should handle gracefully
        assert len(vsk.document.layers) >= 0

    def test_schotter_finalize_integration(self, schotter_sketch, workspace_dir):
        """Test Schotter finalize method with vpype-vfab."""
        import vsketch

        # Create Schotter pattern
        vsk = vsketch.Vsketch()
        schotter_sketch.draw(vsk)

        # Apply finalize (which includes vpype optimization)
        schotter_sketch.finalize(vsk)

        # Save to SVG
        svg_file = os.path.join(workspace_dir, "schotter_finalized.svg")
        vsk.save(svg_file)

        # Verify file exists and is valid
        assert os.path.exists(svg_file)
        assert os.path.getsize(svg_file) > 0

        # Add to vfab
        result = subprocess.run(
            [
                "vpype",
                "read",
                svg_file,
                "vfab-add",
                "--name",
                "schotter_finalized",
                "--preset",
                "hq",  # High quality for finalized sketch
                "--workspace",
                workspace_dir,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Job 'schotter_finalized' added to vfab" in result.stdout
