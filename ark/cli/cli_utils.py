"""Ark - Click Related Utilities."""

import getpass
import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import click

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=Callable[..., Any])


def log_command_call(log_level: str = "info") -> Callable[[T], T]:
    """
    A decorator that logs the start, end, and time elapsed of a Click command
    call with a specified log level. It also logs the provided arguments
    and options.

    Args:
        log_level (str, optional): The log level to use for logging.
            Defaults to "info".

    Returns:
        Callable[[T], T]: The decorated function.
    """

    def decorator(func: T) -> T:
        """Command call logging decorator."""

        @wraps(func)
        def command_logger(*args: Any, **kwargs: Any) -> Any:
            """Log command call."""
            ctx = click.get_current_context()
            command_name = ctx.command_path
            log_function = getattr(logger, log_level.lower())
            log_function(
                "User: '%s', Command: '%s'", getpass.getuser(), command_name
            )

            # Log arguments and options
            params = [
                f"{param.name}: {ctx.params[param.name] if ctx.params[param.name] is not None else 'None'}"  # noqa: E501 pylint: disable=line-too-long
                for param in ctx.command.params
                if param.name is not None
            ]
            log_function("Parameters: {%s}", ", ".join(params))

            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time

            log_function("Command finished: %s", command_name)
            logger.debug(
                "Time elapsed for command '%s': %.2f seconds",
                command_name,
                elapsed_time,
            )
            return result

        return cast(T, command_logger)

    return decorator
