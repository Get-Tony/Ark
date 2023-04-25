"""Ark - Reporting Commands."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from pathlib import Path
from typing import Optional

import click
from tabulate import tabulate

from ark.core import report
from ark.settings import config
from ark.utils import read_file_contents

from .utilities import log_command_call, project_name_validation_callback

logger = logging.getLogger(__name__)


def display_artifact_report(artifact_path: Path) -> None:
    """
    Display a report for a given artifact.

    Args:
        artifact_path (Path): Path to the artifact.
    """
    stdout_path: Path = artifact_path / "stdout"

    content = read_file_contents(stdout_path) or ""

    play_recaps = report.extract_play_recaps(content)
    timestamp = report.get_artifact_timestamp(stdout_path)
    playbook_name = report.extract_playbook_name_from_file(
        str(artifact_path / "command")
    )

    click.echo(f"Report for {artifact_path}:")
    click.echo(f"{playbook_name or 'Playbook'} completed at: {timestamp}")

    headers = ["Host", "ok", "changed", "unreachable", "failed", "skipped"]
    rows = []

    for recap in play_recaps:
        host_stats = report.extract_host_stats(recap)
        for host, stats in host_stats.items():
            row = [
                host,
                stats.get("ok", 0),
                stats.get("changed", 0),
                stats.get("unreachable", 0),
                stats.get("failed", 0),
                stats.get("skipped", 0),
            ]
            rows.append(row)

    table = tabulate(rows, headers=headers, tablefmt=config.TABLE_FORMAT)
    click.echo(table)
    click.echo("")


@click.command("report")
@click.argument(
    "project_name",
    type=click.Path(exists=False),
    callback=project_name_validation_callback,
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
    """
    Display a report for a given project.

    Args:
        project_name (str): Name of the project.
        last (Optional[int]): Display the last x reports.
    """
    artifact_folders = report.find_artifacts(project_name)
    artifact_folders = report.sort_and_limit_artifacts(artifact_folders, last)

    if not artifact_folders:
        click.echo("No artifacts found.")
        return
    for artifact_path in artifact_folders:
        display_artifact_report(artifact_path)
    if not artifact_folders:
        click.echo("No artifacts found.")
        return
    for artifact_path in artifact_folders:
        display_artifact_report(artifact_path)
