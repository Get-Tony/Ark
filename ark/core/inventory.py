"""Ark - Ansible Inventory Management."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import csv
import logging
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Union

from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader

from ark.settings import config

logger = logging.getLogger(__name__)


def get_host(project_name: str, host_name: str) -> Union[Host, None]:
    """
    Get a host from a project.

    Args:
        project_name (str): Project name.
        host_name (str): Host name.

    Returns:
        Union[Host, None]: Host object or None if the host does not exist.
    """
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[
            str(Path(config.PROJECTS_DIR) / project_name / "inventory"),
        ],
    )
    return inventory.get_host(host_name)


def get_project_hosts(target_project: str) -> list[Host]:
    """
    Get all hosts in a project.

    Args:
        target_project (str): Project name.

    Returns:
        list[Host]: List of hosts.
    """
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
    """
    Get all groups a host is a member of.

    Args:
        host (Host): Host object.

    Returns:
        list[str]: List of groups.
    """
    groups = []
    for group in host.groups:
        groups.append(group.name)
    return groups


def get_group(project_name: str, group_name: str) -> Union[Group, None]:
    """
    Get a group from a project.

    Args:
        project_name (str): Project name.
        group_name (str): Group name.

    Returns:
        Union[Group, None]: Group object or None if the group does not exist.
    """
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[str(Path(config.PROJECTS_DIR) / project_name / "inventory")],
    )
    return inventory.groups.get(group_name)


def get_hosts_for_group(group: Group) -> list[Union[Host, None]]:
    """
    Get all hosts in a group.

    Args:
        group (Group): Group object.

    Returns:
        list[Union[Host, None]]: List of hosts.
    """
    host_list: list[Union[Host, None]] = []
    host_list = group.get_hosts()
    return host_list


def get_all_groups(project_name: str) -> dict[str, Group]:
    """
    Get all groups in a project's inventory.

    Args:
        project_name (str): Project name.

    Returns:
        dict[str, Group]: Dictionary of groups.
    """
    data_loader = DataLoader()
    inventory = InventoryManager(
        loader=data_loader,
        sources=[str(Path(config.PROJECTS_DIR) / project_name / "inventory")],
    )
    groups: dict[str, Group] = inventory.groups
    return groups


def check_host_resolution(
    host: str, dns_servers: List[str], timeout: int
) -> List[str]:
    """
    Check if a host can be resolved by a list of DNS servers.

    Args:
        host (str): Host name.
        dns_servers (List[str]): List of DNS servers.
        timeout (int): Timeout in seconds.

    Returns:
        List[str]: List of DNS servers that could not resolve the host.
    """
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
    """
    Check if all hosts in a project can be resolved by a list of DNS servers.

    Args:
        dns_servers (Optional[list[str]], optional): List of DNS servers.
            Defaults to None.
        timeout (int, optional): Timeout in seconds. Defaults to 5.
        output (Optional[str], optional): Output format. Defaults to None.

    Returns:
        Optional[list[dict[str, str]]]: List of hosts that could not be
            resolved.
    """
    if not dns_servers:
        dns_servers = config.DNS_SERVERS.split(",")
    else:
        dns_servers = list(dns_servers)

    hosts = get_project_hosts(project_name)

    results = []
    for host in hosts:
        hostname = host.get_name()
        if not hostname:
            logger.error("Host '%s' has no name", host)
            continue
        try:
            missing_servers = check_host_resolution(
                hostname, dns_servers, timeout
            )
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
        ) as timeout_error:
            logger.error("Error: '%s'", timeout_error, exc_info=True)
            continue
        except ValueError as value_error:
            logger.error("Error: '%s'", value_error, exc_info=True)
            continue

        if missing_servers:
            results.append([host, ", ".join(missing_servers)])

    if output:
        try:
            with open(
                output, "w", newline="", encoding=config.ENCODING
            ) as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Hostname", "Unresolvable from"])
                writer.writerows(results)
        except FileNotFoundError as file_error:
            logger.critical(
                "Error: File not found - '%s'", file_error, exc_info=True
            )
        except PermissionError as perm_error:
            logger.critical(
                "Error: Permission denied - '%s'", perm_error, exc_info=True
            )
    else:
        unresolvable_hosts: list[dict[str, Any]] = []
        for host, missing_servers in results:
            unresolvable_hosts.append(
                {"Hostname": host, "Unresolvable from": missing_servers}
            )
            logger.error(
                "Host '%s' is not resolvable by DNS servers: %s",
                host,
                missing_servers,
            )
        return unresolvable_hosts

    return None
