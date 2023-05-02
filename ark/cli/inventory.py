"""Ark - Ansible Inventory Management Commands."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from pathlib import Path
from typing import Union

import click
from ansible.inventory.host import Host
from tabulate import tabulate

from ark.core import inventory
from ark.settings import config
from ark.utils import get_valid_projects

from .utilities import log_command_call

logger = logging.getLogger(__name__)


def validate_inventory_dir(
    ctx: click.Context,
    param: click.Parameter,  # pylint: disable=unused-argument
    project_name: str,
) -> str:
    """
    Validate that a project's inventory directory exists.

    Args:
        ctx (click.Context): Click context. Do not use.
        param (click.Parameter): Click parameter. Do not use.
        project_name (str): Project name.

    Returns:
        str: Project name.
    """
    if not (Path(config.PROJECTS_DIR) / project_name / "inventory").is_dir():
        click.echo(
            f"Inventory directory does not exist for Project: {project_name}"
        )
        ctx.exit(1)
    return project_name


@click.group("inventory")
def inventory_group() -> None:
    """Ansible Inventory operations."""


@inventory_group.command("host-groups")
@click.argument("project-name", callback=validate_inventory_dir)
@click.argument("inventory-name")
@log_command_call()
def get_host_groups(project_name: str, inventory_name: str) -> None:
    """
    Display all groups a host belongs to.

    Args:
        project_name (str): Project name.
        inventory_name (str): Host name.
    """
    host = inventory.get_host(project_name, inventory_name)
    logger.debug("Host: %s", host)

    if not host:
        click.echo(f"Host '{inventory_name}' not found in the inventory.")
        return

    groups = inventory.get_groups_for_host(host)
    click.echo(f"Host '{inventory_name}' is a member of the following groups:")
    for group in groups:
        click.echo(f"- {group}")
    logger.debug("Groups: %s", groups)


@inventory_group.command("list-hosts")
@click.argument("project_name", callback=validate_inventory_dir)
@click.argument("group_name", required=False, default=None)
@log_command_call()
def get_group_members(project_name: str, group_name: str) -> None:
    """
    Display all hosts in a group.

    Args:
        project_name (str): Project name.
        group_name (str): Group name.
    """
    if not group_name:
        groups = inventory.get_all_groups(project_name)
        for group in groups:
            click.echo(f"[{group}]")
            hosts = inventory.get_hosts_for_group(groups[group])
            for host in hosts:
                click.echo(f"{host}")
            click.echo()
        return

    host_group = inventory.get_group(project_name, group_name)

    if not host_group:
        click.echo(f"Group '{group_name}' not found in the inventory.")
        return
    click.echo(f"[{group_name}]")
    group_hosts: list[Union[Host, None]] = inventory.get_hosts_for_group(
        host_group
    )
    for host in group_hosts:
        click.echo(f"{host}")


@inventory_group.command("check-dns")
@click.argument(
    "project_name",
    default="",
    required=False,
)
@click.argument("host", required=False, default=None)
@click.option("--dns-server", multiple=True, required=False, default=None)
@click.option("--timeout", required=False, default=5)
@log_command_call()
def check_dns(
    project_name: str,
    dns_server: list[str],
    host: str,
    timeout: int,
) -> None:
    """
    Check DNS resolution for all hosts in an inventory.

    Args:
        project_name (str): Project name.
        dns_server (list[str]): List of DNS servers to check.
        host (str): Host to check. If not specified, all hosts will be checked.
        timeout (int): Timeout in seconds.
    """
    known_projects = get_valid_projects()
    if project_name:
        if project_name not in known_projects:
            click.echo(
                f"Project '{project_name}' not found. "
                f"Valid projects are: {', '.join(known_projects)}"
            )
            return
        projects = [project_name]
    else:
        projects = known_projects

    for project in projects:
        hosts = inventory.check_host_resolution(
            project, dns_server, host, timeout
        )
        if hosts:
            click.echo(f"[{project}]")
            table_data = [
                {
                    "Hostname": host.get("Hostname"),
                    "Unresolvable from": host.get("Unresolvable from"),
                }
                for host in hosts
            ]
            click.echo(
                tabulate(
                    table_data, headers="keys", tablefmt=config.TABLE_FORMAT
                )
            )
        click.echo()
