"""Enhanced test utility functions with Qt mocking setup."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Set up Qt mocks BEFORE importing vpype modules
os.environ["DISPLAY"] = ""
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["PYQT_QPA_PLATFORM"] = "offscreen"

qt_modules = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",
    "shiboken6",
    "shiboken6.Shiboken",
]

for module in qt_modules:
    sys.modules[module] = MagicMock()

# Now we can safely import vpype modules
from vpype import Document

from src.utils import (
    format_job_list,
    format_job_status,
    generate_job_name,
    save_document_for_plotty,
    validate_preset,
)
from src.exceptions import PlottyJobError


class TestUtilsEnhanced:
    """Enhanced test utility functions with comprehensive coverage."""

    def test_generate_job_name_with_fallback(self):
        """Test job name generation with fallback."""
        document = Document()
        name = generate_job_name(document, "fallback_name")
        assert name == "fallback_name"

    def test_generate_job_name_auto(self):
        """Test automatic job name generation."""
        document = Document()
        name = generate_job_name(document)
        assert name.startswith("vpype_job_")
        assert len(name) > len("vpype_job_")

    def test_generate_job_name_from_metadata_name(self):
        """Test job name generation from document metadata name."""
        document = Document()
        document.metadata = {"name": "test_from_metadata"}
        name = generate_job_name(document)
        assert name == "test_from_metadata"

    def test_generate_job_name_from_metadata_title(self):
        """Test job name generation from document metadata title."""
        document = Document()
        document.metadata = {"title": "test_title"}
        name = generate_job_name(document)
        assert name == "test_title"

    def test_generate_job_name_metadata_priority(self):
        """Test that 'name' takes priority over 'title' in metadata."""
        document = Document()
        document.metadata = {"name": "priority_name", "title": "priority_title"}
        name = generate_job_name(document)
        assert name == "priority_name"

    def test_generate_job_name_empty_metadata(self):
        """Test job name generation with empty metadata."""
        document = Document()
        document.metadata = {}
        name = generate_job_name(document)
        assert name.startswith("vpype_job_")

    def test_validate_preset_valid(self):
        """Test validating valid presets."""
        assert validate_preset("fast") == "fast"
        assert validate_preset("default") == "default"
        assert validate_preset("hq") == "hq"

    def test_validate_preset_invalid(self):
        """Test validating invalid preset."""
        with pytest.raises(Exception):  # click.BadParameter
            validate_preset("invalid")

    def test_validate_preset_case_sensitivity(self):
        """Test that preset validation is case sensitive."""
        with pytest.raises(Exception):  # click.BadParameter
            validate_preset("Fast")  # Should be "fast"

    def test_save_document_for_plotty_basic(self):
        """Test basic document saving for ploTTY."""
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()
            job_path = Path(temp_dir) / "test_job"

            svg_path, job_json_path = save_document_for_plotty(
                document, job_path, "test_job"
            )

            assert svg_path.exists()
            assert job_json_path.exists()
            assert svg_path.name == "src.svg"
            assert job_json_path.name == "job.json"

    def test_save_document_for_plotty_content(self):
        """Test that saved document contains correct content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()
            job_path = Path(temp_dir) / "test_job"

            svg_path, job_json_path = save_document_for_plotty(
                document, job_path, "test_job"
            )

            # Check job.json content
            with open(job_json_path, "r") as f:
                job_data = json.load(f)

            assert job_data["id"] == "test_job"
            assert job_data["name"] == "test_job"
            assert job_data["paper"] == "A4"
            assert job_data["state"] == "NEW"
            assert "created_at" in job_data
            assert job_data["metadata"]["created_by"] == "vpype-plotty"
            assert job_data["metadata"]["source"] == "vpype document"

    def test_save_document_for_plotty_existing_dir(self):
        """Test saving to existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()
            job_path = Path(temp_dir) / "existing_job"
            job_path.mkdir()  # Create directory first

            svg_path, job_json_path = save_document_for_plotty(
                document, job_path, "test_job"
            )

            assert svg_path.exists()
            assert job_json_path.exists()

    def test_save_document_for_plotty_nested_dirs(self):
        """Test saving to nested directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()
            job_path = Path(temp_dir) / "level1" / "level2" / "test_job"

            svg_path, job_json_path = save_document_for_plotty(
                document, job_path, "test_job"
            )

            assert svg_path.exists()
            assert job_json_path.exists()
            assert job_path.exists()

    def test_save_document_for_plotty_error(self):
        """Test error handling when saving document."""
        document = Document()
        # Use invalid path that should cause an error
        invalid_path = Path("/invalid/path/that/does/not/exist")

        with pytest.raises(PlottyJobError) as exc_info:
            save_document_for_plotty(document, invalid_path, "test_job")

        assert "Failed to save document for ploTTY" in str(exc_info.value)

    @patch("vpype.write_svg")
    def test_save_document_for_plotty_vpype_error(self, mock_write_svg):
        """Test handling of vpype write_svg errors."""
        mock_write_svg.side_effect = Exception("vpype error")

        with tempfile.TemporaryDirectory() as temp_dir:
            document = Document()
            job_path = Path(temp_dir) / "test_job"

            with pytest.raises(PlottyJobError) as exc_info:
                save_document_for_plotty(document, job_path, "test_job")

            assert "Failed to save document for ploTTY" in str(exc_info.value)

    def test_format_job_status_table_complete(self):
        """Test formatting job status as table with complete data."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
            "paper": "A4",
            "created_at": "2023-01-01T12:00:00Z",
        }

        output = format_job_status(job_data, "table")
        assert "test_job" in output
        assert "QUEUED" in output
        assert "A4" in output
        assert "2023-01-01T12:00:00Z" in output

    def test_format_job_status_table_missing_fields(self):
        """Test formatting job status as table with missing fields."""
        job_data = {
            "name": "test_job",
            # Missing state, paper, created_at
        }

        output = format_job_status(job_data, "table")
        assert "test_job" in output
        assert "Unknown" in output  # Should appear for missing fields

    def test_format_job_status_json(self):
        """Test formatting job status as JSON."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
        }

        output = format_job_status(job_data, "json")
        parsed = json.loads(output)
        assert parsed["name"] == "test_job"
        assert parsed["state"] == "QUEUED"

    def test_format_job_status_simple(self):
        """Test formatting job status as simple text."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
        }

        output = format_job_status(job_data, "simple")
        assert output == "test_job: QUEUED"

    def test_format_job_status_default_format(self):
        """Test that default format is table."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
        }

        output = format_job_status(job_data)  # No format specified
        assert "test_job" in output
        assert "QUEUED" in output

    def test_format_job_list_table_multiple(self):
        """Test formatting multiple jobs as table."""
        jobs = [
            {
                "name": "job1",
                "state": "QUEUED",
                "paper": "A4",
                "created_at": "2023-01-01T12:00:00Z",
            },
            {
                "name": "job2",
                "state": "NEW",
                "paper": "A3",
                "created_at": "2023-01-01T13:00:00Z",
            },
        ]

        output = format_job_list(jobs, "table")
        lines = output.split("\n")

        # Check header
        assert "Name" in lines[0]
        assert "State" in lines[0]
        assert "Paper" in lines[0]
        assert "Created" in lines[0]

        # Check separator
        assert "---" in lines[1]

        # Check data rows
        assert "job1" in output
        assert "job2" in output
        assert "QUEUED" in output
        assert "NEW" in output

    def test_format_job_list_table_timezone_truncation(self):
        """Test that timezone info is truncated in table format."""
        jobs = [
            {
                "name": "job1",
                "state": "QUEUED",
                "paper": "A4",
                "created_at": "2023-01-01T12:00:00.123456+00:00",
            },
        ]

        output = format_job_list(jobs, "table")
        # Should truncate after 19 characters (YYYY-MM-DDTHH:MM:SS)
        assert "2023-01-01T12:00:00" in output
        assert ".123456" not in output

    def test_format_job_list_json(self):
        """Test formatting job list as JSON."""
        jobs = [
            {"name": "job1", "state": "QUEUED"},
            {"name": "job2", "state": "NEW"},
        ]

        output = format_job_list(jobs, "json")
        parsed = json.loads(output)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "job1"
        assert parsed[1]["name"] == "job2"

    def test_format_job_list_csv(self):
        """Test formatting job list as CSV."""
        jobs = [
            {"name": "job1", "state": "QUEUED"},
            {"name": "job2", "state": "NEW"},
        ]

        output = format_job_list(jobs, "csv")
        lines = output.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows
        assert "name,state" in lines[0]
        assert "job1,QUEUED" in lines[1]
        assert "job2,NEW" in lines[2]

    def test_format_job_list_csv_complex_data(self):
        """Test CSV formatting with complex job data."""
        jobs = [
            {
                "name": "job1",
                "state": "QUEUED",
                "paper": "A4",
                "created_at": "2023-01-01T12:00:00Z",
                "metadata": {"key": "value"},
            },
        ]

        output = format_job_list(jobs, "csv")
        lines = output.strip().split("\n")
        assert len(lines) == 2  # Header + 1 data row
        assert "job1" in lines[1]

    def test_format_job_list_empty(self):
        """Test formatting empty job list."""
        output = format_job_list([], "table")
        assert output == "No jobs found."

    def test_format_job_list_default_format(self):
        """Test that default format is table."""
        jobs = [{"name": "job1", "state": "QUEUED"}]
        output = format_job_list(jobs)  # No format specified
        assert "job1" in output
        assert "QUEUED" in output

    def test_format_job_list_missing_fields_table(self):
        """Test table formatting with missing job fields."""
        jobs = [
            {"name": "job1"},  # Missing state, paper, created_at
        ]

        output = format_job_list(jobs, "table")
        assert "job1" in output
        assert "Unknown" in output
