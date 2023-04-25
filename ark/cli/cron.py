"""Ark - Cronjob Commands."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from typing import Optional

import click

from ark.core import cron

from .utilities import log_command_call

logger = logging.getLogger(__name__)


@click.group("cron")
def cron_group() -> None:
    """Cron job management."""


@cron_group.command("add")
@click.argument("project_name", type=str)
@click.argument("playbook", type=str)
@click.option(
    "--loop", type=click.Choice(["hourly", "daily"]), default="hourly"
)
@click.option(
    "--hourly_minute",
    type=int,
    default=30,
    help="Minute to run hourly cron jobs (0-59).",
)
@click.option(
    "--daily_hour",
    type=int,
    default=4,
    help="Hour to run daily cron jobs (0-23).",
)
@log_command_call()
def add_cron_job(
    project_name: str,
    playbook: str,
    loop: str,
    hourly_minute: int,
    daily_hour: int,
) -> None:
    """
    Add a new Ark-managed cron job.

    Args:
        project_name (str): Project name.
        playbook (str): Playbook name.
        loop (str): Either 'hourly' or 'daily'. Defaults to "hourly".
        hourly_minute (int): Which minute of the hour to run the cronjob.
            Defaults to 30.
        daily_hour (int): Which hour of the day to run the cronjob.
            Defaults to 4.
    """
    new_job = cron.create_cronjob(
        project_name=project_name,
        playbook=playbook,
        loop=loop,
        hourly_minute=hourly_minute,
        daily_hour=daily_hour,
    )
    if new_job is None:
        click.echo(f"Not creating. Similar job already exists: {new_job}")
    else:
        click.echo(f"Created new cron job: {new_job}")


@cron_group.command("list")
@log_command_call()
def list_cron_jobs() -> None:
    """List all Ark-managed cron jobs."""
    click.echo("Ark-managed cron jobs:")
    for job in cron.list_ark_cronjobs():
        click.echo(f" - {job}")


@cron_group.command("remove")
@click.argument("pattern", type=str)
@click.option("--force", is_flag=True, help="Skip confirmation prompt.")
@log_command_call()
def remove_cron_job(pattern: str, force: bool) -> None:
    """
    Remove all Ark-managed cron jobs matching a pattern.

    Args:
        pattern (str): Pattern to match.
        force (bool): Skip confirmation prompt.
    """
    if not force:
        click.echo("Ark-managed cron jobs:")
        for job in cron.list_ark_cronjobs():
            click.echo(f" - {job}")
        if not click.confirm(
            f"Are you sure you want to remove all cron jobs "
            f"matching pattern '{pattern}'?"
        ):
            click.echo("Cancelled.")
            return
    cron.remove_cronjob(pattern=pattern)
    click.echo(f"Removed all cron jobs matching pattern '{pattern}'.")


@cron_group.command("wipe")
@click.argument("project_name", type=str, default=None, required=False)
@click.option("--force", is_flag=True, help="Skip confirmation prompt.")
@log_command_call()
def wipe_cron_jobs(project_name: Optional[str], force: bool) -> None:
    """
    Remove all Ark-managed cron jobs.

    Args:
        project_name (Optional[str]): Project name.
        force (bool): Skip confirmation prompt.
    """
    if not force:
        click.echo("Ark-managed cron jobs:")
        for job in cron.list_ark_cronjobs():
            click.echo(f" - {job}")
        if not click.confirm(
            "Are you sure you want to remove all Ark-managed cron jobs?"
        ):
            click.echo("Cancelled.")
            return
    if not project_name:
        click.echo("Removing all Ark-managed cron jobs.")
        cron.remove_all_cronjobs()
    else:
        click.echo(
            f"Removing all Ark-managed cron jobs for project '{project_name}'."
        )
        cron.remove_all_cronjobs(project_name=project_name)
    click.echo("Done.")
