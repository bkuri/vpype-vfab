"""Qt-free tests for vpype_vfab.exceptions module."""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import the exceptions module
from vpype_vfab import exceptions


class TestExceptionsQtFree:
    """Qt-free test suite for exceptions module."""

    def test_vfab_error_init(self):
        """Test PlottyError base exception initialization."""
        message = "Test error message"
        error = exceptions.PlottyError(message)

        assert str(error) == message
        assert error.recovery_hint is None
        assert error.retry_after is None

    def test_vfab_error_with_recovery_hint(self):
        """Test PlottyError with recovery hint."""
        message = "Error with hint"
        recovery_hint = "Try again later"
        error = exceptions.PlottyError(message, recovery_hint)

        assert str(error) == message
        assert error.recovery_hint == recovery_hint

    def test_vfab_error_with_retry_after(self):
        """Test PlottyError with retry_after."""
        message = "Error with retry"
        retry_after = 5.0
        error = exceptions.PlottyError(message, None, retry_after)

        assert str(error) == message
        assert error.retry_after == retry_after

    def test_vfab_not_found_error_init(self):
        """Test VfabNotFoundError initialization."""
        message = "vfab not found"
        error = exceptions.VfabNotFoundError(message)

        assert str(error) == message
        assert "Verify vfab is properly installed" in error.recovery_hint

    def test_vfab_not_found_error_with_workspace(self):
        """Test VfabNotFoundError with workspace path."""
        message = "Workspace not found"
        workspace_path = "/path/to/workspace"
        error = exceptions.VfabNotFoundError(message, workspace_path)

        assert str(error) == message
        assert workspace_path in error.recovery_hint

    def test_vfab_not_found_error_inheritance(self):
        """Test VfabNotFoundError inheritance."""
        error = exceptions.VfabNotFoundError("test")

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_vfab_connection_error_init(self):
        """Test PlottyConnectionError initialization."""
        message = "Connection failed"
        error = exceptions.PlottyConnectionError(message)

        assert str(error) == message
        assert error.retry_after == 5.0
        assert "Check vfab is running" in error.recovery_hint

    def test_vfab_connection_error_inheritance(self):
        """Test PlottyConnectionError inheritance."""
        error = exceptions.PlottyConnectionError("test")

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_vfab_job_error_init(self):
        """Test VfabJobError initialization."""
        message = "Job failed"
        error = exceptions.VfabJobError(message)

        assert str(error) == message
        assert "Verify job parameters" in error.recovery_hint

    def test_vfab_job_error_with_job_id(self):
        """Test VfabJobError with job ID."""
        message = "Job failed"
        job_id = "job123"
        error = exceptions.VfabJobError(message, job_id)

        assert str(error) == message
        assert job_id in error.recovery_hint

    def test_vfab_job_error_inheritance(self):
        """Test VfabJobError inheritance."""
        error = exceptions.VfabJobError("test")

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_vfab_config_error_init(self):
        """Test VfabConfigError initialization."""
        message = "Config error"
        error = exceptions.VfabConfigError(message)

        assert str(error) == message
        assert "Verify vfab configuration" in error.recovery_hint

    def test_vfab_config_error_with_config_file(self):
        """Test VfabConfigError with config file."""
        message = "Config error"
        config_file = "/path/to/config"
        error = exceptions.VfabConfigError(message, config_file)

        assert str(error) == message
        assert config_file in error.recovery_hint

    def test_vfab_config_error_inheritance(self):
        """Test VfabConfigError inheritance."""
        error = exceptions.VfabConfigError("test")

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_vfab_timeout_error_init(self):
        """Test PlottyTimeoutError initialization."""
        message = "Operation timed out"
        timeout_seconds = 30.0
        error = exceptions.PlottyTimeoutError(message, timeout_seconds)

        assert str(error) == message
        assert error.retry_after == timeout_seconds
        assert "Increase timeout" in error.recovery_hint

    def test_vfab_timeout_error_inheritance(self):
        """Test PlottyTimeoutError inheritance."""
        error = exceptions.PlottyTimeoutError("test", 30.0)

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_vfab_resource_error_init(self):
        """Test PlottyResourceError initialization."""
        message = "Out of memory"
        error = exceptions.PlottyResourceError(message)

        assert str(error) == message
        assert "unknown resources" in error.recovery_hint

    def test_vfab_resource_error_with_type(self):
        """Test PlottyResourceError with resource type."""
        message = "Out of memory"
        resource_type = "memory"
        error = exceptions.PlottyResourceError(message, resource_type)

        assert str(error) == message
        assert resource_type in error.recovery_hint

    def test_vfab_resource_error_inheritance(self):
        """Test PlottyResourceError inheritance."""
        error = exceptions.PlottyResourceError("test")

        assert isinstance(error, exceptions.PlottyError)
        assert isinstance(error, Exception)

    def test_exception_hierarchy_consistency(self):
        """Test that all custom exceptions inherit from PlottyError."""
        exception_classes = [
            exceptions.VfabNotFoundError,
            exceptions.PlottyConnectionError,
            exceptions.VfabJobError,
            exceptions.VfabConfigError,
            exceptions.PlottyTimeoutError,
            exceptions.PlottyResourceError,
        ]

        for exc_class in exception_classes:
            # Test that each exception class inherits from PlottyError
            assert issubclass(exc_class, exceptions.PlottyError)
            assert issubclass(exc_class, Exception)

            # Test instantiation
            if exc_class == exceptions.VfabNotFoundError:
                instance = exc_class("test", "/path")
            elif exc_class == exceptions.VfabJobError:
                instance = exc_class("test", "job123")
            elif exc_class == exceptions.VfabConfigError:
                instance = exc_class("test", "/config")
            elif exc_class == exceptions.PlottyTimeoutError:
                instance = exc_class("test", 30.0)
            elif exc_class == exceptions.PlottyResourceError:
                instance = exc_class("test", "memory")
            else:
                instance = exc_class("test")

            assert isinstance(instance, exceptions.PlottyError)

    def test_retry_on_failure_decorator(self):
        """Test retry_on_failure decorator."""

        # Test successful function
        @exceptions.retry_on_failure(max_retries=2)
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_retry_on_failure_with_exception(self):
        """Test retry_on_failure with transient exception."""
        call_count = 0

        @exceptions.retry_on_failure(max_retries=2, base_delay=0.1)
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise exceptions.PlottyConnectionError("Connection failed")
            return "success"

        result = failing_func()
        assert result == "success"
        assert call_count == 2

    def test_retry_on_failure_max_retries_exceeded(self):
        """Test retry_on_failure when max retries exceeded."""

        @exceptions.retry_on_failure(max_retries=1, base_delay=0.1)
        def always_failing_func():
            raise exceptions.PlottyConnectionError("Always fails")

        with pytest.raises(exceptions.PlottyConnectionError):
            always_failing_func()

    def test_retry_on_failure_non_transient_exception(self):
        """Test retry_on_failure with non-transient exception."""

        @exceptions.retry_on_failure(max_retries=2)
        def non_transient_func():
            raise ValueError("Non-transient error")

        with pytest.raises(ValueError):
            non_transient_func()

    def test_handle_plotty_errors_decorator(self):
        """Test handle_plotty_errors decorator."""

        @exceptions.handle_plotty_errors
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_handle_plotty_errors_file_not_found(self):
        """Test handle_plotty_errors with FileNotFoundError."""

        @exceptions.handle_plotty_errors
        def file_func():
            raise FileNotFoundError("No such file", "test.txt")

        with pytest.raises(exceptions.VfabNotFoundError) as exc_info:
            file_func()

        assert "test.txt" in str(exc_info.value)

    def test_handle_plotty_errors_permission_error(self):
        """Test handle_plotty_errors with PermissionError."""

        @exceptions.handle_plotty_errors
        def permission_func():
            raise PermissionError("Access denied", "config.yaml")

        with pytest.raises(exceptions.VfabConfigError) as exc_info:
            permission_func()

        assert "config.yaml" in str(exc_info.value)

    def test_handle_plotty_errors_connection_error(self):
        """Test handle_plotty_errors with ConnectionError."""

        @exceptions.handle_plotty_errors
        def connection_func():
            raise ConnectionError("Connection refused")

        with pytest.raises(exceptions.PlottyConnectionError) as exc_info:
            connection_func()

        assert "Connection refused" in str(exc_info.value)

    def test_handle_plotty_errors_timeout_error(self):
        """Test handle_plotty_errors with TimeoutError."""

        @exceptions.handle_plotty_errors
        def timeout_func():
            raise TimeoutError("Operation timed out")

        with pytest.raises(exceptions.PlottyTimeoutError) as exc_info:
            timeout_func()

        assert "Operation timed out" in str(exc_info.value)
        assert exc_info.value.retry_after == 30.0

    def test_handle_plotty_errors_generic_exception(self):
        """Test handle_plotty_errors with generic Exception."""

        @exceptions.handle_plotty_errors
        def generic_func():
            raise RuntimeError("Unexpected error")

        with pytest.raises(exceptions.PlottyError) as exc_info:
            generic_func()

        assert "Unexpected error" in str(exc_info.value)

    def test_handle_plotty_errors_preserves_plotty_errors(self):
        """Test handle_plotty_errors preserves PlottyError instances."""

        @exceptions.handle_plotty_errors
        def plotty_error_func():
            raise exceptions.VfabJobError("Job failed", "job123")

        with pytest.raises(exceptions.VfabJobError) as exc_info:
            plotty_error_func()

        assert str(exc_info.value) == "Job failed"
