"""Ark - Ansible Linting Commands."""
__author__ = "Anthony Pagan <Get-Tony@outlook.com>"

import logging

import click

from ark.core import linter

from .cli_utils import log_command_call, project_name_validation_callback

logger = logging.getLogger(__name__)


@click.command("lint")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=project_name_validation_callback,
)
@click.argument("playbook_file", type=click.Path(exists=False), default="")
@click.option(
    "-v",
    "--verbosity",
    default=0,
    type=int,
    help="Increase the verbosity of the output.",
)
@log_command_call()
def lint_command(
    project_name: str, playbook_file: str, verbosity: int
) -> None:
    """
    Lint an Ansible playbook or project.

    Args:
        project_name (str): Project name.
        playbook_file (str): Playbook file.
        verbosity (int): Verbosity level.
    """
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
