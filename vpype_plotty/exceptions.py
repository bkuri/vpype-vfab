"""Custom exceptions for vpype-plotty."""


class PlottyError(Exception):
    """Base exception for vpype-plotty."""

    pass


class PlottyNotFoundError(PlottyError):
    """ploTTY installation or workspace not found."""

    pass


class PlottyConfigError(PlottyError):
    """ploTTY configuration error."""

    pass


class PlottyJobError(PlottyError):
    """Job creation or management error."""

    pass
