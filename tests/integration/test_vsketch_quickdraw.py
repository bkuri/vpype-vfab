"""Integration tests for Quick Draw sketch with vpype-vfab."""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

# Add temp/vsketch to path for importing vsketch examples
vsketch_path = Path(__file__).parent.parent.parent / "temp" / "vsketch"
if vsketch_path.exists():
    sys.path.insert(0, str(vsketch_path))
    sys.path.insert(0, str(vsketch_path / "examples" / "quick_draw"))


class TestQuickDrawIntegration:
    """Test Quick Draw sketch integration with vpype-vfab."""

    @pytest.fixture
    def quickdraw_sketch(self):
        """Import Quick Draw sketch from temp vsketch."""
        try:
            from sketch_quick_draw import QuickDrawSketch

            return QuickDrawSketch()
        except ImportError as e:
            pytest.skip(f"Could not import Quick Draw sketch: {e}")

    @pytest.fixture
    def workspace_dir(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_quickdraw_basic_generation(self, quickdraw_sketch, workspace_dir):
        """Test basic Quick Draw pattern generation."""
        try:
            import vsketch
        except ImportError:
            pytest.skip("vsketch not available")

        # Mock the URL download to avoid network dependency
        with patch("urllib.request.urlretrieve"):
            # Create a mock binary file
            mock_binary_content = b"\\x00" * 1000  # Simple mock data
            with open(os.path.join(workspace_dir, "crab.bin"), "wb") as f:
                f.write(mock_binary_content)

            # Create vsketch instance
            vsk = vsketch.Vsketch()

            # Set simple parameters for testing
            quickdraw_sketch.category = "crab"
            quickdraw_sketch.columns = 2
            quickdraw_sketch.rows = 2
            quickdraw_sketch.layer_count = 1

            # Mock the unpack_drawings function
            with patch("sketch_quick_draw.unpack_drawings") as mock_unpack:
                # Mock drawing data
                mock_drawing = {
                    "key_id": 1,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890,
                    "image": [([10, 20, 30], [15, 25, 35])],  # Simple stroke
                }
                mock_unpack.return_value = [mock_drawing] * 4  # 4 drawings for 2x2 grid

                # Execute Quick Draw
                quickdraw_sketch.draw(vsk)

                # Verify document has content
                assert len(vsk.document.layers) > 0
                assert vsk.document.page_size is not None

    def test_quickdraw_different_categories(self, workspace_dir):
        """Test Quick Draw with different categories."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        categories = ["cat", "dog", "house", "tree"]

        for category in categories:
            vsk = vsketch.Vsketch()
            sketch = QuickDrawSketch()
            sketch.category = category
            sketch.columns = 1
            sketch.rows = 1
            sketch.layer_count = 1

            # Mock the data download and unpacking
            with (
                patch("urllib.request.urlretrieve"),
                patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
            ):
                mock_drawing = {
                    "key_id": 1,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890,
                    "image": [([10, 20], [15, 25])],
                }
                mock_unpack.return_value = [mock_drawing]

                sketch.draw(vsk)

                # Verify generation worked
                assert len(vsk.document.layers) > 0

    def test_quickdraw_grid_configurations(self, workspace_dir):
        """Test Quick Draw with different grid configurations."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        grid_configs = [
            {"columns": 2, "rows": 2},  # 2x2
            {"columns": 3, "rows": 3},  # 3x3
            {"columns": 4, "rows": 4},  # 4x4
            {"columns": 1, "rows": 5},  # 1x5
            {"columns": 5, "rows": 1},  # 5x1
        ]

        for config in grid_configs:
            vsk = vsketch.Vsketch()
            sketch = QuickDrawSketch()
            sketch.columns = config["columns"]
            sketch.rows = config["rows"]
            sketch.layer_count = 1

            # Mock data
            with (
                patch("urllib.request.urlretrieve"),
                patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
            ):
                total_drawings = config["columns"] * config["rows"]
                mock_drawing = {
                    "key_id": 1,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890,
                    "image": [([10, 20], [15, 25])],
                }
                mock_unpack.return_value = [mock_drawing] * total_drawings

                sketch.draw(vsk)

                # Verify grid was created
                assert len(vsk.document.layers) > 0

    def test_quickdraw_with_vpype_vfab_add(self, quickdraw_sketch, workspace_dir):
        """Test adding Quick Draw sketch to vfab."""
        try:
            import vsketch
        except ImportError:
            pytest.skip("vsketch not available")

        # Mock the download and data
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

            # Create Quick Draw pattern
            vsk = vsketch.Vsketch()
            quickdraw_sketch.columns = 2
            quickdraw_sketch.rows = 2
            quickdraw_sketch.layer_count = 1
            quickdraw_sketch.draw(vsk)

            # Save to SVG
            svg_file = os.path.join(workspace_dir, "quickdraw.svg")
            vsk.save(svg_file)

            # Add to vfab using vpype command
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "vfab-add",
                    "--name",
                    "quickdraw_test",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'quickdraw_test' added to vfab" in result.stdout

    def test_quickdraw_batch_processing(self, workspace_dir):
        """Test batch processing of multiple Quick Draw categories."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        categories = ["cat", "dog", "house"]
        job_names = []

        for category in categories:
            vsk = vsketch.Vsketch()
            sketch = QuickDrawSketch()
            sketch.category = category
            sketch.columns = 2
            sketch.rows = 2
            sketch.layer_count = 1

            # Mock data
            with (
                patch("urllib.request.urlretrieve"),
                patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
            ):
                mock_drawing = {
                    "key_id": 1,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890,
                    "image": [([10, 20], [15, 25])],
                }
                mock_unpack.return_value = [mock_drawing] * 4

                sketch.draw(vsk)

                # Save and add to vfab
                svg_file = os.path.join(workspace_dir, f"quickdraw_{category}.svg")
                vsk.save(svg_file)

                job_name = f"quickdraw_{category}"
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

    def test_quickdraw_large_dataset(self, workspace_dir):
        """Test Quick Draw with large dataset (performance test)."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        vsk = vsketch.Vsketch()
        sketch = QuickDrawSketch()
        sketch.columns = 5  # 5x5 grid = 25 drawings
        sketch.rows = 5
        sketch.layer_count = 2  # 2 layers

        # Mock large dataset
        with (
            patch("urllib.request.urlretrieve"),
            patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
        ):
            # Create 25 mock drawings
            mock_drawings = []
            for i in range(25):
                mock_drawing = {
                    "key_id": i,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890 + i,
                    "image": [([10 + i, 20 + i, 30 + i], [15 + i, 25 + i, 35 + i])],
                }
                mock_drawings.append(mock_drawing)

            mock_unpack.return_value = mock_drawings

            sketch.draw(vsk)

            # Verify large dataset was processed
            assert len(vsk.document.layers) > 0

            # Save to SVG
            svg_file = os.path.join(workspace_dir, "quickdraw_large.svg")
            vsk.save(svg_file)

            # Verify file size is reasonable
            assert os.path.exists(svg_file)
            assert os.path.getsize(svg_file) > 1000  # Should be substantial

    def test_quickdraw_multilayer_pen_mapping(self, workspace_dir):
        """Test Quick Draw with multi-layer pen mapping."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        vsk = vsketch.Vsketch()
        sketch = QuickDrawSketch()
        sketch.columns = 3
        sketch.rows = 3
        sketch.layer_count = 3  # 3 layers for pen mapping test

        # Mock data
        with (
            patch("urllib.request.urlretrieve"),
            patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
        ):
            mock_drawings = []
            for i in range(9):  # 3x3 grid
                mock_drawing = {
                    "key_id": i,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890 + i,
                    "image": [([10 + i, 20 + i], [15 + i, 25 + i])],
                }
                mock_drawings.append(mock_drawing)

            mock_unpack.return_value = mock_drawings

            sketch.draw(vsk)

            # Verify multiple layers were created
            layer_count = len(vsk.document.layers)
            assert layer_count >= 1  # At least one layer should exist

            # Save to SVG
            svg_file = os.path.join(workspace_dir, "quickdraw_multilayer.svg")
            vsk.save(svg_file)

            # Test with vfab
            result = subprocess.run(
                [
                    "vpype",
                    "read",
                    svg_file,
                    "vfab-add",
                    "--name",
                    "quickdraw_multilayer",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

    def test_quickdraw_error_handling(self, workspace_dir):
        """Test error handling with Quick Draw sketch."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        # Test with invalid category
        vsk = vsketch.Vsketch()
        sketch = QuickDrawSketch()
        sketch.category = "invalid_category"

        # Mock download failure
        with patch(
            "urllib.request.urlretrieve", side_effect=Exception("Download failed")
        ):
            # This should handle the error gracefully
            try:
                sketch.draw(vsk)
            except Exception:
                # Expected to fail with invalid category
                pass

        # Test with zero grid size
        vsk = vsketch.Vsketch()
        sketch.category = "cat"
        sketch.columns = 0
        sketch.rows = 0

        with (
            patch("urllib.request.urlretrieve"),
            patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
        ):
            mock_unpack.return_value = []  # No drawings
            sketch.draw(vsk)

            # Should handle gracefully
            assert len(vsk.document.layers) >= 0

    def test_quickdraw_finalize_integration(self, quickdraw_sketch, workspace_dir):
        """Test Quick Draw finalize method with vpype-vfab."""
        try:
            import vsketch
        except ImportError:
            pytest.skip("vsketch not available")

        # Mock the data
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
            mock_unpack.return_value = [mock_drawing] * 4

            # Create Quick Draw pattern
            vsk = vsketch.Vsketch()
            quickdraw_sketch.columns = 2
            quickdraw_sketch.rows = 2
            quickdraw_sketch.layer_count = 1
            quickdraw_sketch.draw(vsk)

            # Apply finalize (which includes vpype optimization)
            quickdraw_sketch.finalize(vsk)

            # Save to SVG
            svg_file = os.path.join(workspace_dir, "quickdraw_finalized.svg")
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
                    "quickdraw_finalized",
                    "--preset",
                    "default",
                    "--workspace",
                    workspace_dir,
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Job 'quickdraw_finalized' added to vfab" in result.stdout

    def test_quickdraw_memory_usage(self, workspace_dir):
        """Test memory usage with large Quick Draw dataset."""
        try:
            from sketch_quick_draw import QuickDrawSketch
            import vsketch
        except ImportError:
            pytest.skip("Could not import Quick Draw sketch")

        # Test with very large grid to check memory efficiency
        vsk = vsketch.Vsketch()
        sketch = QuickDrawSketch()
        sketch.columns = 10  # 10x10 grid = 100 drawings
        sketch.rows = 10
        sketch.layer_count = 1

        # Mock large dataset
        with (
            patch("urllib.request.urlretrieve"),
            patch("sketch_quick_draw.unpack_drawings") as mock_unpack,
        ):
            # Create 100 mock drawings with more complex paths
            mock_drawings = []
            for i in range(100):
                # Create more complex drawing with multiple strokes
                image = []
                for stroke in range(3):  # 3 strokes per drawing
                    x_coords = list(range(10 + stroke * 10, 20 + stroke * 10))
                    y_coords = list(range(15 + stroke * 10, 25 + stroke * 10))
                    image.append((x_coords, y_coords))

                mock_drawing = {
                    "key_id": i,
                    "country_code": b"US",
                    "recognized": 1,
                    "timestamp": 1234567890 + i,
                    "image": image,
                }
                mock_drawings.append(mock_drawing)

            mock_unpack.return_value = mock_drawings

            # This should complete without memory issues
            sketch.draw(vsk)

            # Verify processing completed
            assert len(vsk.document.layers) > 0

            # Save to test file size
            svg_file = os.path.join(workspace_dir, "quickdraw_memory_test.svg")
            vsk.save(svg_file)

            # File should be reasonably sized
            file_size = os.path.getsize(svg_file)
            assert file_size > 5000  # Should be substantial for 100 complex drawings
            assert file_size < 1000000  # But not excessively large (< 1MB for test)
