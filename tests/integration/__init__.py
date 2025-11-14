"""Test utilities for sandbox environment setup and management."""

import sys
from pathlib import Path

# Add sandbox to Python path for all tests
sandbox_dir = Path(__file__).parent.parent.parent / "sandbox"
if sandbox_dir.exists():
    sys.path.insert(0, str(sandbox_dir))
    sys.path.insert(0, str(sandbox_dir / "vsketch"))
    sys.path.insert(0, str(sandbox_dir / "plotty" / "src"))


def get_sandbox_config():
    """Get sandbox configuration for tests."""
    sandbox_dir = Path(__file__).parent.parent.parent / "sandbox"

    if not sandbox_dir.exists():
        return None

    return {
        "sandbox_dir": sandbox_dir,
        "vsketch_dir": sandbox_dir / "vsketch",
        "plotty_dir": sandbox_dir / "plotty",
        "vsketch_examples": {
            "schotter": sandbox_dir
            / "vsketch"
            / "examples"
            / "schotter"
            / "sketch_schotter.py",
            "quick_draw": sandbox_dir
            / "vsketch"
            / "examples"
            / "quick_draw"
            / "sketch_quick_draw.py",
            "random_lines": sandbox_dir
            / "vsketch"
            / "examples"
            / "random_lines"
            / "sketch_random_lines.py",
            "polygons": sandbox_dir
            / "vsketch"
            / "examples"
            / "polygons"
            / "sketch_polygons.py",
            "transforms": sandbox_dir
            / "vsketch"
            / "examples"
            / "transforms"
            / "sketch_transforms.py",
        },
        "plotty_config": sandbox_dir / "plotty" / "config" / "config.yaml",
        "plotty_presets": sandbox_dir / "plotty" / "config" / "vpype-presets.yaml",
    }


def import_vsketch_example(example_name):
    """Import a vsketch example from sandbox."""
    config = get_sandbox_config()
    if not config:
        return None

    example_path = config["vsketch_examples"].get(example_name)
    if not example_path or not example_path.exists():
        return None

    # Add example directory to path
    example_dir = example_path.parent
    if str(example_dir) not in sys.path:
        sys.path.insert(0, str(example_dir))

    try:
        # Import the sketch class
        if example_name == "schotter":
            from sketch_schotter import SchotterSketch

            return SchotterSketch()
        elif example_name == "quick_draw":
            from sketch_quick_draw import QuickDrawSketch

            return QuickDrawSketch()
        elif example_name == "random_lines":
            from sketch_random_lines import RandomLinesSketch

            return RandomLinesSketch()
        elif example_name == "polygons":
            from sketch_polygons import PolygonsSketch

            return PolygonsSketch()
        elif example_name == "transforms":
            from sketch_transforms import TransformsSketch

            return TransformsSketch()
    except ImportError:
        return None

    return None


def create_mock_plotty_workspace(workspace_dir):
    """Create a mock ploTTY workspace for testing."""
    workspace_path = Path(workspace_dir)

    # Create ploTTY directory structure
    (workspace_path / "jobs").mkdir(parents=True, exist_ok=True)
    (workspace_path / "devices").mkdir(parents=True, exist_ok=True)
    (workspace_path / "logs").mkdir(parents=True, exist_ok=True)

    # Create mock ploTTY config
    config_content = """
websocket:
  enabled: true
  port: 8765
  host: localhost

devices:
  axidraw:auto:
    type: axidraw
    port: auto
    config:
      speed: 50
      acceleration: 50

database:
  type: sqlite
  path: ploTTY.db

logging:
  level: INFO
  file: logs/plotty.log
"""

    config_file = workspace_path / "config.yaml"
    config_file.write_text(config_content)

    # Create mock database
    db_file = workspace_path / "ploTTY.db"
    db_file.touch()

    return workspace_path


def mock_quickdraw_data():
    """Create mock Quick Draw data for testing."""
    return {
        "key_id": 1,
        "country_code": b"US",
        "recognized": 1,
        "timestamp": 1234567890,
        "image": [([10, 20, 30, 40], [15, 25, 35, 45])],
    }


def skip_if_no_sandbox(test_func):
    """Decorator to skip tests if sandbox is not available."""

    def wrapper(*args, **kwargs):
        config = get_sandbox_config()
        if not config:
            import pytest

            pytest.skip("Sandbox environment not available")
        return test_func(*args, **kwargs)

    return wrapper


def skip_if_no_vsketch(test_func):
    """Decorator to skip tests if vsketch is not available."""

    def wrapper(*args, **kwargs):
        try:
            import vsketch

            _ = vsketch  # Mark as used
        except ImportError:
            import pytest

            pytest.skip("vsketch not available")
        return test_func(*args, **kwargs)

    return wrapper
