"""Ark - Ansible Linting."""
__author__ = "Anthony Pagan <Get-Tony@outlook.com>"

import logging
import re
import subprocess
from pathlib import Path
from typing import Optional

from ark.core.run import get_playbook_path
from ark.settings import config

logger = logging.getLogger(__name__)


def ansible_lint_accessible() -> bool:
    """
    Check if ansible-lint is installed and accessible.

    Returns:
        bool: True if ansible-lint is installed and accessible,
            otherwise False.
    """
    try:
        lint_version = subprocess.check_output(
            ["ansible-lint", "--version", "--nocolor"],
            stderr=subprocess.STDOUT,
        )
        logger.debug(lint_version.decode(config.ENCODING).strip())
        return True
    except subprocess.CalledProcessError:
        logger.critical("ansible-lint is not installed.")
        return False


def lint_playbook_or_project(
    project_name: str, playbook_file: Optional[str], verbosity: int = 0
) -> Optional[str]:
    """
    Lint a playbook or project.

    Args:
        project_name (str): Project name.
        playbook_file (Optional[str]): Playbook filename.
        verbosity (int, optional): Verbosity level. Defaults to 0.

    Returns:
        Optional[str]: Linting output or None if the linting process fails.
    """
    if playbook_file:
        lint_target = get_playbook_path(project_name, playbook_file)
    else:
        lint_target = Path(config.PROJECTS_DIR) / project_name
    if not lint_target:
        logger.critical(
            "Could not find lint target '%s'",
            lint_target,
        )
        return None
    logger.info("Linting playbook: '%s'", str(lint_target).strip())
    lint_command = ["ansible-lint"]
    if playbook_file:
        lint_command.append(str(lint_target))
    lint_command.extend(
        [
            "--project-dir",
            str(Path(config.PROJECTS_DIR) / project_name),
        ]
    )
    verbosity = min(verbosity, 3)
    if verbosity > 0:
        lint_command.append("-" + "v" * verbosity)
    lint_command.append("--nocolor")
    logger.debug("Lint command: '%s'", " ".join(lint_command))
    result = None
    try:
        process = subprocess.run(
            lint_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=config.ENCODING,
            cwd=str(Path(config.PROJECTS_DIR) / project_name),
            check=True,
        )
        result = process.stdout
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                lint_command,
                output=result,
                stderr=process.stderr,
            )

    except subprocess.CalledProcessError as linting_error:
        error_info = re.search(
            r"Failed to load YAML file\n(.+?):\d+", linting_error.stderr
        )
        if error_info:
            playbook_path = error_info.group(1)
            logger.critical(
                "Error linting project '%s'! "
                "Problematic playbook: '%s', Error: '%s'",
                project_name,
                playbook_path,
                linting_error.stderr.strip(),
            )
        else:
            logger.critical("Error linting target '%s':", lint_target)
            indented_stderr = "\n".join(
                "    " + line if line else line
                for line in linting_error.stderr.split("\n")
            )
            logger.critical(
                "%s",
                indented_stderr,
            )
        result = linting_error.output
    if not result:
        return None

    indented_result = "\n".join(
        "    " + line if line else line for line in result.split("\n")
    )

    logger.info(indented_result.strip())
    return indented_result.strip()
