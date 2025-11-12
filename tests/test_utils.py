"""Test utility functions."""

import tempfile
from pathlib import Path

import pytest
from vpype import Document

from vpype_plotty.utils import (
    format_job_list,
    format_job_status,
    generate_job_name,
    save_document_for_plotty,
    validate_preset,
)
from vpype_plotty.exceptions import PlottyJobError


class TestUtils:
    """Test utility functions."""

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

    def test_generate_job_name_from_metadata(self):
        """Test job name generation from document metadata."""
        document = Document()
        document.metadata = {"name": "test_from_metadata"}
        name = generate_job_name(document)
        assert name == "test_from_metadata"

    def test_validate_preset_valid(self):
        """Test validating valid presets."""
        assert validate_preset("fast") == "fast"
        assert validate_preset("default") == "default"
        assert validate_preset("hq") == "hq"

    def test_validate_preset_invalid(self):
        """Test validating invalid preset."""
        with pytest.raises(Exception):  # click.BadParameter
            validate_preset("invalid")

    def test_save_document_for_plotty(self):
        """Test saving document for ploTTY."""
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

    def test_save_document_for_plotty_error(self):
        """Test error handling when saving document."""
        document = Document()
        # Use invalid path that should cause an error
        invalid_path = Path("/invalid/path/that/does/not/exist")

        with pytest.raises(PlottyJobError):
            save_document_for_plotty(document, invalid_path, "test_job")

    def test_format_job_status_table(self):
        """Test formatting job status as table."""
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

    def test_format_job_status_json(self):
        """Test formatting job status as JSON."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
        }

        output = format_job_status(job_data, "json")
        assert '"name": "test_job"' in output
        assert '"state": "QUEUED"' in output

    def test_format_job_status_simple(self):
        """Test formatting job status as simple text."""
        job_data = {
            "name": "test_job",
            "state": "QUEUED",
        }

        output = format_job_status(job_data, "simple")
        assert output == "test_job: QUEUED"

    def test_format_job_list_table(self):
        """Test formatting job list as table."""
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
        assert "job1" in output
        assert "job2" in output
        assert "QUEUED" in output
        assert "NEW" in output

    def test_format_job_list_json(self):
        """Test formatting job list as JSON."""
        jobs = [
            {"name": "job1", "state": "QUEUED"},
            {"name": "job2", "state": "NEW"},
        ]

        output = format_job_list(jobs, "json")
        assert '"name": "job1"' in output
        assert '"name": "job2"' in output

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

    def test_format_job_list_empty(self):
        """Test formatting empty job list."""
        output = format_job_list([], "table")
        assert output == "No jobs found."
