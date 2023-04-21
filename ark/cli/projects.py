"""Ark - Project Commands."""

import getpass
import logging
from pathlib import Path
from typing import List, Optional

import click

from ark import utils
from ark.core import linter, runner
from ark.settings import config

logger = logging.getLogger(__name__)


@click.group("projects")
def projects_group() -> None:
    """Project operations."""


@projects_group.command("run")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=utils.project_name_validation_callback,
)
@click.argument("playbook_file", type=click.Path(exists=False), required=False)
@click.option(
    "--rotate-artifacts",
    default=7,
    type=click.IntRange(1, 31),
    help="Number of artifacts to keep.",
)
@click.option(
    "--limit",
    default="",
    type=str,
    help="Limit the playbook execution to a specific group or host.",
)
@click.option(
    "--extra-vars",
    default="",
    type=str,
    help="Pass additional variables as key-value pairs.",
)
@click.option(
    "-v",
    "--verbosity",
    default=0,
    type=int,
    help="Increase the verbosity of the output.",
)
def run_playbook(  # pylint: disable=too-many-arguments
    project_name: str,
    playbook_file: str,
    rotate_artifacts: int,
    limit: str,
    extra_vars: str,
    verbosity: int,
) -> None:
    """Run a Project playbook."""
    logger.info(
        "Command: run, User: %s, Project: %s",
        getpass.getuser(),
        project_name,
    )

    if not playbook_file:
        click.echo("Please specify a playbook to run.")
        click.echo(f"Available playbooks for the '{project_name}' project:")
        for playbook in utils.find_playbooks(
            str(Path(config.PROJECTS_DIR) / project_name)
        ):
            click.echo(f" - {playbook}")
        return

    playbook_path = utils.get_playbook_path(project_name, playbook_file)
    if not playbook_path:
        click.echo(
            f"Playbook '{playbook_file}' not found in project '{project_name}'"
        )
        click.echo("Available playbooks:")
        for playbook in utils.find_playbooks(
            str(Path(config.PROJECTS_DIR) / project_name)
        ):
            click.echo(f" - {playbook}")
        return
    extra_vars_dict = runner.prepare_extra_vars(extra_vars)
    click.echo(f"Running playbook: {playbook_path}")
    play_results = runner.run_ansible_playbook(
        project_name=project_name,
        playbook_path=playbook_path,
        rotate_artifacts=rotate_artifacts,
        limit=limit,
        extra_vars_dict=extra_vars_dict,
        verbosity=verbosity,
    )
    if play_results:
        click.echo(
            f"Playbook run completed with status: {play_results.status}"
        )
        return
    click.echo("Run returned no results.")


def find_artifacts(project_name: str) -> List[Path]:
    """Find all artifact folders in a project."""
    artifact_root_path = Path(config.PROJECTS_DIR) / project_name / "artifacts"
    logger.debug("Checking project for artifacts: %s", project_name)
    artifact_folders = [
        path
        for path in artifact_root_path.glob("**")
        if (path / "stdout").is_file()
    ]
    logger.debug(
        "Found %s artifacts for project: %s",
        len(artifact_folders),
        project_name,
    )
    return artifact_folders


@projects_group.command("report")
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
def report_artifacts(project_name: str, last: Optional[int]) -> None:
    """Display the last x reports for a given project."""
    logger.info(
        "Command: report, User: %s, Artifacts dir: %s",
        getpass.getuser(),
        project_name,
    )
    artifact_folders = find_artifacts(project_name)
    artifact_folders = utils.sort_and_limit_artifacts(artifact_folders, last)

    if not artifact_folders:
        click.echo("No artifacts found.")
        return
    for artifact_path in artifact_folders:
        utils.display_artifact_report(artifact_path)


@projects_group.command("lint")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=utils.project_name_validation_callback,
)
@click.argument("playbook_file", type=click.Path(exists=False), default="")
@click.option(
    "-v",
    "--verbosity",
    default=0,
    type=int,
    help="Increase the verbosity of the output.",
)
def lint(project_name: str, playbook_file: str, verbosity: int) -> None:
    """Lint Project playbooks using ansible-lint."""
    logger.info(
        "Command: lint, User: %s, Project name: %s",
        getpass.getuser(),
        project_name,
    )
    if not linter.ansible_lint_accessible():
        click.echo("ansible-lint is not installed.")
        return

    if playbook_file:
        click.echo(f"Linting '{playbook_file}'...")
        result = linter.lint_playbook_or_project(
            project_name, playbook_file, verbosity
        )
        if result:
            click.echo(
                f"Error linting playbook '{playbook_file}': "
                f"{str(result).strip()}"
            )
            return
    else:
        click.echo(f"Linting all playbooks in project '{project_name}'...")
        result = linter.lint_playbook_or_project(
            project_name=project_name, playbook_file=None, verbosity=verbosity
        )
        if result:
            click.echo(
                f"Error linting project {project_name}: {str(result).strip()}"
            )
            return
    click.echo("Done linting.")
