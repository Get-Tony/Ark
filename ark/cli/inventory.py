"""Ark - Ansible Inventory Management Commands."""
__author__ = "Anthony Pagan <Get-Tony@outlook.com>"

import logging
from typing import Union

import click
from ansible.inventory.host import Host
from tabulate import tabulate

from ark.core import inventory
from ark.settings import config

from .cli_utils import log_command_call

logger = logging.getLogger(__name__)


@click.group("inventory")
def inventory_group() -> None:
    """Ansible Inventory operations."""


@inventory_group.command("host-groups")
@click.argument("project-name", callback=inventory.validate_inventory_dir)
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
    inventory.display_groups(inventory_name, groups)
    logger.debug("Groups: %s", groups)


@inventory_group.command("list-hosts")
@click.argument("project_name", callback=inventory.validate_inventory_dir)
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
    callback=inventory.validate_inventory_dir,
    required=True,
)
@click.option("--dns-server", multiple=True, required=False, default=None)
@click.option("--timeout", required=False, default=5)
@click.option("--outfile", required=False, default=None)
@log_command_call()
def check_dns(
    project_name: str, dns_server: list[str], timeout: int, outfile: str
) -> None:
    """
    Check DNS resolution for all hosts in an inventory.

    Args:
        project_name (str): Project name.
        dns_server (list[str]): List of DNS servers to check.
        timeout (int): Timeout in seconds.
        outfile (str): Output file.
    """
    hosts = inventory.check_project_resolution(
        project_name, dns_server, timeout, outfile
    )
    if hosts:
        click.echo(
            "The following hosts are not resolvable with the following "
            "DNS targets:"
        )
        table_data = [
            {
                "Hostname": host.get("Hostname"),
                "Unresolvable from": host.get("Unresolvable from"),
            }
            for host in hosts
        ]
        click.echo(
            tabulate(table_data, headers="keys", tablefmt=config.TABLE_FORMAT)
        )
