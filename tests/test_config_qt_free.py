"""Qt-free tests for vpype_plotty.config module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import yaml
from pathlib import Path
import sys
import os
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock external dependencies to avoid Qt issues
mock_platformdirs = Mock()
mock_user_data_dir = Mock(return_value="/mock/user/data/plotty")
mock_platformdirs.user_data_dir = mock_user_data_dir
sys.modules["platformdirs"] = mock_platformdirs

# Mock exceptions module
mock_exceptions = Mock()
mock_plotty_config_error = Exception
mock_plotty_not_found_error = Exception
mock_exceptions.PlottyConfigError = mock_plotty_config_error
mock_exceptions.PlottyNotFoundError = mock_plotty_not_found_error
sys.modules["vpype_plotty.exceptions"] = mock_exceptions

# Now import the config module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "config", "/home/bk/source/vpype-plotty/vpype_plotty/config.py"
)
if spec is None:
    raise ImportError("Could not load config module")
config = importlib.util.module_from_spec(spec)
sys.modules["config"] = config  # Register in sys.modules for patching
spec.loader.exec_module(config)


class TestConfigQtFree:
    """Qt-free test suite for config module."""

    def test_init_with_workspace_path(self):
        """Test PlottyConfig initialization with explicit workspace path."""
        with patch("config.Path") as mock_path_class:
            # Create a proper mock that supports the / operator
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_path_instance.__truediv__ = MagicMock(return_value=MagicMock())
            mock_path_class.return_value = mock_path_instance

            pc = config.PlottyConfig("/test/workspace")

            assert pc.workspace_path == mock_path_instance
            assert pc.config_path == mock_path_instance / "config.yaml"
            assert pc.vpype_presets_path == mock_path_instance / "vpype-presets.yaml"

    def test_init_without_workspace_path(self):
        """Test PlottyConfig initialization without explicit workspace."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock workspace finding
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_path_instance.__truediv__ = MagicMock(return_value=MagicMock())
            mock_path_instance.__truediv__.return_value.name = "config.yaml"
            mock_path_class.return_value = mock_path_instance
            mock_path_class.cwd.return_value = Path("/current/dir")

            pc = config.PlottyConfig()

            assert pc.workspace_path is not None
            assert pc.config_path.name == "config.yaml"
            assert pc.vpype_presets_path.name == "vpype-presets.yaml"

    def test_find_workspace_explicit_path(self):
        """Test workspace finding with explicit path."""
        with patch("config.Path") as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_path_class.return_value = mock_path_instance

            pc = config.PlottyConfig("/explicit/path")

            assert pc.workspace_path == mock_path_instance

    def test_find_workspace_current_directory(self):
        """Test workspace finding in current directory."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock explicit path fails
            mock_path_class.side_effect = [
                MagicMock(exists=False, is_dir=False),  # explicit path
                MagicMock(exists=True, is_dir=True),  # current/plotty-workspace
                MagicMock(),  # home/plotty-workspace
                MagicMock(),  # user_data_dir
            ]
            mock_path_class.cwd.return_value = Path("/current")

            pc = config.PlottyConfig()

            # Should find current directory workspace
            assert pc.workspace_path is not None

    def test_find_workspace_home_directory(self):
        """Test workspace finding in home directory."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock explicit and current directory fail
            mock_path_class.side_effect = [
                MagicMock(exists=False, is_dir=False),  # explicit path
                MagicMock(exists=False, is_dir=False),  # current/plotty-workspace
                MagicMock(exists=True, is_dir=True),  # home/plotty-workspace
                MagicMock(),  # user_data_dir
            ]
            mock_path_class.home.return_value = Path("/home/user")

            pc = config.PlottyConfig()

            # Should find home directory workspace
            assert pc.workspace_path is not None

    def test_find_workspace_user_data_dir(self):
        """Test workspace finding in user data directory."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock all but user data dir fail
            mock_path_class.side_effect = [
                MagicMock(exists=False, is_dir=False),  # explicit path
                MagicMock(exists=False, is_dir=False),  # current/plotty-workspace
                MagicMock(exists=False, is_dir=False),  # home/plotty-workspace
                MagicMock(exists=True, is_dir=True),  # user_data_dir
            ]
            mock_user_data_dir.return_value = "/user/data/plotty"

            pc = config.PlottyConfig()

            # Should find user data directory workspace
            assert pc.workspace_path is not None

    def test_find_workspace_create_default(self):
        """Test workspace creation when none found."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock all candidates fail
            mock_path_class.side_effect = [
                MagicMock(exists=False, is_dir=False),  # explicit path
                MagicMock(exists=False, is_dir=False),  # current/plotty-workspace
                MagicMock(exists=False, is_dir=False),  # home/plotty-workspace
                MagicMock(exists=False, is_dir=False),  # user_data_dir
            ]

            # Mock successful creation
            default_path = MagicMock()
            default_path.mkdir.return_value = None
            mock_path_class.home.return_value = Path("/home/user")
            # Reset side_effect and return the default path
            mock_path_class.side_effect = None
            mock_path_class.return_value = default_path

            pc = config.PlottyConfig()

            # Should create and return default workspace
            assert pc.workspace_path == default_path

    def test_find_workspace_creation_failure(self):
        """Test workspace creation failure."""
        with (
            patch("config.Path") as mock_path_class,
            patch("config.user_data_dir") as mock_user_data_dir,
        ):
            # Mock all candidates fail
            mock_path_class.side_effect = [
                MagicMock(exists=False, is_dir=False),  # explicit path
                MagicMock(exists=False, is_dir=False),  # current/plotty-workspace
                MagicMock(exists=False, is_dir=False),  # home/plotty-workspace
                MagicMock(exists=False, is_dir=False),  # user_data_dir
            ]

            # Mock creation failure
            default_path = MagicMock()
            default_path.mkdir.side_effect = OSError("Permission denied")
            mock_path_class.home.return_value = Path("/home/user")
            # Reset side_effect and return the default path
            mock_path_class.side_effect = None
            mock_path_class.return_value = default_path

            with pytest.raises(Exception):  # PlottyNotFoundError
                config.PlottyConfig()

    def test_load_config_existing_file(self):
        """Test loading existing configuration file."""
        test_config = {"vpype": {"preset": "hq"}, "paper": {"default_size": "A3"}}

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                result = pc.load_config()

                assert result == test_config

    def test_load_config_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        with patch("config.Path") as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path_instance.__str__ = lambda: "/test/config.yaml"
            mock_path_class.return_value = mock_path_instance

            pc = config.PlottyConfig()
            result = pc.load_config()

            # Should return default config
            assert "vpype" in result
            assert "paper" in result
            assert result["vpype"]["preset"] == "fast"

    def test_load_config_empty_file(self):
        """Test loading empty configuration file."""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                result = pc.load_config()

                # Should return default config for empty file
                assert "vpype" in result
                assert "paper" in result

    def test_load_config_yaml_error(self):
        """Test loading configuration with YAML error."""
        with patch("builtins.open", mock_open(read_data="invalid: yaml: content: [")):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()

                with pytest.raises(Exception):  # PlottyConfigError
                    pc.load_config()

    def test_load_config_os_error(self):
        """Test loading configuration with OS error."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()

                with pytest.raises(Exception):  # PlottyConfigError
                    pc.load_config()

    def test_save_config_success(self):
        """Test successful configuration saving."""
        test_config = {"vpype": {"preset": "default"}, "paper": {"default_size": "A4"}}

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent = MagicMock()
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                pc.save_config(test_config)

                # Verify file was opened for writing
                mock_file.assert_called_once_with(
                    mock_path_instance, "w", encoding="utf-8"
                )

    def test_save_config_yaml_error(self):
        """Test saving configuration with YAML error."""
        test_config = {"invalid": object()}  # Non-serializable object

        with patch("builtins.open", mock_open()):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent = MagicMock()
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()

                with pytest.raises(Exception):  # PlottyConfigError
                    pc.save_config(test_config)

    def test_save_config_os_error(self):
        """Test saving configuration with OS error."""
        test_config = {"vpype": {"preset": "fast"}}

        with patch("builtins.open", side_effect=OSError("Disk full")):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent = MagicMock()
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()

                with pytest.raises(Exception):  # PlottyConfigError
                    pc.save_config(test_config)

    def test_default_config_structure(self):
        """Test default configuration structure."""
        with patch("config.Path") as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path_instance.__str__ = lambda: "/test/workspace"
            mock_path_class.return_value = mock_path_instance

            pc = config.PlottyConfig()
            default = pc._default_config()

            assert "workspace" in default
            assert "vpype" in default
            assert "paper" in default
            assert default["vpype"]["preset"] == "fast"
            assert default["paper"]["default_size"] == "A4"
            assert default["paper"]["default_margin_mm"] == 10.0

    def test_get_vpype_preset_from_config(self):
        """Test getting vpype preset from configuration."""
        test_config = {"vpype": {"preset": "hq"}, "paper": {"default_size": "A3"}}

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                preset = pc.get_vpype_preset()

                assert preset == "hq"

    def test_get_vpype_preset_default(self):
        """Test getting vpype preset with default fallback."""
        test_config = {"paper": {"default_size": "A3"}}  # No vpype section

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                preset = pc.get_vpype_preset()

                assert preset == "fast"  # Default value

    def test_get_default_paper_size_from_config(self):
        """Test getting default paper size from configuration."""
        test_config = {"vpype": {"preset": "hq"}, "paper": {"default_size": "A3"}}

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                paper_size = pc.get_default_paper_size()

                assert paper_size == "A3"

    def test_get_default_paper_size_default(self):
        """Test getting default paper size with fallback."""
        test_config = {"vpype": {"preset": "hq"}}  # No paper section

        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                paper_size = pc.get_default_paper_size()

                assert paper_size == "A4"  # Default value
