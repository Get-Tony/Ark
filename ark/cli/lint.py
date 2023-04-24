"""Ark - Project Commands."""

import logging

import click

from ark import utils
from ark.core import linter

from .call_logger import log_command_call

logger = logging.getLogger(__name__)


@click.command("lint")
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
@log_command_call()
def lint_command(
    project_name: str, playbook_file: str, verbosity: int
) -> None:
    """Lint Project playbooks using ansible-lint."""
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
