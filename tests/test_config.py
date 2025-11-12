"""Test ploTTY configuration detection."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from vpype_plotty.config import PlottyConfig
from vpype_plotty.exceptions import PlottyConfigError


class TestPlottyConfig:
    """Test ploTTY configuration management."""

    def test_find_workspace_with_explicit_path(self):
        """Test workspace detection with explicit path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            assert config.workspace_path == Path(temp_dir)

    def test_find_workspace_creates_default(self):
        """Test workspace creation when none exists."""
        with patch("platformdirs.user_data_dir") as mock_user_data_dir:
            mock_user_data_dir.return_value = "/fake/xdg/data"

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False  # All candidates don't exist

                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    PlottyConfig()
                    # Should be called when creating default workspace
                    assert mock_mkdir.call_count >= 1

    def test_load_config_default(self):
        """Test loading default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            default_config = config.load_config()

            assert "workspace" in default_config
            assert "vpype" in default_config
            assert "paper" in default_config
            assert default_config["vpype"]["preset"] == "fast"

    def test_load_config_from_file(self):
        """Test loading configuration from file."""
        test_config = {
            "vpype": {"preset": "hq"},
            "paper": {"default_size": "A3"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(test_config, f)

            config = PlottyConfig(temp_dir)
            loaded_config = config.load_config()

            assert loaded_config["vpype"]["preset"] == "hq"
            assert loaded_config["paper"]["default_size"] == "A3"

    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content:")

            config = PlottyConfig(temp_dir)
            with pytest.raises(PlottyConfigError):
                config.load_config()

    def test_save_config(self):
        """Test saving configuration."""
        test_config = {
            "vpype": {"preset": "default"},
            "paper": {"default_size": "A4"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            # Verify file was created and contains correct data
            assert config.config_path.exists()
            with open(config.config_path) as f:
                saved_config = yaml.safe_load(f)

            assert saved_config["vpype"]["preset"] == "default"

    def test_get_vpype_preset(self):
        """Test getting vpype preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            assert config.get_vpype_preset() == "fast"

    def test_get_default_paper_size(self):
        """Test getting default paper size."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            assert config.get_default_paper_size() == "A4"
