"""Ark - Command Line Interface."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"


import click

from .cron import cron_group
from .facts import facts_group
from .inventory import inventory_group
from .lint import lint_command
from .report import report_command
from .run import run_command


@click.group()
@click.version_option()
def ark_cli() -> None:
    """Ark - Streamline Your Ansible Workflow."""


# Add subcommands
ark_cli.add_command(run_command)
ark_cli.add_command(lint_command)
ark_cli.add_command(report_command)
ark_cli.add_command(facts_group)
ark_cli.add_command(inventory_group)
ark_cli.add_command(cron_group)
