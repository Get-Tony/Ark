"""Ark - Click Related Utilities."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import getpass
import logging
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar, Union, cast

import click

from ark.settings import config
from ark.utils import validate_project_dir

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=Callable[..., Any])


def log_command_call(log_level: str = "info") -> Callable[[T], T]:
    """
    Command call logging decorator.

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


def echo_or_page(content: str, page: Optional[bool]) -> None:
    """
    Echo content to the terminal or page it.

    Args:
        content (str): Content to echo or page.
        page (Optional[bool]): Pages the output if True.
    """
    if page:
        click.echo_via_pager(content)
    else:
        click.echo(content)


def project_name_validation_callback(
    ctx: click.Context,
    param: click.Parameter,  # pylint: disable=unused-argument
    project_name: str,
) -> Optional[str]:
    """
    Validate a project.

    Args:
        ctx (click.Context): Click context. Do not use.
        param (click.Parameter): Click parameter. Do not use.
        project_name (str): Project name to validate.

    Returns:
        Optional[str]: Validated value or None in case of an error.
    """
    logger.debug(
        "Validating project '%s' for the '%s' command.",
        project_name,
        ctx.info_name,
    )
    missing_objects: Optional[
        dict[str, List[Union[str, Path]]]
    ] = validate_project_dir(str(Path(config.PROJECTS_DIR) / project_name))
    if missing_objects:
        click.echo("Project is missing required files or directories:")
        click.echo(f" Path: {Path(config.PROJECTS_DIR) / project_name}")
        for missing_dir in missing_objects["missing_dirs"]:
            click.echo(f" - directory: {missing_dir}")
        for missing_file in missing_objects["missing_files"]:
            click.echo(f" - file: {missing_file}")
        click.echo("Please resolve the issues above and try again.")
        ctx.abort()
    logger.debug("Project validation complete.")
    return project_name
