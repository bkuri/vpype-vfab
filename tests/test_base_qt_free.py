"""Qt-free tests for vpype_plotty.base module with mocked dependencies."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import click
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock the database module before importing base
sys.modules["vpype_plotty.database"] = Mock()

# Now import the base module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "base", "/home/bk/source/vpype-plotty/vpype_plotty/base.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class TestBaseQtFree:
    """Qt-free test suite for base module."""

    def test_get_pen_mapping_single_layer(self):
        """Test pen mapping for single layer document."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = [0]  # Single layer

        result = command.get_pen_mapping(document)

        assert result is None

    def test_get_pen_mapping_auto_preset(self):
        """Test pen mapping with auto preset."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = [0, 1, 2, 3, 4, 5]  # Multiple layers

        result = command.get_pen_mapping(document, "auto")

        expected = {0: 1, 1: 2, 2: 3, 3: 4, 4: 1, 5: 2}
        assert result == expected

    def test_get_pen_mapping_sequential_preset(self):
        """Test pen mapping with sequential preset."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = [0, 1, 2, 3]  # Multiple layers

        result = command.get_pen_mapping(document, "sequential")

        expected = {0: 1, 1: 2, 2: 3, 3: 4}
        assert result == expected

    def test_get_pen_mapping_default_preset(self):
        """Test pen mapping with unknown preset (defaults to auto)."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = [0, 1, 2, 3, 4]  # Multiple layers

        result = command.get_pen_mapping(document, "unknown")

        expected = {0: 1, 1: 2, 2: 3, 3: 4, 4: 1}
        assert result == expected

    def test_get_pen_mapping_default_parameter(self):
        """Test pen mapping with default parameter (auto)."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = [0, 1, 2]  # Multiple layers

        result = command.get_pen_mapping(document)  # No preset specified

        expected = {0: 1, 1: 2, 2: 3}
        assert result == expected

    def test_get_pen_mapping_empty_layers(self):
        """Test pen mapping with empty layers list."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = []  # No layers

        result = command.get_pen_mapping(document)

        assert result is None

    def test_get_pen_mapping_many_layers_auto(self):
        """Test pen mapping with many layers using auto preset."""
        command = base.StreamlinedPlottyCommand()
        document = Mock()
        document.layers = list(range(10))  # 10 layers

        result = command.get_pen_mapping(document, "auto")

        # Should cycle through pens 1-4
        expected = {i: (i % 4) + 1 for i in range(10)}
        assert result == expected
