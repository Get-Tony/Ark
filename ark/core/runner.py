"""Ark - Ansible Project Execution."""

import logging
from pathlib import Path
from typing import Any

import ansible_runner

from ark.settings import config

logger = logging.getLogger(__name__)


def prepare_extra_vars(extra_vars: str) -> dict[str, str]:
    """Prepare extra variables for the playbook."""
    extra_vars_dict = {}
    if extra_vars:
        extra_vars_list = extra_vars.split(",")
        for pair in extra_vars_list:
            key, value = pair.split("=")
            extra_vars_dict[key] = value

    return extra_vars_dict


def run_ansible_playbook(  # pylint: disable=too-many-arguments
    project_name: str,
    playbook_path: Path,
    rotate_artifacts: int,
    limit: str,
    extra_vars_dict: dict[str, str],
    verbosity: int = 0,
) -> Any:
    """Run an Ansible playbook using ansible-runner."""
    logger.info(
        "Running playbook: %s. "
        "(limit: %s, rotate artifacts: %s, extra vars: %s)",
        playbook_path,
        limit or "None",
        rotate_artifacts,
        extra_vars_dict or "None",
    )
    result = ansible_runner.run(
        private_data_dir=Path(config.PROJECTS_DIR) / project_name,
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
    return result
