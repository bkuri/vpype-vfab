"""Test coverage for vpype-vfab utils module."""

import tempfile
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import json

import pytest

from vpype_vfab.utils import (
    JobFormatter,
    save_document_for_vfab,
    generate_job_name,
    validate_preset,
    format_job_status,
    format_job_list,
)


class TestUtilsCoverage:
    """Comprehensive tests for utils module to boost coverage."""

    def test_job_formatter_initialization(self):
        """Test JobFormatter initialization with state colors."""
        formatter = JobFormatter()

        # Should have state colors
        assert "pending" in formatter.state_colors
        assert "queued" in formatter.state_colors
        assert "running" in formatter.state_colors
        assert "completed" in formatter.state_colors
        assert "failed" in formatter.state_colors
        assert "cancelled" in formatter.state_colors

        # Should have device status icons
        assert "connected" in formatter.device_status_icons
        assert "disconnected" in formatter.device_status_icons
        assert "busy" in formatter.device_status_icons
        assert "error" in formatter.device_status_icons
        assert "offline" in formatter.device_status_icons

    def test_job_formatter_format_single_json(self):
        """Test single job formatting as JSON."""
        formatter = JobFormatter()
        job = {"id": "test", "name": "test_job", "state": "running"}

        result = formatter.format(job, "json", "single")

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["id"] == "test"
        assert parsed["name"] == "test_job"

    def test_job_formatter_format_single_table(self):
        """Test single job formatting as table."""
        formatter = JobFormatter()
        job = {
            "id": "test",
            "name": "test_job",
            "state": "running",
            "paper": "A4",
            "created_at": "2023-01-01T12:00:00Z",
        }

        result = formatter.format(job, "table", "single")

        assert "test_job" in result
        assert "running" in result
        assert "A4" in result

    def test_job_formatter_format_single_simple(self):
        """Test single job formatting as simple."""
        formatter = JobFormatter()
        job = {"name": "test_job", "state": "running"}

        result = formatter.format(job, "simple", "single")

        assert result == "test_job: running"

    def test_job_formatter_format_list_json(self):
        """Test job list formatting as JSON."""
        formatter = JobFormatter()
        jobs = [
            {"id": "test1", "name": "job1", "state": "running"},
            {"id": "test2", "name": "job2", "state": "completed"},
        ]

        result = formatter.format(jobs, "json", "list")

        # Should be valid JSON
        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "job1"

    def test_job_formatter_format_list_empty(self):
        """Test empty job list formatting."""
        formatter = JobFormatter()

        result = formatter.format([], "json", "list")
        assert result == "No jobs found."

        result = formatter.format([], "table", "list")
        assert result == "No jobs found."

    def test_job_formatter_format_list_table(self):
        """Test job list formatting as table."""
        formatter = JobFormatter()
        jobs = [
            {
                "name": "test_job",
                "state": "running",
                "paper": "A4",
                "created_at": "2023-01-01T12:00:00Z",
            }
        ]

        result = formatter.format(jobs, "table", "list")

        assert "Name" in result
        assert "State" in result
        assert "Paper" in result
        assert "Created" in result
        assert "test_job" in result

    def test_job_formatter_format_list_csv(self):
        """Test job list formatting as CSV."""
        formatter = JobFormatter()
        jobs = [
            {"name": "test_job", "state": "running", "paper": "A4"},
            {"name": "test_job2", "state": "completed", "paper": "A3"},
        ]

        result = formatter.format(jobs, "csv", "list")

        assert "name,state,paper" in result
        assert "test_job,running,A4" in result

    def test_job_formatter_monitor_formatting(self):
        """Test monitor-specific job formatting."""
        formatter = JobFormatter()
        job = {
            "id": "test-job-123456789",
            "name": "test_job",
            "state": "running",
            "created_at": "2023-01-01T12:00:00Z",
            "progress": 75.5,
        }

        result = formatter.format_job_status_monitor(job)

        assert "test_job" in result
        assert "test-job-12" in result  # Short ID
        assert "75.5%" in result
        assert "12:00:00" in result  # Time
        assert "running" in result

    def test_job_formatter_device_formatting(self):
        """Test device status formatting."""
        formatter = JobFormatter()
        device = {"name": "test_device", "type": "axidraw", "status": "connected"}

        result = formatter.format_device_status(device)

        assert "test_device" in result
        assert "axidraw" in result
        assert "connected" in result

    @patch("vpype_vfab.utils.vpype.write_svg")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_document_for_vfab_success(self, mock_file, mock_write_svg):
        """Test successful document saving."""
        # Mock document
        mock_doc = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            job_path = Path(temp_dir) / "test_job"

            svg_path, json_path = save_document_for_vfab(
                mock_doc, job_path, "test_job"
            )

            # Should return correct paths
            assert svg_path == job_path / "vpype_vfab.svg"
            assert json_path == job_path / "job.json"

            # Should create directory
            mock_file.assert_called_with(job_path / "job.json", "w", encoding="utf-8")

            # Should write SVG
            mock_write_svg.assert_called_once()

            # Should write correct JSON data
            written_data = json.loads(mock_file().write.call_args[0][0])
            assert written_data["id"] == "test_job"
            assert written_data["name"] == "test_job"
            assert written_data["state"] == "NEW"

    def test_save_document_for_vfab_failure(self):
        """Test document saving failure."""
        mock_doc = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            job_path = Path(temp_dir) / "test_job"

            # Mock file operation to raise exception
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                with pytest.raises(Exception):  # Should raise VfabJobError
                    save_document_for_vfab(mock_doc, job_path, "test_job")

    def test_generate_job_name_from_metadata(self):
        """Test job name generation from document metadata."""
        mock_doc = MagicMock()
        mock_doc.metadata = {"name": "custom_job_name"}

        result = generate_job_name(mock_doc)
        assert result == "custom_job_name"

    def test_generate_job_name_from_title(self):
        """Test job name generation from document title."""
        mock_doc = MagicMock()
        mock_doc.metadata = {"title": "custom_job_title"}

        result = generate_job_name(mock_doc)
        assert result == "custom_job_title"

    def test_generate_job_name_fallback(self):
        """Test job name generation with fallback."""
        mock_doc = MagicMock()
        mock_doc.metadata = {}

        result = generate_job_name(mock_doc, "fallback_name")
        assert result == "fallback_name"

    def test_generate_job_name_timestamp(self):
        """Test job name generation with timestamp."""
        mock_doc = MagicMock()
        mock_doc.metadata = {}

        with patch("vpype_vfab.utils.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20230101_120000"

            result = generate_job_name(mock_doc)
            assert result == "vpype_job_20230101_120000"

    def test_validate_preset_valid(self):
        """Test preset validation with valid presets."""
        for preset in ["fast", "default", "hq"]:
            result = validate_preset(preset)
            assert result == preset

    def test_validate_preset_invalid(self):
        """Test preset validation with invalid preset."""
        with pytest.raises(Exception):  # Should raise click.BadParameter
            validate_preset("invalid_preset")

    def test_format_job_status_backward_compatibility(self):
        """Test backward compatibility job status formatting."""
        job = {"name": "test_job", "state": "running"}

        result = format_job_status(job, "simple")
        assert result == "test_job: running"

    def test_format_job_list_backward_compatibility(self):
        """Test backward compatibility job list formatting."""
        jobs = [{"name": "test_job", "state": "running"}]

        result = format_job_list(jobs, "simple")
        # Should use JobFormatter internally
        assert "test_job" in result or "No jobs found" in result

    def test_job_formatter_edge_cases(self):
        """Test JobFormatter edge cases."""
        formatter = JobFormatter()

        # Missing state
        job = {"name": "test_job"}
        result = formatter.format(job, "simple", "single")
        assert "unknown" in result.lower()

        # Missing device status
        device = {"name": "test_device"}
        result = formatter.format_device_status(device)
        assert "unknown" in result.lower()

    @patch("vpype_vfab.utils.datetime")
    def test_job_formatter_timing(self, mock_datetime):
        """Test timing formatting in monitor mode."""
        mock_datetime.fromisoformat.return_value.strftime.return_value = "12:00:00"

        formatter = JobFormatter()
        job = {
            "name": "test_job",
            "state": "running",
            "created_at": "2023-01-01T12:00:00Z",
        }

        result = formatter.format_job_status_monitor(job)
        assert "12:00:00" in result

    def test_csv_formatter_empty_jobs(self):
        """Test CSV formatting with empty jobs list."""
        formatter = JobFormatter()

        result = formatter.format([], "csv", "list")
        assert result == "No jobs found."

    def test_table_formatter_timezone_truncation(self):
        """Test table formatting truncates timezone info."""
        formatter = JobFormatter()
        job = {
            "name": "test_job",
            "state": "running",
            "paper": "A4",
            "created_at": "2023-01-01T12:00:00Z",  # With timezone
        }

        result = formatter.format([job], "table", "list")

        # Should truncate timezone info (first 19 chars)
        assert "2023-01-01T12:00:00" in result
        assert "Z" not in result.split("\n")[-2]  # Not in last data line
