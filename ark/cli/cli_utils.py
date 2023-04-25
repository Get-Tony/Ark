"""Ark - Click Related Utilities."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import getpass
import logging
import re
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar, Union, cast

import click

from ark.settings import config

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


def validate_project_dir(
    project_name: str,
) -> Optional[dict[str, List[Union[str, Path]]]]:
    """
    Validate project directory.

    Args:
        project_name (str): Project name.

    Raises:
        ValueError: If project name is not valid.

    Returns:
        Optional[dict[str, List[Union[str, Path]]]]: A dictionary containing
            the project name and a list of required directories and files.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", Path(project_name).name):
        logger.critical(
            "Project name '%s' is not valid. It must only contain "
            "alphanumeric characters, dashes, and underscores.",
            project_name,
        )
        raise ValueError(
            "Project name is not valid. It must only contain alphanumeric "
            "characters, dashes, and underscores."
        )
    required_dirs = [
        Path(config.PROJECTS_DIR) / project_name / "project",
        Path(config.PROJECTS_DIR) / project_name / "inventory",
        Path(config.PROJECTS_DIR) / project_name / "env",
    ]
    required_files = [
        Path(config.PROJECTS_DIR) / project_name / "project" / "main.yml",
        Path(config.PROJECTS_DIR) / project_name / "env" / "envvars",
        Path(config.PROJECTS_DIR) / project_name / "env" / "ssh_key",
    ]

    logger.info("Checking for required files and directories")

    # Check for required directories
    missing_dirs: List[Union[str, Path]] = []
    for required_dir in required_dirs:
        if not required_dir.is_dir():
            missing_dirs.append(required_dir)
    if missing_dirs:
        logger.critical("Required directories are missing: '%s'", missing_dirs)
    else:
        logger.debug("No missing directories found for: '%s'", project_name)

    # Check for required files
    missing_files: List[Union[str, Path]] = []
    for required_file in required_files:
        if not required_file.is_file():
            missing_files.append(required_file)
    if missing_files:
        logger.critical("Required files are missing: '%s'", missing_files)
    else:
        logger.debug("No missing files found for: '%s'", project_name)

    # Return a report if any directories or files are missing
    if any(missing_dirs or missing_files):
        missing_report: dict[str, List[Union[str, Path]]] = {
            "missing_dirs": missing_dirs,
            "missing_files": missing_files,
        }
        return missing_report
    return None


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
