#!/usr/bin/env python3
"""Simple test script to verify vpype-plotty functionality."""

import tempfile
from pathlib import Path

from vpype_plotty.config import PlottyConfig
from vpype_plotty.database import PlottyIntegration
from vpype_plotty.utils import generate_job_name, validate_preset

import vpype


def test_basic_functionality():
    """Test basic functionality of vpype-plotty."""
    print("Testing vpype-plotty basic functionality...")

    # Test 1: Configuration
    print("\n1. Testing configuration...")
    with tempfile.TemporaryDirectory() as temp_dir:
        config = PlottyConfig(temp_dir)
        assert config.workspace_path == Path(temp_dir)
        print("✓ Configuration works")

    # Test 2: Preset validation
    print("\n2. Testing preset validation...")
    assert validate_preset("fast") == "fast"
    assert validate_preset("default") == "default"
    assert validate_preset("hq") == "hq"
    print("✓ Preset validation works")

    # Test 3: Job name generation
    print("\n3. Testing job name generation...")
    document = vpype.Document()
    name = generate_job_name(document, "test_name")
    assert name == "test_name"
    print("✓ Job name generation works")

    # Test 4: Database integration
    print("\n4. Testing database integration...")
    with tempfile.TemporaryDirectory() as temp_dir:
        plotty = PlottyIntegration(temp_dir)

        # Create a simple document
        document = vpype.Document()
        from shapely.geometry import LineString

        line = LineString([(0, 0), (10, 10)])
        document.add(line)

        # Add job
        job_id = plotty.add_job(document, "test_job", "fast", "A4")
        assert job_id == "test_job"

        # Check job status
        job_data = plotty.get_job_status("test_job")
        assert job_data["name"] == "test_job"
        assert job_data["state"] == "NEW"

        # List jobs
        jobs = plotty.list_jobs()
        assert len(jobs) == 1
        assert jobs[0]["name"] == "test_job"

        print("✓ Database integration works")

    # Test 5: Import commands
    print("\n5. Testing command imports...")
    try:
        import vpype_plotty.commands

        # Test that commands are available
        assert hasattr(vpype_plotty.commands, "plotty_add")
        assert hasattr(vpype_plotty.commands, "plotty_queue")

        print("✓ Command imports work")
    except ImportError as e:
        print(f"✗ Command import failed: {e}")
        return False

    print("\n🎉 All tests passed! vpype-plotty is working correctly.")
    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)
