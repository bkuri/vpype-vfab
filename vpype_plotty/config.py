"""ploTTY configuration detection and management."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from platformdirs import user_data_dir

from vpype_plotty.exceptions import PlottyConfigError, PlottyNotFoundError


class PlottyConfig:
    """ploTTY configuration detection and management."""

    def __init__(self, workspace_path: Optional[str] = None) -> None:
        """Initialize ploTTY configuration manager.

        Args:
            workspace_path: Optional path to ploTTY workspace directory
        """
        self.workspace_path = self._find_workspace(workspace_path)
        self.config_path = self.workspace_path / "config.yaml"
        self.vpype_presets_path = self.workspace_path / "vpype-presets.yaml"

    def _find_workspace(self, workspace_path: Optional[str]) -> Path:
        """Find ploTTY workspace using multiple strategies.

        Args:
            workspace_path: Explicit workspace path to check first

        Returns:
            Path to ploTTY workspace directory

        Raises:
            PlottyNotFoundError: If no suitable workspace found
        """
        candidates = [
            Path(workspace_path) if workspace_path else None,
            Path.cwd() / "plotty-workspace",
            Path.home() / "plotty-workspace",
            Path(user_data_dir("plotty")),
        ]

        for candidate in candidates:
            if candidate and candidate.exists() and candidate.is_dir():
                return candidate

        # Create default workspace if none found
        default = Path.home() / "plotty-workspace"
        try:
            default.mkdir(parents=True, exist_ok=True)
            return default
        except OSError as e:
            raise PlottyNotFoundError(
                f"ploTTY workspace not found and could not create default at {default}: {e}"
            )

    def load_config(self) -> Dict[str, Any]:
        """Load ploTTY configuration.

        Returns:
            Configuration dictionary

        Raises:
            PlottyConfigError: If configuration cannot be loaded
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            return self._default_config()
        except (yaml.YAMLError, OSError) as e:
            raise PlottyConfigError(
                f"Failed to load ploTTY config from {self.config_path}: {e}"
            )

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save ploTTY configuration.

        Args:
            config: Configuration dictionary to save

        Raises:
            PlottyConfigError: If configuration cannot be saved
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except (yaml.YAMLError, OSError) as e:
            raise PlottyConfigError(
                f"Failed to save ploTTY config to {self.config_path}: {e}"
            )

    def _default_config(self) -> Dict[str, Any]:
        """Default ploTTY configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "workspace": str(self.workspace_path),
            "vpype": {
                "preset": "fast",
                "presets_file": str(self.vpype_presets_path),
            },
            "paper": {
                "default_size": "A4",
                "default_margin_mm": 10.0,
            },
        }

    def get_vpype_preset(self) -> str:
        """Get default vpype preset from configuration.

        Returns:
            Default vpype preset name
        """
        config = self.load_config()
        return config.get("vpype", {}).get("preset", "fast")

    def get_default_paper_size(self) -> str:
        """Get default paper size from configuration.

        Returns:
            Default paper size
        """
        config = self.load_config()
        return config.get("paper", {}).get("default_size", "A4")
