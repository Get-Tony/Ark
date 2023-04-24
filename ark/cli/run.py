"""Ark - Project Commands."""

import logging
from pathlib import Path

import click

from ark import utils
from ark.core import runner
from ark.settings import config

from .call_logger import log_command_call

logger = logging.getLogger(__name__)


@click.command("run")
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
@log_command_call()
def run_command(  # pylint: disable=too-many-arguments
    project_name: str,
    playbook_file: str,
    rotate_artifacts: int,
    limit: str,
    extra_vars: str,
    verbosity: int,
) -> None:
    """Run a Project playbook."""
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
