"""Ark - Utilities."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
import re
from pathlib import Path
from typing import Any, List, Optional, Union

from ark.settings import config

logger = logging.getLogger(__name__)


def fuzzy_match_strings(base: str, comparator: str) -> bool:
    """
    Fuzzy match two strings.

    Rules:
        - Both strings are converted to lowercase and stripped.
        - If the base string is equal to the comparator string, return True.
        - If the base string is in the comparator string, return True.
        - If the comparator string is in the base string, return True.
        - Otherwise, return False.

    Args:
        base (str): The base string.
        comparator (str): The string to compare against.

    Returns:
        bool: True if the strings match, False otherwise.
    """
    base = base.lower().strip()
    comparator = comparator.lower().strip()
    return any(
        [
            base == comparator,
            base in comparator,
            comparator in base,
        ]
    )


def convert_bool_to_str(data: Any) -> Any:
    """
    Convert boolean values to strings.

    Args:
        data (Any): The data to convert.

    Returns:
        Any: The converted data.
    """
    if isinstance(data, bool):
        return str(data)
    if isinstance(data, list):
        return [convert_bool_to_str(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_bool_to_str(value) for key, value in data.items()}
    return data


def read_file_contents(
    filepath: Union[Path, str], encoding: str = config.ENCODING
) -> Union[str, None]:
    """
    Read the contents of a file.

    Args:
        filepath (Union[Path, str]): Path to the file.
        encoding (str, optional): The encoding to use.
            Defaults to config.ENCODING.

    Returns:
        Union[str, None]: The contents of the file or None if the file could
            not be read.
    """
    filepath = Path(filepath)
    logger.debug("Reading file: '%s'", filepath)
    try:
        with open(filepath, "r", encoding=encoding) as current_file:
            content = current_file.read()
    except UnicodeDecodeError:
        logger.error(
            "Could not read file: %s. Error: UnicodeDecodeError", filepath
        )
        return None
    except PermissionError as permission_error:
        logger.error(
            "Could not read file: %s. Error: '%s'",
            filepath,
            permission_error,
        )
        return None
    logger.debug("Successfully read file: '%s'", filepath)
    return content


def write_file_contents(
    filepath: Union[Path, str],
    content: str,
    encoding: str = config.ENCODING,
) -> bool:
    """
    Write the contents of a file.

    Args:
        filepath (Union[Path, str]): Path to the file.
        content (str): The content to write.
        encoding (str, optional): The encoding to use.
            Defaults to config.ENCODING.

    Returns:
        bool: True if the file was written, False otherwise.
    """
    filepath = Path(filepath)
    logger.debug("Writing file: '%s'", filepath)
    try:
        with open(filepath, "w", encoding=encoding) as current_file:
            current_file.write(content)
    except PermissionError as permission_error:
        logger.error(
            "Could not write file: %s. Error: '%s'",
            filepath,
            permission_error,
        )
        return False
    logger.debug("Successfully wrote file: '%s'", filepath)
    return True


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
        logger.info("Required directories are missing: '%s'", missing_dirs)
    else:
        logger.debug("No missing directories found for: '%s'", project_name)

    # Check for required files
    missing_files: List[Union[str, Path]] = []
    for required_file in required_files:
        if not required_file.is_file():
            missing_files.append(required_file)
    if missing_files:
        logger.info("Required files are missing: '%s'", missing_files)
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


def get_valid_projects() -> list[str]:
    """
    Get a list of valid projects.

    Returns:
        list[str]: List of valid projects.
    """
    projects: list[str] = []
    for project in Path(config.PROJECTS_DIR).iterdir():
        if any(
            [
                project.stem.strip().lower() == "logs",
                project.stem.startswith("_"),
                project.stem.startswith("."),
            ]
        ):
            continue
        if not validate_project_dir(project.stem):
            projects.append(project.stem)
    return projects
