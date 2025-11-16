"""Enhanced vfab configuration tests with Qt mocking setup."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

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
from vpype_vfab.config import PlottyConfig
from vpype_vfab.exceptions import VfabConfigError, VfabNotFoundError


class TestPlottyConfigEnhanced:
    """Enhanced vfab configuration management tests."""

    def test_init_with_explicit_path(self):
        """Test initialization with explicit workspace path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            assert config.workspace_path == Path(temp_dir)
            assert config.config_path == Path(temp_dir) / "config.yaml"
            assert config.vpype_presets_path == Path(temp_dir) / "vpype-presets.yaml"

    def test_init_without_path(self):
        """Test initialization without explicit path."""
        with patch("platformdirs.user_data_dir") as mock_user_data_dir:
            mock_user_data_dir.return_value = "/fake/xdg/data"

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False  # All candidates don't exist

                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    config = PlottyConfig()
                    # Should create default workspace
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_find_workspace_explicit_path(self):
        """Test workspace finding with explicit valid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            workspace = config._find_workspace(temp_dir)
            assert workspace == Path(temp_dir)

    def test_find_workspace_current_dir_candidate(self):
        """Test workspace finding in current directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_dir = Path(temp_dir) / "vfab-workspace"
            workspace_dir.mkdir()

            with patch("pathlib.Path.cwd") as mock_cwd:
                mock_cwd.return_value = Path(temp_dir)

                config = PlottyConfig()
                workspace = config._find_workspace(None)
                assert workspace == workspace_dir

    def test_find_workspace_home_candidate(self):
        """Test workspace finding in home directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_dir = Path(temp_dir) / "vfab-workspace"
            workspace_dir.mkdir()

            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                config = PlottyConfig()
                workspace = config._find_workspace(None)
                assert workspace == workspace_dir

    def test_find_workspace_user_data_dir_candidate(self):
        """Test workspace finding in user data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("platformdirs.user_data_dir") as mock_user_data_dir:
                mock_user_data_dir.return_value = temp_dir

                with patch("pathlib.Path.exists") as mock_exists:

                    def exists_side_effect(self):
                        return str(self) == temp_dir

                    mock_exists.side_effect = exists_side_effect

                    config = PlottyConfig()
                    workspace = config._find_workspace(None)
                    assert workspace == Path(temp_dir)

    def test_find_workspace_creates_default(self):
        """Test workspace creation when no candidates exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_home = Path(temp_dir) / "fake_home"
            fake_home.mkdir()

            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = fake_home

                with patch("pathlib.Path.exists") as mock_exists:

                    def exists_side_effect(self):
                        # Return False for all candidates except the created workspace
                        return str(self).endswith("vfab-workspace")

                    mock_exists.side_effect = exists_side_effect

                    config = PlottyConfig()
                    expected_workspace = fake_home / "vfab-workspace"
                    assert config.workspace_path == expected_workspace
                    assert expected_workspace.exists()

    def test_find_workspace_creation_failure(self):
        """Test workspace creation failure handling."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/fake/home")

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False

                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    mock_mkdir.side_effect = OSError("Permission denied")

                    with pytest.raises(VfabNotFoundError) as exc_info:
                        PlottyConfig()

                    assert "vfab workspace not found" in str(exc_info.value)
                    assert "Permission denied" in str(exc_info.value)

    def test_load_config_default(self):
        """Test loading default configuration when no file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            default_config = config.load_config()

            assert "workspace" in default_config
            assert "vpype" in default_config
            assert "paper" in default_config
            assert default_config["vpype"]["preset"] == "fast"
            assert default_config["vpype"]["presets_file"] == str(
                config.vpype_presets_path
            )
            assert default_config["paper"]["default_size"] == "A4"
            assert default_config["paper"]["default_margin_mm"] == 10.0

    def test_load_config_from_file(self):
        """Test loading configuration from existing file."""
        test_config = {
            "vpype": {"preset": "hq", "custom_setting": "value"},
            "paper": {"default_size": "A3", "default_margin_mm": 15.0},
            "custom_section": {"custom_key": "custom_value"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(test_config, f)

            config = PlottyConfig(temp_dir)
            loaded_config = config.load_config()

            assert loaded_config["vpype"]["preset"] == "hq"
            assert loaded_config["vpype"]["custom_setting"] == "value"
            assert loaded_config["paper"]["default_size"] == "A3"
            assert loaded_config["paper"]["default_margin_mm"] == 15.0
            assert loaded_config["custom_section"]["custom_key"] == "custom_value"

    def test_load_config_empty_file(self):
        """Test loading configuration from empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.touch()  # Create empty file

            config = PlottyConfig(temp_dir)
            loaded_config = config.load_config()

            # When file exists but is empty, yaml.safe_load returns None
            # The code does: yaml.safe_load(f) or {} which returns {} for empty files
            assert loaded_config == {}  # Empty dict, not default config

    def test_load_config_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content:")

            config = PlottyConfig(temp_dir)
            with pytest.raises(VfabConfigError) as exc_info:
                config.load_config()

            assert "Failed to load vfab config" in str(exc_info.value)

    def test_load_config_file_read_error(self):
        """Test loading configuration with file read error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text("valid: yaml")

            config = PlottyConfig(temp_dir)

            with patch("builtins.open", side_effect=OSError("Permission denied")):
                with pytest.raises(VfabConfigError) as exc_info:
                    config.load_config()

                assert "Failed to load vfab config" in str(exc_info.value)

    def test_save_config_basic(self):
        """Test basic configuration saving."""
        test_config = {
            "vpype": {"preset": "default"},
            "paper": {"default_size": "A4"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            # Verify file was created
            assert config.config_path.exists()

            # Verify content
            with open(config.config_path) as f:
                saved_config = yaml.safe_load(f)

            assert saved_config["vpype"]["preset"] == "default"
            assert saved_config["paper"]["default_size"] == "A4"

    def test_save_config_creates_directory(self):
        """Test that save_config creates parent directories."""
        test_config = {"vpype": {"preset": "hq"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            # Remove config directory to test creation
            config.config_path.parent.rmdir()

            config.save_config(test_config)
            assert config.config_path.exists()

    def test_save_config_yaml_error(self):
        """Test saving configuration with YAML error."""
        test_config = {"vpype": {"preset": "default"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)

            with patch("yaml.dump", side_effect=yaml.YAMLError("YAML error")):
                with pytest.raises(VfabConfigError) as exc_info:
                    config.save_config(test_config)

                assert "Failed to save vfab config" in str(exc_info.value)

    def test_save_config_file_error(self):
        """Test saving configuration with file error."""
        test_config = {"vpype": {"preset": "default"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)

            with patch("builtins.open", side_effect=OSError("Disk full")):
                with pytest.raises(VfabConfigError) as exc_info:
                    config.save_config(test_config)

                assert "Failed to save vfab config" in str(exc_info.value)

    def test_default_config_structure(self):
        """Test default configuration structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            default_config = config._default_config()

            # Check required sections
            assert "workspace" in default_config
            assert "vpype" in default_config
            assert "paper" in default_config

            # Check vpype section
            assert "preset" in default_config["vpype"]
            assert "presets_file" in default_config["vpype"]
            assert default_config["vpype"]["preset"] == "fast"
            assert default_config["vpype"]["presets_file"] == str(
                config.vpype_presets_path
            )

            # Check paper section
            assert "default_size" in default_config["paper"]
            assert "default_margin_mm" in default_config["paper"]
            assert default_config["paper"]["default_size"] == "A4"
            assert default_config["paper"]["default_margin_mm"] == 10.0

    def test_get_vpype_preset_default(self):
        """Test getting vpype preset from default config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            preset = config.get_vpype_preset()
            assert preset == "fast"

    def test_get_vpype_preset_from_config(self):
        """Test getting vpype preset from saved config."""
        test_config = {"vpype": {"preset": "hq"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            preset = config.get_vpype_preset()
            assert preset == "hq"

    def test_get_vpype_preset_missing_section(self):
        """Test getting vpype preset when vpype section is missing."""
        test_config = {"paper": {"default_size": "A3"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            preset = config.get_vpype_preset()
            assert preset == "fast"  # Should return default

    def test_get_vpype_preset_missing_preset(self):
        """Test getting vpype preset when preset key is missing."""
        test_config = {"vpype": {"other_setting": "value"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            preset = config.get_vpype_preset()
            assert preset == "fast"  # Should return default

    def test_get_default_paper_size_default(self):
        """Test getting default paper size from default config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            paper_size = config.get_default_paper_size()
            assert paper_size == "A4"

    def test_get_default_paper_size_from_config(self):
        """Test getting default paper size from saved config."""
        test_config = {"paper": {"default_size": "A3"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            paper_size = config.get_default_paper_size()
            assert paper_size == "A3"

    def test_get_default_paper_size_missing_section(self):
        """Test getting default paper size when paper section is missing."""
        test_config = {"vpype": {"preset": "hq"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            paper_size = config.get_default_paper_size()
            assert paper_size == "A4"  # Should return default

    def test_get_default_paper_size_missing_size(self):
        """Test getting default paper size when size key is missing."""
        test_config = {"paper": {"default_margin_mm": 15.0}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)
            config.save_config(test_config)

            paper_size = config.get_default_paper_size()
            assert paper_size == "A4"  # Should return default

    def test_workspace_path_priority(self):
        """Test that workspace path candidates are checked in priority order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple candidate directories
            explicit_dir = Path(temp_dir) / "explicit"
            explicit_dir.mkdir()

            current_dir = Path(temp_dir) / "vfab-workspace"
            current_dir.mkdir()

            home_dir = Path(temp_dir) / "home_vfab-workspace"
            home_dir.mkdir()

            with patch("pathlib.Path.cwd") as mock_cwd:
                mock_cwd.return_value = Path(temp_dir)

                with patch("pathlib.Path.home") as mock_home:
                    mock_home.return_value = Path(temp_dir)

                    # Explicit path should take priority
                    config = PlottyConfig(str(explicit_dir))
                    assert config.workspace_path == explicit_dir

    def test_config_and_presets_paths(self):
        """Test that config and vpype-presets paths are correctly set."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PlottyConfig(temp_dir)

            assert config.config_path == config.workspace_path / "config.yaml"
            assert (
                config.vpype_presets_path
                == config.workspace_path / "vpype-presets.yaml"
            )
