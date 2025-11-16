"""Command decorators for vpype-vfab to eliminate DRY violations."""

from functools import wraps
from typing import Callable, Optional

import click
import vpype_cli

from vpype_vfab.base import StreamlinedVfabCommand


def vfab_command(
    *options, requires_workspace: bool = True, error_context: Optional[str] = None
):
    """Universal vfab command decorator that handles common scaffolding.

    This decorator eliminates repetitive code across all vfab commands by:
    - Adding standard --workspace option when required
    - Applying vpype_cli global processor
    - Handling command initialization and error handling
    - Supporting custom options

    Args:
        *options: Custom click.option decorators to apply
        requires_workspace: Whether to add --workspace option (default: True)
        error_context: Default error context for error handling

    Returns:
        Decorated command function with consistent scaffolding
    """

    def decorator(func: Callable) -> Callable:
        # Wrap with error handling and initialization first
        @wraps(func)
        def wrapper(document, *args, **kwargs):
            # Extract workspace from kwargs
            workspace = kwargs.get("workspace")

            # Initialize command
            cmd = StreamlinedVfabCommand(workspace)

            try:
                # Call the original function with cmd as first argument after document
                return func(cmd, document, *args, **kwargs)
            except Exception as e:
                # Use provided error context or function name as fallback
                context = error_context or func.__name__
                cmd.handle_error(e, context)

        # Apply decorators in correct order to the wrapper
        command_func = wrapper

        # Apply vpype_cli global processor first
        command_func = vpype_cli.global_processor(command_func)

        # Add workspace option if required
        if requires_workspace:
            command_func = click.option("--workspace", help="vfab workspace path")(
                command_func
            )

        # Add custom options (in reverse order)
        for opt in reversed(options):
            command_func = opt(command_func)

        # Finally apply click.command to make it a proper Click command
        command_func = click.command()(command_func)

        return command_func

    return decorator


def workspace_option(help_text: str = "vfab workspace path") -> Callable:
    """Standard workspace option decorator.

    Args:
        help_text: Help text for the workspace option

    Returns:
        Click option decorator for workspace
    """
    return click.option("--workspace", "-w", help=help_text)


def format_option(default: str = "table", choices: Optional[list] = None) -> Callable:
    """Standard format option decorator.

    Args:
        default: Default format value
        choices: List of allowed format choices

    Returns:
        Click option decorator for format
    """
    if choices is None:
        choices = ["table", "json", "yaml"]

    return click.option(
        "--format",
        "-f",
        default=default,
        type=click.Choice(choices),
        help="Output format",
    )


def name_option(required: bool = False, help_text: Optional[str] = None) -> Callable:
    """Standard name option decorator.

    Args:
        required: Whether the name option is required
        help_text: Custom help text

    Returns:
        Click option decorator for name
    """
    if help_text is None:
        help_text = (
            "Job name or ID"
            if required
            else "Job name (auto-generated if not provided)"
        )

    return click.option("--name", "-n", required=required, help=help_text)


def priority_option(default: int = 1) -> Callable:
    """Standard priority option decorator.

    Args:
        default: Default priority value

    Returns:
        Click option decorator for priority
    """
    return click.option(
        "--priority", "-p", type=int, default=default, help="Job priority (1=highest)"
    )


def preset_option(default: str = "fast") -> Callable:
    """Standard preset option decorator.

    Args:
        default: Default preset value

    Returns:
        Click option decorator for preset
    """
    return click.option(
        "--preset",
        default=default,
        type=click.Choice(["fast", "default", "hq"]),
        help="Optimization preset (fast, default, hq)",
    )


def queue_option() -> Callable:
    """Standard queue option decorator.

    Returns:
        Click option decorator for queue flag
    """
    return click.option(
        "--queue", "-q", is_flag=True, help="Add job to queue after creation"
    )


def follow_option() -> Callable:
    """Standard follow option decorator.

    Returns:
        Click option decorator for follow flag
    """
    return click.option(
        "--follow", "-f", is_flag=True, help="Follow job progress with updates"
    )


def poll_rate_option(default: float = 1.0) -> Callable:
    """Standard poll rate option decorator.

    Args:
        default: Default poll rate in seconds

    Returns:
        Click option decorator for poll rate
    """
    return click.option(
        "--poll-rate",
        "-r",
        type=float,
        default=default,
        help="Polling rate in seconds (0.1-10.0, default: 1.0)",
    )


def fast_option() -> Callable:
    """Standard fast option decorator.

    Returns:
        Click option decorator for fast flag
    """
    return click.option(
        "--fast", is_flag=True, help="Fast updates (100ms polling rate)"
    )


def slow_option() -> Callable:
    """Standard slow option decorator.

    Returns:
        Click option decorator for slow flag
    """
    return click.option("--slow", is_flag=True, help="Slow updates (5s polling rate)")


def force_option() -> Callable:
    """Standard force option decorator.

    Returns:
        Click option decorator for force flag
    """
    return click.option(
        "--force", is_flag=True, help="Force action without confirmation"
    )


def limit_option() -> Callable:
    """Standard limit option decorator.

    Returns:
        Click option decorator for limit
    """
    return click.option("--limit", type=int, help="Limit number of jobs")


def state_option() -> Callable:
    """Standard state option decorator.

    Returns:
        Click option decorator for state filter
    """
    return click.option("--state", "-s", help="Filter by job state")


def pen_mapping_option() -> Callable:
    """Standard pen mapping option decorator.

    Returns:
        Click option decorator for pen mapping
    """
    return click.option(
        "--pen-mapping",
        type=click.Choice(["auto", "sequential", "single", "interactive"]),
        default="auto",
        help="Pen mapping preset for multi-layer designs",
    )
