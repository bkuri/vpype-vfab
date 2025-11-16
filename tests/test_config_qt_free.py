"""Qt-free tests for vpype_vfab.config module."""

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
mock_exceptions.VfabConfigError = mock_plotty_config_error
mock_exceptions.VfabNotFoundError = mock_plotty_not_found_error
sys.modules["vpype_vfab.exceptions"] = mock_exceptions

# Now import the config module
import importlib.util

spec = importlib.util.spec_from_file_location(
    "config", "/home/bk/source/vpype-vfab/src/config.py"
)
if spec is None:
    raise ImportError("Could not load config module")
config = importlib.util.module_from_spec(spec)
sys.modules["config"] = config  # Register in sys.modules for patching
if spec.loader is None:
    raise ImportError("Could not get loader for config module")
spec.loader.exec_module(config)


class TestConfigQtFree:
    """Qt-free test suite for config module."""

    def setup_method(self):
        """Reset any global state before each test."""
        # Ensure we're using real yaml, not a mocked version from other test files
        import importlib

        if "yaml" in sys.modules:
            del sys.modules["yaml"]
        real_yaml = importlib.import_module("yaml")
        sys.modules["yaml"] = real_yaml

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
            patch("config.Path.cwd") as mock_cwd,
            patch("config.Path.home") as mock_home,
        ):
            # Mock workspace finding - current directory has workspace
            mock_workspace = MagicMock()
            mock_workspace.exists.return_value = True
            mock_workspace.is_dir.return_value = True

            mock_config_path = MagicMock()
            mock_config_path.name = "config.yaml"

            mock_presets_path = MagicMock()
            mock_presets_path.name = "vpype-presets.yaml"

            mock_workspace.__truediv__ = MagicMock(
                side_effect=lambda x: {
                    "config.yaml": mock_config_path,
                    "vpype-presets.yaml": mock_presets_path,
                }.get(x, MagicMock())
            )

            # Mock Path.cwd() to return the workspace
            mock_cwd.return_value.__truediv__.return_value = mock_workspace

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
                MagicMock(exists=True, is_dir=True),  # current/vfab-workspace
                MagicMock(),  # home/vfab-workspace
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
                MagicMock(exists=False, is_dir=False),  # current/vfab-workspace
                MagicMock(exists=True, is_dir=True),  # home/vfab-workspace
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
                MagicMock(exists=False, is_dir=False),  # current/vfab-workspace
                MagicMock(exists=False, is_dir=False),  # home/vfab-workspace
                MagicMock(exists=True, is_dir=True),  # user_data_dir
            ]
            mock_user_data_dir.return_value = "/user/data/plotty"

            pc = config.PlottyConfig()

            # Should find user data directory workspace
            assert pc.workspace_path is not None

    def test_find_workspace_create_default(self):
        """Test workspace creation when none found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temp directory that doesn't have vfab-workspace
            temp_path = Path(temp_dir)

            # Mock home to be in our temp directory
            with patch("config.Path.home") as mock_home:
                mock_home.return_value = temp_path

                pc = config.PlottyConfig()

                # Should create and return default workspace
                expected_workspace = temp_path / "vfab-workspace"
                assert pc.workspace_path == expected_workspace
                assert expected_workspace.exists()

    def test_find_workspace_creation_failure(self):
        """Test workspace creation failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file where we want to create directory (causes failure)
            blocking_file = temp_path / "vfab-workspace"
            blocking_file.write_text("blocked")

            # Mock home to be in our temp directory
            with patch("config.Path.home") as mock_home:
                mock_home.return_value = temp_path

                with pytest.raises(Exception):  # VfabNotFoundError
                    config.PlottyConfig()

    def test_load_config_existing_file(self):
        """Test loading existing configuration file."""
        test_config = {"vpype": {"preset": "hq"}, "paper": {"default_size": "A3"}}
        # Create YAML string manually to avoid mock contamination
        config_yaml = "vpype:\n  preset: hq\npaper:\n  default_size: A3\n"

        with patch("builtins.open", mock_open(read_data=config_yaml)):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                result = pc.load_config()

                assert result == test_config

    def test_load_config_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use real temporary directory for workspace
            workspace = Path(temp_dir)

            pc = config.PlottyConfig(str(workspace))
            result = pc.load_config()

            # Should return default config
            assert "vpype" in result
            assert "paper" in result
            assert result["vpype"]["preset"] == "fast"

    def test_load_config_empty_file(self):
        """Test loading empty configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use real temporary directory for workspace
            workspace = Path(temp_dir)
            config_file = workspace / "config.yaml"

            # Create empty config file
            config_file.write_text("")

            pc = config.PlottyConfig(str(workspace))
            result = pc.load_config()

            # Should return empty dict for empty file (None or {} = {})
            assert result == {}

    def test_load_config_yaml_error(self):
        """Test loading configuration with YAML error."""
        # Mock yaml.safe_load to raise YAMLError
        with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
            with patch("builtins.open"):
                with patch("config.Path") as mock_path_class:
                    mock_path_instance = MagicMock()
                    mock_path_instance.exists.return_value = True
                    mock_path_class.return_value = mock_path_instance

                    pc = config.PlottyConfig()

                    with pytest.raises(Exception):  # VfabConfigError
                        pc.load_config()

    def test_load_config_os_error(self):
        """Test loading configuration with OS error."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()

                with pytest.raises(Exception):  # VfabConfigError
                    pc.load_config()

    def test_save_config_success(self):
        """Test successful configuration saving."""
        test_config = {"vpype": {"preset": "default"}, "paper": {"default_size": "A4"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            pc = config.PlottyConfig(str(workspace))
            pc.save_config(test_config)

            # Verify file was created and contains correct content
            config_file = workspace / "config.yaml"
            assert config_file.exists()

            with open(config_file) as f:
                saved_config = yaml.safe_load(f)

            assert saved_config == test_config

    def test_save_config_yaml_error(self):
        """Test saving configuration with YAML error."""
        test_config = {"vpype": {"preset": "default"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            pc = config.PlottyConfig(str(workspace))

            # Mock yaml.dump to raise an exception
            with patch("yaml.dump", side_effect=yaml.YAMLError("YAML error")):
                with pytest.raises(Exception):  # VfabConfigError
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

                with pytest.raises(Exception):  # VfabConfigError
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

        # Create YAML string manually to avoid mock contamination
        config_yaml = "vpype:\n  preset: hq\npaper:\n  default_size: A3\n"
        with patch("builtins.open", mock_open(read_data=config_yaml)):
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

        # Create YAML string manually to avoid mock contamination
        config_yaml = "paper:\n  default_size: A3\n"
        with patch("builtins.open", mock_open(read_data=config_yaml)):
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

        # Create YAML string manually to avoid mock contamination
        config_yaml = "vpype:\n  preset: hq\npaper:\n  default_size: A3\n"
        with patch("builtins.open", mock_open(read_data=config_yaml)):
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

        # Create YAML string manually to avoid mock contamination
        config_yaml = "vpype:\n  preset: hq\n"
        with patch("builtins.open", mock_open(read_data=config_yaml)):
            with patch("config.Path") as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_class.return_value = mock_path_instance

                pc = config.PlottyConfig()
                paper_size = pc.get_default_paper_size()

                assert paper_size == "A4"  # Default value
