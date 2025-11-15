"""Custom exceptions for vpype-plotty."""

import time
from typing import Optional, Any, Callable
from functools import wraps


class PlottyError(Exception):
    """Base exception for vpype-plotty."""

    def __init__(
        self,
        message: str,
        recovery_hint: Optional[str] = None,
        retry_after: Optional[float] = None,
    ):
        super().__init__(message)
        self.recovery_hint = recovery_hint
        self.retry_after = retry_after


class VfabNotFoundError(PlottyError):
    """vfab installation or workspace not found."""

    def __init__(self, message: str, workspace_path: Optional[str] = None):
        recovery_hint = (
            f"Check vfab installation at {workspace_path}"
            if workspace_path
            else "Verify vfab is properly installed"
        )
        super().__init__(message, recovery_hint)


class VfabConfigError(PlottyError):
    """vfab configuration error."""

    def __init__(self, message: str, config_file: Optional[str] = None):
        recovery_hint = (
            f"Check configuration file: {config_file}"
            if config_file
            else "Verify vfab configuration"
        )
        super().__init__(message, recovery_hint)


class VfabJobError(PlottyError):
    """Job creation or management error."""

    def __init__(self, message: str, job_id: Optional[str] = None):
        recovery_hint = (
            f"Check job status with: plotty-status {job_id}"
            if job_id
            else "Verify job parameters and vfab status"
        )
        super().__init__(message, recovery_hint)


class PlottyConnectionError(PlottyError):
    """Connection or communication error with vfab."""

    def __init__(self, message: str, retry_after: float = 5.0):
        super().__init__(message, "Check vfab is running and accessible", retry_after)


class PlottyTimeoutError(PlottyError):
    """Operation timeout error."""

    def __init__(self, message: str, timeout_seconds: float):
        super().__init__(
            message, "Increase timeout or check vfab performance", timeout_seconds
        )


class PlottyResourceError(PlottyError):
    """Resource exhaustion or allocation error."""

    def __init__(self, message: str, resource_type: str = "unknown"):
        super().__init__(
            message, f"Free up {resource_type} resources or wait for availability"
        )


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (PlottyConnectionError, PlottyTimeoutError),
):
    """Decorator for retrying operations on transient failures."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    delay = base_delay * (backoff_factor**attempt)
                    if hasattr(e, "retry_after") and e.retry_after:
                        delay = max(delay, e.retry_after)

                    print(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                except Exception:
                    # Don't retry on non-transient exceptions
                    raise

            if last_exception:
                raise last_exception
            else:
                raise PlottyError("All retry attempts failed")

        return wrapper

    return decorator


def handle_plotty_errors(func: Callable) -> Callable:
    """Decorator for consistent error handling across plotty operations."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except PlottyError:
            # Re-raise plotty errors as-is
            raise
        except FileNotFoundError as e:
            raise VfabNotFoundError(
                f"Required file or directory not found: {e}",
                str(e.filename) if hasattr(e, "filename") else None,
            )
        except PermissionError as e:
            raise VfabConfigError(
                f"Permission denied accessing vfab resources: {e}",
                str(e.filename) if hasattr(e, "filename") else None,
            )
        except ConnectionError as e:
            raise PlottyConnectionError(f"Failed to connect to vfab: {e}")
        except TimeoutError as e:
            raise PlottyTimeoutError(f"Operation timed out: {e}", 30.0)
        except Exception as e:
            raise PlottyError(f"Unexpected error in vfab operation: {e}")

    return wrapper
