"""Test enhanced exceptions functionality."""

import time
import pytest

from src.exceptions import (
    PlottyError,
    PlottyNotFoundError,
    PlottyConfigError,
    PlottyJobError,
    PlottyConnectionError,
    PlottyTimeoutError,
    PlottyResourceError,
    retry_on_failure,
    handle_plotty_errors,
)


class TestPlottyError:
    """Test base PlottyError class."""

    def test_basic_error(self):
        error = PlottyError("Test message")
        assert str(error) == "Test message"
        assert error.recovery_hint is None
        assert error.retry_after is None

    def test_error_with_recovery_hint(self):
        error = PlottyError("Test message", recovery_hint="Try again")
        assert str(error) == "Test message"
        assert error.recovery_hint == "Try again"

    def test_error_with_retry_after(self):
        error = PlottyError("Test message", retry_after=5.0)
        assert str(error) == "Test message"
        assert error.retry_after == 5.0


class TestSpecificExceptions:
    """Test specific exception classes."""

    def test_plotty_not_found_error(self):
        error = PlottyNotFoundError("ploTTY not found", "/path/to/plotty")
        assert "ploTTY not found" in str(error)
        assert "/path/to/plotty" in error.recovery_hint

    def test_plotty_not_found_error_no_path(self):
        error = PlottyNotFoundError("ploTTY not found")
        assert "Verify ploTTY is properly installed" in error.recovery_hint

    def test_plotty_config_error(self):
        error = PlottyConfigError("Invalid config", "/path/to/config")
        assert "Invalid config" in str(error)
        assert "/path/to/config" in error.recovery_hint

    def test_plotty_job_error(self):
        error = PlottyJobError("Job failed", "job123")
        assert "Job failed" in str(error)
        assert "job123" in error.recovery_hint

    def test_plotty_connection_error(self):
        error = PlottyConnectionError("Connection failed")
        assert "Connection failed" in str(error)
        assert error.retry_after == 5.0

    def test_plotty_timeout_error(self):
        error = PlottyTimeoutError("Operation timed out", 30.0)
        assert "Operation timed out" in str(error)
        assert error.retry_after == 30.0

    def test_plotty_resource_error(self):
        error = PlottyResourceError("Out of memory", "memory")
        assert "Out of memory" in str(error)
        assert "memory" in error.recovery_hint


class TestRetryDecorator:
    """Test retry_on_failure decorator."""

    def test_successful_operation_no_retry(self):
        @retry_on_failure(max_retries=3)
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_retry_on_connection_error(self):
        call_count = 0

        @retry_on_failure(max_retries=2, base_delay=0.1)
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise PlottyConnectionError("Connection failed")
            return "success"

        result = failing_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_exhausted(self):
        @retry_on_failure(max_retries=2, base_delay=0.1)
        def always_failing_func():
            raise PlottyConnectionError("Connection failed")

        with pytest.raises(PlottyConnectionError):
            always_failing_func()

    def test_retry_with_custom_retry_after(self):
        call_count = 0

        @retry_on_failure(max_retries=2, base_delay=0.1)
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error = PlottyConnectionError("Connection failed")
                error.retry_after = 0.2  # Custom retry time
                raise error
            return "success"

        start_time = time.time()
        result = failing_func()
        elapsed_time = time.time() - start_time

        assert result == "success"
        assert call_count == 2
        assert elapsed_time >= 0.2  # Should respect custom retry time

    def test_no_retry_on_non_transient_exception(self):
        @retry_on_failure(max_retries=3)
        def raising_config_error():
            raise PlottyConfigError("Bad config")

        with pytest.raises(PlottyConfigError):
            raising_config_error()


class TestErrorHandlingDecorator:
    """Test handle_plotty_errors decorator."""

    def test_handles_plotty_error_passthrough(self):
        @handle_plotty_errors
        def raising_plotty_error():
            raise PlottyError("Plotty error")

        with pytest.raises(PlottyError) as exc_info:
            raising_plotty_error()
        assert str(exc_info.value) == "Plotty error"

    def test_converts_file_not_found(self):
        @handle_plotty_errors
        def file_not_found():
            raise FileNotFoundError("No such file")

        with pytest.raises(PlottyNotFoundError) as exc_info:
            file_not_found()
        assert "Required file or directory not found" in str(exc_info.value)

    def test_converts_permission_error(self):
        @handle_plotty_errors
        def permission_error():
            raise PermissionError("Access denied")

        with pytest.raises(PlottyConfigError) as exc_info:
            permission_error()
        assert "Permission denied" in str(exc_info.value)

    def test_converts_connection_error(self):
        @handle_plotty_errors
        def connection_error():
            raise ConnectionError("Cannot connect")

        with pytest.raises(PlottyConnectionError) as exc_info:
            connection_error()
        assert "Failed to connect to ploTTY" in str(exc_info.value)

    def test_converts_timeout_error(self):
        @handle_plotty_errors
        def timeout_error():
            raise TimeoutError("Operation timed out")

        with pytest.raises(PlottyTimeoutError) as exc_info:
            timeout_error()
        assert "Operation timed out" in str(exc_info.value)
        assert exc_info.value.retry_after == 30.0

    def test_converts_generic_exception(self):
        @handle_plotty_errors
        def generic_error():
            raise ValueError("Generic error")

        with pytest.raises(PlottyError) as exc_info:
            generic_error()
        assert "Unexpected error in ploTTY operation" in str(exc_info.value)

    def test_successful_operation_passthrough(self):
        @handle_plotty_errors
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"


class TestIntegration:
    """Test integration of decorators."""

    def test_retry_and_error_handling_combined(self):
        call_count = 0

        @retry_on_failure(max_retries=2, base_delay=0.1)
        @handle_plotty_errors
        def connection_then_file_error():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            raise FileNotFoundError("File not found")

        with pytest.raises(PlottyNotFoundError):
            connection_then_file_error()
        assert call_count == 2
