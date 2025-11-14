"""Qt mocking utility for headless testing environment."""

import os
import sys
from unittest.mock import MagicMock
from typing import Callable


def setup_qt_mocks() -> None:
    """Set up Qt module mocks for headless testing.

    This function must be called before any vpype imports to prevent
    Qt/display-related segmentation faults during testing.
    """
    # Set up headless environment variables
    os.environ["DISPLAY"] = ""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["PYQT_QPA_PLATFORM"] = "offscreen"

    # Mock Qt modules before they're imported
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


def create_mocked_qt_test(test_function: Callable) -> Callable:
    """Decorator to wrap test functions with Qt mocking.

    Args:
        test_function: The test function to wrap

    Returns:
        Wrapped test function with Qt mocks set up
    """

    def wrapper(*args, **kwargs):
        setup_qt_mocks()
        return test_function(*args, **kwargs)

    return wrapper


class MockedQtTestContext:
    """Context manager for Qt mocking in tests."""

    def __enter__(self):
        setup_qt_mocks()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up if needed
        pass
