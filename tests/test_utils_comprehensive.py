"""Comprehensive tests for vpype-vfab utilities."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import io
import csv

import pytest

# Mock vpype imports to avoid Qt display issues
mock_vpype = MagicMock()
mock_vpype.__version__ = "1.15.0"
sys.modules["vpype"] = mock_vpype
sys.modules["vpype.Document"] = MagicMock()

# Mock click to avoid display issues
sys.modules["click"] = MagicMock()

# Import after mocking
from vpype_vfab.utils import (
    save_document_for_vfab,
    generate_job_name,
    validate_preset,
    format_job_status,
    format_job_list,
)
from vpype_vfab.exceptions import VfabJobError


class TestSaveDocumentForPlotty:
    """Test cases for save_document_for_vfab function."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_document(self):
        """Create mock vpype document."""
        doc = MagicMock()
        doc.layers = [MagicMock(), MagicMock()]
        return doc

    def test_save_document_success(self, temp_dir, mock_document):
        """Test successful document saving."""
        job_path = temp_dir / "test_job"

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("vpype.write_svg") as mock_write_svg:
                svg_path, job_json_path = save_document_for_vfab(
                    mock_document, job_path, "test_job"
                )

        # Check return paths
        assert svg_path == job_path / "vpype_vfab.svg"
        assert job_json_path == job_path / "job.json"

        # Check vpype.write_svg was called
        mock_write_svg.assert_called_once()

    def test_save_document_creates_directory(self, temp_dir, mock_document):
        """Test that job directory is created."""
        job_path = temp_dir / "new_job" / "subdir"

        with patch("builtins.open", mock_open()):
            with patch("vpype.write_svg"):
                save_document_for_vfab(mock_document, job_path, "test_job")

        # Check directory was created
        assert job_path.exists()
        assert job_path.is_dir()

    def test_save_document_job_json_content(self, temp_dir, mock_document):
        """Test job.json content is correct."""
        job_path = temp_dir / "test_job"

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("vpype.write_svg"):
                save_document_for_vfab(mock_document, job_path, "test_job")

        # Find the JSON write call
        json_write_call = None
        for call in mock_file().write.call_args_list:
            if len(call.args) > 0:
                content = call.args[0]
                try:
                    parsed = json.loads(content)
                    if "id" in parsed and parsed["id"] == "test_job":
                        json_write_call = parsed
                        break
                except json.JSONDecodeError:
                    pass

        assert json_write_call is not None
        assert json_write_call["id"] == "test_job"
        assert json_write_call["name"] == "test_job"
        assert json_write_call["paper"] == "A4"
        assert json_write_call["state"] == "NEW"
        assert "created_at" in json_write_call
        assert json_write_call["metadata"]["created_by"] == "vpype-vfab"
        assert json_write_call["metadata"]["source"] == "vpype document"

    def test_save_document_vpype_error(self, temp_dir, mock_document):
        """Test handling of vpype write error."""
        job_path = temp_dir / "test_job"

        with patch("vpype.write_svg", side_effect=Exception("SVG write failed")):
            with pytest.raises(VfabJobError, match="Failed to save document for vfab"):
                save_document_for_vfab(mock_document, job_path, "test_job")

    def test_save_document_file_error(self, temp_dir, mock_document):
        """Test handling of file system error."""
        job_path = temp_dir / "test_job"

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(VfabJobError, match="Failed to save document for vfab"):
                save_document_for_vfab(mock_document, job_path, "test_job")


class TestGenerateJobName:
    """Test cases for generate_job_name function."""

    @pytest.fixture
    def mock_document(self):
        """Create mock vpype document."""
        doc = MagicMock()
        return doc

    def test_generate_name_from_metadata_name(self, mock_document):
        """Test generating name from document metadata name."""
        mock_document.metadata = {"name": "my_design"}

        result = generate_job_name(mock_document)

        assert result == "my_design"

    def test_generate_name_from_metadata_title(self, mock_document):
        """Test generating name from document metadata title."""
        mock_document.metadata = {"title": "My Awesome Design"}

        result = generate_job_name(mock_document)

        assert result == "My Awesome Design"

    def test_generate_name_prefer_name_over_title(self, mock_document):
        """Test that name is preferred over title."""
        mock_document.metadata = {"name": "design", "title": "Design Title"}

        result = generate_job_name(mock_document)

        assert result == "design"

    def test_generate_name_with_fallback(self, mock_document):
        """Test generating name with fallback."""
        mock_document.metadata = {}

        result = generate_job_name(mock_document, fallback_name="fallback")

        assert result == "fallback"

    def test_generate_name_timestamp_fallback(self, mock_document):
        """Test generating timestamp-based name."""
        mock_document.metadata = {}
        mock_document.hasattr.return_value = False  # No metadata attribute

        with patch("vpype_vfab.utils.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"

            result = generate_job_name(mock_document)

            assert result == "vpype_job_20240101_120000"

    def test_generate_name_no_metadata_attribute(self, mock_document):
        """Test generating name when document has no metadata attribute."""
        mock_document.hasattr.return_value = False

        result = generate_job_name(mock_document, fallback_name="test")

        assert result == "test"

    def test_generate_name_empty_metadata(self, mock_document):
        """Test generating name with empty metadata."""
        mock_document.metadata = {}

        result = generate_job_name(mock_document, fallback_name="fallback")

        assert result == "fallback"


class TestValidatePreset:
    """Test cases for validate_preset function."""

    def test_validate_preset_fast(self):
        """Test validating fast preset."""
        result = validate_preset("fast")
        assert result == "fast"

    def test_validate_preset_default(self):
        """Test validating default preset."""
        result = validate_preset("default")
        assert result == "default"

    def test_validate_preset_hq(self):
        """Test validating hq preset."""
        result = validate_preset("hq")
        assert result == "hq"

    def test_validate_preset_invalid(self):
        """Test validating invalid preset."""
        with patch("vpype_vfab.utils.click") as mock_click:
            mock_bad_param = MagicMock()
            mock_click.BadParameter = mock_bad_param

            validate_preset("invalid")

            # Should raise BadParameter
            mock_bad_param.assert_called_once()

    def test_validate_preset_case_sensitive(self):
        """Test that preset validation is case sensitive."""
        with patch("vpype_vfab.utils.click") as mock_click:
            mock_bad_param = MagicMock()
            mock_click.BadParameter = mock_bad_param

            validate_preset("FAST")  # Uppercase should fail

            mock_bad_param.assert_called_once()


class TestFormatJobStatus:
    """Test cases for format_job_status function."""

    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing."""
        return {
            "name": "test_job",
            "state": "QUEUED",
            "paper": "A4",
            "created_at": "2024-01-01T12:00:00Z",
            "metadata": {"test": True},
        }

    def test_format_status_table(self, sample_job_data):
        """Test formatting status as table."""
        result = format_job_status(sample_job_data, "table")

        assert "test_job" in result
        assert "QUEUED" in result
        assert "A4" in result
        assert "2024-01-01T12:00:00Z" in result

    def test_format_status_json(self, sample_job_data):
        """Test formatting status as JSON."""
        result = format_job_status(sample_job_data, "json")

        parsed = json.loads(result)
        assert parsed["name"] == "test_job"
        assert parsed["state"] == "QUEUED"
        assert parsed["paper"] == "A4"

    def test_format_status_simple(self, sample_job_data):
        """Test formatting status as simple."""
        result = format_job_status(sample_job_data, "simple")

        assert result == "test_job: QUEUED"

    def test_format_status_table_missing_fields(self):
        """Test table format with missing fields."""
        job_data = {"name": "minimal_job"}

        result = format_job_status(job_data, "table")

        assert "minimal_job" in result
        assert "Unknown" in result  # Should show Unknown for missing fields

    def test_format_status_simple_missing_state(self):
        """Test simple format with missing state."""
        job_data = {"name": "test_job"}

        result = format_job_status(job_data, "simple")

        assert result == "test_job: Unknown"


class TestFormatJobList:
    """Test cases for format_job_list function."""

    @pytest.fixture
    def sample_jobs(self):
        """Sample job list for testing."""
        return [
            {
                "name": "job1",
                "state": "NEW",
                "paper": "A4",
                "created_at": "2024-01-01T12:00:00Z",
            },
            {
                "name": "job2",
                "state": "QUEUED",
                "paper": "A3",
                "created_at": "2024-01-01T13:00:00Z",
            },
        ]

    def test_format_list_table(self, sample_jobs):
        """Test formatting job list as table."""
        result = format_job_list(sample_jobs, "table")

        assert "job1" in result
        assert "job2" in result
        assert "NEW" in result
        assert "QUEUED" in result
        assert "A4" in result
        assert "A3" in result
        assert "2024-01-01T12:00:00" in result  # Truncated timezone
        assert "2024-01-01T13:00:00" in result

    def test_format_list_json(self, sample_jobs):
        """Test formatting job list as JSON."""
        result = format_job_list(sample_jobs, "json")

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "job1"
        assert parsed[1]["name"] == "job2"

    def test_format_list_csv(self, sample_jobs):
        """Test formatting job list as CSV."""
        result = format_job_list(sample_jobs, "csv")

        # Parse CSV to verify structure
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["name"] == "job1"
        assert rows[1]["name"] == "job2"
        assert "state" in rows[0]
        assert "paper" in rows[0]

    def test_format_list_empty(self):
        """Test formatting empty job list."""
        result = format_job_list([], "table")

        assert result == "No jobs found."

    def test_format_list_empty_json(self):
        """Test formatting empty job list as JSON."""
        result = format_job_list([], "json")

        parsed = json.loads(result)
        assert parsed == []

    def test_format_list_empty_csv(self):
        """Test formatting empty job list as CSV."""
        result = format_job_list([], "csv")

        # Should not raise error and return empty string
        assert result == ""

    def test_format_list_table_missing_fields(self):
        """Test table format with missing fields."""
        jobs = [{"name": "minimal_job"}]

        result = format_job_list(jobs, "table")

        assert "minimal_job" in result
        assert "Unknown" in result  # Should show Unknown for missing fields

    def test_format_list_csv_missing_fields(self):
        """Test CSV format with missing fields."""
        jobs = [{"name": "minimal_job"}]

        result = format_job_list(jobs, "csv")

        # Should still include header and available data
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["name"] == "minimal_job"

    def test_format_list_table_long_timestamp(self):
        """Test table format truncates long timestamps."""
        jobs = [
            {
                "name": "test_job",
                "created_at": "2024-01-01T12:00:00.123456+00:00",  # Long timestamp
            }
        ]

        result = format_job_list(jobs, "table")

        # Should truncate to avoid table formatting issues
        assert "2024-01-01T12:00:00." in result
        assert len(result.split()[-1]) <= 19  # Timestamp should be truncated
