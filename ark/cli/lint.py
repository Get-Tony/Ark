"""Ark - Ansible Linting Commands."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from typing import Any

import click

from ark.core import lint

from .utilities import log_command_call, project_name_validation_callback

logger = logging.getLogger(__name__)


def print_lint_results(result: dict[str, Any], verbose: bool = False) -> None:
    """
    Print lint results.

    Args:
        result (dict[str, Any]): Lint results.
        verbose (bool, optional): Print verbose output. Defaults to False.
    """
    if verbose:
        click.echo("Error(s) found:")
        for lint_result in result["lint_results"]:
            click.echo(
                "".join(
                    [
                        f"    {lint_result['match']} "
                        f"(Line {lint_result['linenumber']}): ",
                        lint_result["details"].replace("\n", "\n    "),
                    ]
                )
            )
    click.echo("Rule Violation Summary")
    click.echo("count  tag          profile rule associated tags")
    click.echo("------------------------------------------------")
    for summary_item in result["summary"]:
        click.echo(
            f"{summary_item['count']:<6} {summary_item['tag']:<12} "
            f"{summary_item['profile']:<6} "
            f"{summary_item['rule_associated_tags']:<14}"
        )


@click.command("lint")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=project_name_validation_callback,
)
@click.argument("playbook", type=click.Path(exists=False), default="")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Display verbose output.",
)
@log_command_call()
def lint_command(project_name: str, playbook: str, verbose: bool) -> None:
    """
    Lint playbooks in a project.

    Args:
        project_name (str): Project name.
        playbook (str): Playbook name.
        verbose (bool): Print verbose output.
    """
    if playbook:
        click.echo(f"Linting '{playbook}'...")
        result = lint.lint_single_playbook(project_name, playbook, verbose)
        if result:
            print_lint_results(result, verbose)
    else:
        click.echo(f"Linting all playbooks in project '{project_name}'...")
        results = lint.lint_all_playbooks(project_name, verbose)
        for playbook_, result in results:
            click.echo(
                f"\nLinting playbook '{playbook_}' in project "
                f"'{project_name}'..."
            )
            if result:
                print_lint_results(result, verbose)
            else:
                click.echo(f"No issues found in playbook '{playbook_}'.")
    click.echo("Done linting.")
