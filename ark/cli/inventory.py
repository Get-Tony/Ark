"""Ark - Inventory Commands."""

import getpass
import logging
from typing import Union

import click
from ansible.inventory.host import Host
from tabulate import tabulate

from ark.core import inventory
from ark.settings import config

logger = logging.getLogger(__name__)


@click.group("inventory")
def inventory_group() -> None:
    """Ansible Inventory operations."""


@inventory_group.command("host-groups")
@click.argument("target_project", callback=inventory.validate_inventory_dir)
@click.argument("target_host")
def get_host_groups(target_project: str, target_host: str) -> None:
    """Display all groups a host is a member of."""
    logger.info(
        "Command: get_host_groups, User: %s, Hostname: %s",
        getpass.getuser(),
        target_host,
    )
    host = inventory.get_host(target_project, target_host)

    if not host:
        click.echo(f"Host '{target_host}' not found in the inventory.")
        return

    groups = inventory.get_groups_for_host(host)
    inventory.display_groups(target_host, groups)


@inventory_group.command("list-members")
@click.argument("target_project", callback=inventory.validate_inventory_dir)
@click.argument("target_group", required=False, default=None)
def get_group_members(target_project: str, target_group: str) -> None:
    """Display all hosts in a group.

    If no group is specified, display all groups and their members.
    """
    logger.info(
        "Command: get_group_hosts, User: %s, Group: %s",
        getpass.getuser(),
        target_group,
    )

    if not target_group:
        click.echo("All groups in the inventory:")
        groups = inventory.get_all_groups(target_project)
        for group in groups:
            click.echo(f"[{group}]")
            hosts = inventory.get_hosts_for_group(groups[group])
            for host in hosts:
                click.echo(f"{host}")
            click.echo()
        return

    host_group = inventory.get_group(target_project, target_group)

    if not host_group:
        click.echo(f"Group '{target_group}' not found in the inventory.")
        return
    click.echo(f"[{target_group}]")
    group_hosts: list[Union[Host, None]] = inventory.get_hosts_for_group(
        host_group
    )
    for host in group_hosts:
        click.echo(f"{host}")


@inventory_group.command("check-dns")
@click.argument(
    "target_project",
    callback=inventory.validate_inventory_dir,
    required=True,
)
@click.option("--dns-servers", multiple=True, required=False, default=None)
@click.option("--timeout", required=False, default=5)
@click.option("--outfile", required=False, default=None)
def check_dns(
    target_project: str, dns_servers: tuple[str], timeout: int, outfile: str
) -> None:
    """Check if all hosts in the inventory have a valid DNS entry."""
    logger.info(
        "Command: check_dns, User: %s, Project: %s",
        getpass.getuser(),
        target_project,
    )
    hosts = inventory.check_project_resolution(
        target_project, list(dns_servers), timeout, outfile
    )
    if hosts:
        click.echo(
            "The following hosts are not resolvable with the following "
            "DNS targets:"
        )
        table_data = [
            {
                "Hostname": host.get("Hostname"),
                "No resolution": host.get("No resolution"),
            }
            for host in hosts
        ]
        click.echo(
            tabulate(table_data, headers="keys", tablefmt=config.TABLE_FORMAT)
        )
