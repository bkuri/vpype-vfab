"""Base command class for vpype-plotty."""

from typing import Dict, Optional

import click

from vpype_plotty.database import StreamlinedPlottyIntegration


class StreamlinedPlottyCommand:
    """Base class for streamlined ploTTY commands."""

    def __init__(self, workspace: Optional[str] = None):
        """Initialize command with ploTTY integration.

        Args:
            workspace: Optional ploTTY workspace path
        """
        self.plotty = StreamlinedPlottyIntegration(workspace)

    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle command errors consistently.

        Args:
            error: Exception that occurred
            context: Optional context for the error
        """
        message = f"✗ Error: {error}"
        if context:
            message = f"✗ Error in {context}: {error}"
        click.echo(message, err=True)
        raise click.ClickException(str(error))

    def get_pen_mapping(self, document, preset: str = "auto") -> Optional[Dict]:
        """Get pen mapping using simple presets.

        Args:
            document: vpype document
            preset: Mapping preset (auto, sequential, single)

        Returns:
            Pen mapping dictionary or None
        """
        if len(document.layers) <= 1:
            return None  # Single layer uses default pen

        if preset == "auto":
            # Automatic mapping: cycle through pens 1-4
            return {i: (i % 4) + 1 for i in document.layers}
        elif preset == "sequential":
            # Sequential mapping: 1, 2, 3, 4...
            return {i: i + 1 for i in document.layers}
        else:
            # Default to auto mapping
            return {i: (i % 4) + 1 for i in document.layers}
