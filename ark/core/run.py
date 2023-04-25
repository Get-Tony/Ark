"""Ark - Playbook Execution."""

import logging
from pathlib import Path
from typing import Any, List, Optional

import ansible_runner

from ark.settings import config

logger = logging.getLogger(__name__)


def find_playbooks(project_name: str) -> List[str]:
    """
    Find all playbooks for a project.

    Rules:
        - Playbooks are located in the project directory under the 'project'
            subdirectory.
        - Playbooks must have a '.yml' or '.yaml' extension.

    Args:
        project_name (str): The name of the project.

    Returns:
        List[str]: A list of playbooks.
    """
    logger.info("Finding playbooks for: '%s'", project_name)
    playbooks: List[str] = []
    for playbook in (
        Path(config.PROJECTS_DIR) / project_name / "project"
    ).glob("*.yml"):
        playbooks.append(playbook.name)
    for playbook in (
        Path(config.PROJECTS_DIR) / project_name / "project"
    ).glob("*.yaml"):
        playbooks.append(playbook.name)
    logger.info(
        "Found playbooks for %s: '%s'", project_name, playbooks or "None"
    )
    return playbooks


def get_playbook_path(project_name: str, playbook_file: str) -> Optional[Path]:
    """
    Get the path to a playbook.

    Args:
        project_name (str): Project name.
        playbook_file (str): Playbook filename.

    Returns:
        Optional[Path]: Path to the playbook or None if it does not exist.
    """
    playbook_path: Path = (
        Path(config.PROJECTS_DIR) / project_name / "project" / playbook_file
    )
    logger.info("Looking for playbook: '%s'", playbook_path)
    if not playbook_path.is_file():
        logger.error(
            "Playbook '%s' does not exist for Project: '%s'",
            playbook_file,
            project_name,
        )
        return None
    logger.info("Found playbook: '%s'", playbook_path)
    return playbook_path


def prepare_extra_vars(extra_vars: str) -> dict[str, str]:
    """
    Prepare extra vars for ansible-runner.

    Args:
        extra_vars (str): A comma separated list of key=value pairs.

    Returns:
        dict[str, str]: A dictionary of extra vars.
    """
    extra_vars_dict = {}
    if extra_vars:
        extra_vars_list = extra_vars.split(",")
        for pair in extra_vars_list:
            key, value = pair.split("=")
            extra_vars_dict[key] = value
    logger.info("Extra vars: %s", extra_vars_dict or "None")
    return extra_vars_dict


def run_ansible_playbook(  # pylint: disable=too-many-arguments
    project_name: str,
    playbook_path: Path,
    rotate_artifacts: int,
    limit: str,
    extra_vars_dict: dict[str, str],
    verbosity: int = 0,
) -> Any:
    """
    Run an Ansible playbook.

    Args:
        playbook_path (Path): Path to the playbook.
        rotate_artifacts (int): Artifact rotation limit.
        limit (str): Ansible limit.
        extra_vars_dict (dict[str, str]): Extra vars.
        verbosity (int, optional): Ansible verbosity. Defaults to 0.

    Returns:
        Any: Ansible runner result.
    """
    logger.info(
        "Running playbook: %s. "
        "(limit: %s, rotate artifacts: %s, extra vars: %s)",
        playbook_path,
        limit or "None",
        rotate_artifacts,
        extra_vars_dict or "None",
    )
    private_data_dir = Path(config.PROJECTS_DIR) / project_name
    result = ansible_runner.run(
        private_data_dir=private_data_dir,
        playbook=str(playbook_path),
        rotate_artifacts=rotate_artifacts,
        limit=limit,
        extravars=extra_vars_dict if extra_vars_dict else None,
        verbosity=verbosity,
    )

    if result.status != "successful":
        logger.error(
            "Playbook failed (return code: %s): '%s'", result.rc, playbook_path
        )
    else:
        logger.info("Playbook completed successfully: '%s'", playbook_path)
    logger.debug("Playbook result: %s", result.status)
    return result
