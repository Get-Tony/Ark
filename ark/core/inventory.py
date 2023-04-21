"""Ark - Ansible Inventory Management."""

import csv
import logging
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Union

import click
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

from ark.settings import config

logger = logging.getLogger(__name__)


def get_host(target_project: str, target_host: str) -> Union[Host, None]:
    """Get a host from the inventory."""
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[
            str(Path(config.PROJECTS_DIR) / target_project / "inventory"),
        ],
    )
    return inventory.get_host(target_host)


def get_project_hosts(target_project: str) -> list[Host]:
    """Get all hosts in a project."""
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[
            str(Path(config.PROJECTS_DIR) / target_project / "inventory"),
        ],
    )
    hosts = sorted(
        inventory.get_hosts(),
        key=lambda host: host.name,  # type: ignore
    )
    return hosts


def get_groups_for_host(host: Host) -> list[str]:
    """Get all groups a host is a member of."""
    groups = []
    for group in host.groups:
        groups.append(group.name)
    return groups


def display_groups(target_host: str, groups: list[str]) -> None:
    """Display all groups a host is a member of."""
    click.echo(f"Host '{target_host}' is a member of the following groups:")
    for group in groups:
        click.echo(f"- {group}")


def get_group(target_project: str, target_group: str) -> Union[Group, None]:
    """Get a group from the inventory."""
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[
            str(Path(config.PROJECTS_DIR) / target_project / "inventory")
        ],
    )
    return inventory.groups.get(target_group)


def get_hosts_for_group(group: Group) -> list[Union[Host, None]]:
    """Get all hosts in a group."""
    host_list: list[Union[Host, None]] = []
    host_list = group.get_hosts()
    return host_list


def get_all_groups(target_project: str) -> dict[str, Group]:
    """Get all groups in the inventory."""
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[
            str(Path(config.PROJECTS_DIR) / target_project / "inventory")
        ],
    )
    groups: dict[str, Group] = inventory.groups
    return groups


def display_all_project_groups(target_project: str) -> None:
    """Display all groups in a project inventory."""
    groups = get_all_groups(target_project)
    click.echo(f"Project '{target_project}' contains the following groups:")
    for group in groups:
        click.echo(f"- {group}")


def validate_inventory_dir(
    ctx: click.Context,
    param: click.Parameter,  # pylint: disable=unused-argument
    project_name: str,
) -> str:
    """Check if the inventory directory exists."""
    if not (Path(config.PROJECTS_DIR) / project_name / "inventory").is_dir():
        click.echo(
            f"Inventory directory does not exist for Project: {project_name}"
        )
        ctx.exit(1)
    return project_name


def check_host_resolution(
    host: str, dns_servers: List[str], timeout: int
) -> List[str]:
    """Check if a host is resolvable by a list of DNS servers."""
    missing_servers = []
    for server in dns_servers:
        try:
            resolved = subprocess.run(
                ["nslookup", host, server],
                capture_output=True,
                timeout=timeout,
                check=True,
            )
            if resolved.returncode == 1:
                continue
        except subprocess.TimeoutExpired:
            missing_servers.append(server)
        except subprocess.CalledProcessError:
            missing_servers.append(server)

    return missing_servers


def check_project_resolution(  # pylint: disable=too-many-locals
    project_name: str,
    dns_servers: Optional[list[str]] = None,
    timeout: int = 5,
    output: Optional[str] = None,
) -> Optional[list[dict[str, str]]]:
    """Check Ansible inventory hosts of a project for DNS resolution."""
    if not dns_servers:
        dns_servers = config.DNS_SERVERS.split(",")
    else:
        dns_servers = list(dns_servers)

    hosts = get_project_hosts(project_name)

    results = []
    for host in hosts:
        hostname = host.get_name()
        if not hostname:
            logger.warning("Host '%s' has no name", host)
            continue
        try:
            missing_servers = check_host_resolution(
                hostname, dns_servers, timeout
            )
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
        ) as timeout_error:
            logger.error("Error: %s", timeout_error, exc_info=True)
            continue
        except ValueError as value_error:
            logger.error("Error: %s", value_error, exc_info=True)
            continue

        if missing_servers:
            results.append([host, ", ".join(missing_servers)])

    if output:
        try:
            with open(output, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Hostname", "No resolution with"])
                writer.writerows(results)
        except FileNotFoundError as file_error:
            logger.error(
                "Error: File not found - %s", file_error, exc_info=True
            )
        except PermissionError as perm_error:
            logger.error(
                "Error: Permission denied - %s", perm_error, exc_info=True
            )
    else:
        unresolvable_hosts: list[dict[str, Any]] = []
        for host, missing_servers in results:
            unresolvable_hosts.append(
                {"Hostname": host, "No resolution": missing_servers}
            )
        return unresolvable_hosts
    return None
