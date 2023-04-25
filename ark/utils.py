"""Ark - Utilities."""

import logging
from pathlib import Path
from typing import Any, Union

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
