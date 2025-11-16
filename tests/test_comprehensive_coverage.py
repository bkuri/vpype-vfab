#!/usr/bin/env python3
"""Comprehensive coverage test with Qt mocking for all modules."""

import json
import sys
from pathlib import Path
import tempfile

# Set up Qt mocks before any imports
sys.path.insert(0, "/home/bk/source/vpype-vfab")
from tests.conftest import setup_qt_mocks

setup_qt_mocks()

import coverage


def test_comprehensive_coverage():
    """Test comprehensive coverage with mocked Qt."""
    cov = coverage.Coverage(source=["src"])
    cov.start()

    # Import all modules after Qt mocks are set up
    from vpype_vfab import config, database, utils, exceptions, monitor

    # Test exceptions module (already covered well)
    error = exceptions.PlottyError("Test error")
    assert str(error) == "Test error"

    not_found = exceptions.VfabNotFoundError("Not found", "/path")
    assert "Not found" in str(not_found)

    job_error = exceptions.VfabJobError("Job failed", "job123")
    assert "Job failed" in str(job_error)

    config_error = exceptions.VfabConfigError("Config error", "/config/path")
    assert "Config error" in str(config_error)

    connection_error = exceptions.PlottyConnectionError("Connection failed", 5.0)
    assert "Connection failed" in str(connection_error)

    # Test config module
    with tempfile.TemporaryDirectory() as tmp_dir:
        workspace_path = Path(tmp_dir)
        config_manager = config.PlottyConfig(str(workspace_path))
        assert config_manager.workspace_path == workspace_path

        # Test workspace finding
        found_workspace = config_manager._find_workspace(str(workspace_path))
        assert found_workspace == workspace_path

    # Test database module
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir)
        integration = database.PlottyIntegration(str(db_path))
        assert integration is not None
        assert integration.workspace.exists()

        # Test plotty availability check
        available = integration._vfab_available()
        assert isinstance(available, bool)

    # Test utils module
    from vpype import Document

    with tempfile.TemporaryDirectory() as tmp_dir:
        job_path = Path(tmp_dir) / "test_job"
        doc = Document()

        # Test save document function
        svg_path, job_json_path = utils.save_document_for_vfab(
            doc, job_path, "test_job"
        )
        assert svg_path.exists()
        assert job_json_path.exists()

        # Verify job JSON
        with open(job_json_path, "r") as f:
            job_data = json.load(f)
        assert job_data["id"] == "test_job"
        assert job_data["state"] == "NEW"

    # Test streamlined monitor
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_monitor = monitor.SimplePlottyMonitor(tmp_dir, poll_rate=0.5)
        assert test_monitor.poll_rate == 0.5
        assert test_monitor.workspace == tmp_dir

        # Test job status formatting
        test_job = {
            "name": "test_job",
            "state": "running",
            "id": "1234567890abcdef",
            "progress": 75.5,
            "created_at": "2024-01-01T12:00:00",
        }
        status = test_monitor.format_job_status(test_job)
        assert "test_job" in status
        assert "12345678" in status  # Short ID
        assert "75.5%" in status
        assert "running" in status

        # Test device status formatting
        test_device = {"name": "axidraw", "status": "connected", "type": "AxiDraw"}
        device_status = test_monitor.format_device_status(test_device)
        assert "axidraw" in device_status
        assert "connected" in device_status

    cov.stop()
    cov.save()

    print("=== Comprehensive Coverage Report (with mocked Qt) ===")
    cov.report()

    # Get detailed coverage by module
    print("\n=== Module-by-Module Coverage ===")
    cov2 = coverage.Coverage(source=["src"])
    cov2.load()

    modules_to_check = [
        "vpype_vfab.exceptions",
        "vpype_vfab.config",
        "vpype_vfab.database",
        "vpype_vfab.utils",
        "vpype_vfab.monitor",
        "vpype_vfab.commands",
    ]

    total_statements = 0
    total_missing = 0

    for module in modules_to_check:
        try:
            analysis = cov2.analysis2(module)
            statements = len(analysis[1])  # executable lines
            missing = len(analysis[2])  # missing lines
            covered = statements - missing
            percentage = (covered / statements * 100) if statements > 0 else 0

            print(
                f"{module}: {statements} stmts, {missing} miss, {percentage:.1f}% cover"
            )

            total_statements += statements
            total_missing += missing
        except Exception as e:
            print(f"{module}: Error analyzing - {e}")

    overall_percentage = (
        ((total_statements - total_missing) / total_statements * 100)
        if total_statements > 0
        else 0
    )
    print(
        f"\nOVERALL: {total_statements} stmts, {total_missing} miss, {overall_percentage:.1f}% cover"
    )

    return cov, overall_percentage


if __name__ == "__main__":
    cov, coverage_pct = test_comprehensive_coverage()
    print(f"\n🎯 Final Coverage Achievement: {coverage_pct:.1f}%")

    if coverage_pct >= 85:
        print("✅ SUCCESS: Achieved 85%+ coverage target!")
    elif coverage_pct >= 80:
        print("🟡 CLOSE: Nearly there, need a bit more coverage")
    else:
        print("❌ NEEDS WORK: Significantly more coverage required")
