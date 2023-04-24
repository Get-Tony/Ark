"""Ark - Project Commands."""

import logging
from pathlib import Path
from typing import List, Optional

import click

from ark import utils
from ark.settings import config

from .call_logger import log_command_call

logger = logging.getLogger(__name__)


def find_artifacts(project_name: str) -> List[Path]:
    """Find all artifact folders in a project."""
    artifact_root_path = Path(config.PROJECTS_DIR) / project_name / "artifacts"
    logger.debug("Checking project for artifacts: '%s'", project_name)
    artifact_folders = [
        path
        for path in artifact_root_path.glob("**")
        if (path / "stdout").is_file()
    ]
    logger.debug(
        "Found '%s' artifacts for project: '%s'",
        len(artifact_folders),
        project_name,
    )
    return artifact_folders


@click.command("report")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=utils.project_name_validation_callback,
)
@click.option(
    "-l",
    "--last",
    type=int,
    default=None,
    help="Display the last x reports.",
)
@log_command_call()
def report_command(project_name: str, last: Optional[int]) -> None:
    """Display reports for a given project."""
    artifact_folders = find_artifacts(project_name)
    artifact_folders = utils.sort_and_limit_artifacts(artifact_folders, last)

    if not artifact_folders:
        click.echo("No artifacts found.")
        return
    for artifact_path in artifact_folders:
        utils.display_artifact_report(artifact_path)
