"""Ark - Ansible Facts Commands."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import json
import logging
from pathlib import Path
from typing import Any, Optional

import click
from tabulate import tabulate

from ark.core import facts
from ark.models.facts import AnsibleHostFacts
from ark.settings import config

from .cli_utils import echo_or_page, log_command_call

logger = logging.getLogger(__name__)


@click.group("facts")
def facts_group() -> None:
    """Ansible Facts operations."""


@facts_group.command("collect")
@click.argument(
    "project-name",
    type=str,
    default=None,
    required=False,
)
@log_command_call()
def collect_facts(project_name: Optional[str]) -> None:
    """
    Collect Ansible facts for all hosts in a project.

    Args:
        project_name (Optional[str]): Project name.
    """
    if not project_name:
        project_name = config.PROJECTS_DIR
    else:
        project_path = Path(config.PROJECTS_DIR) / project_name
        if not project_path.is_dir():
            click.echo(
                f"Project '{project_name}' not found in "
                f"'{config.PROJECTS_DIR}'."
            )
            return
        project_name = str(project_path)

    fact_cache_paths = facts.find_caches(target_dir=project_name)
    host_facts = facts.load_cache_dirs(fact_cache_paths)
    updated_hosts = facts.store_facts(host_facts)

    if updated_hosts:
        click.echo(f"Collected facts from {project_name}:")
        for hostname in updated_hosts:
            click.echo(f"  {hostname}")
    else:
        click.echo(f"No new or modified facts found in {project_name}.")


@facts_group.command("query")
@click.argument("fqdn")
@click.argument("fact-key", default=None, required=False)
@click.option("--fuzzy", is_flag=True, help="Fuzzy match the fact key.")
@click.option("--page", is_flag=True, help="Page the output.")
@log_command_call()
def query_host_facts(
    fqdn: str,
    fact_key: Optional[str],
    fuzzy: Optional[bool],
    page: Optional[bool],
) -> None:
    """
    Query facts for a given host.

    Args:
        fqdn (str): Fully qualified domain name.
        fact_key (Optional[str]): Fact key.
        fuzzy (Optional[bool]): Fuzzy match the fact key.
        page (Optional[bool]): Page the output.
    """
    current_facts = list(facts.query_host_facts(fqdn, fact_key, fuzzy))
    if len(current_facts) == 0:
        click.echo(f"No facts found for {fqdn}.")
        logger.info("Command finished: query")
        return

    # Using JSON instead of tabulate for now, since converting
    # ansible_fact nested bool values to strings has proven unreliable.
    output = json.dumps(current_facts, indent=4)

    logger.debug(
        "%s facts for '%s'",
        "Echoing" if not page else "Paging",
        fqdn,
    )
    echo_or_page(output, page=page)


@facts_group.command("find")
@click.argument("fact_key")
@click.argument("fact_value")
@click.option("--fuzzy", is_flag=True, help="Fuzzy match the fact key.")
@click.option("--page", is_flag=True, help="Page the output.")
@log_command_call()
def find_hosts_by_fact(
    fact_key: str, fact_value: str, fuzzy: Optional[bool], page: Optional[bool]
) -> None:
    """
    Find hosts by a given fact key and value.

    Args:
        fact_key (str): Fact key.
        fact_value (str): Fact value.
        fuzzy (Optional[bool]): Fuzzy match the fact key.
        page (Optional[bool]): Page the output.
    """
    hosts: list[tuple[str, dict[str, Any]]] = list(
        facts.query_hosts_by_fact(fact_key, fact_value, fuzzy or False)
    )
    if not hosts:
        logger.info("No hosts found.")
        click.echo(
            f"No hosts found with '{fact_key}' containing '{fact_value}'."
        )
        logger.info("Command finished: find")
        return
    logger.info("Found hosts: %s", hosts)
    table_data = []
    for fqdn, fact_data in hosts:
        fact_data_str = json.dumps(fact_data)
        table_data.append((fqdn, fact_data_str))
    logger.debug("Table data: %s", table_data)
    table = tabulate(
        table_data,
        headers=["FQDN", "Matching Fact(s)"],
        tablefmt=config.TABLE_FORMAT,
        maxcolwidths=[30, 100],
        colalign=["left", "left"],
    )
    output = (
        f"Hosts with key '{fact_key}' containing value "
        f"'{fact_value}':\n{table}"
    )
    echo_or_page(output, page)


@facts_group.command("remove")
@click.argument("ansible_fqdn")
@log_command_call()
def remove_host_from_db(fqdn: str) -> None:
    """
    Remove a host from the database.

    Args:
        fqdn (str): Fully qualified domain name.
    """
    success = facts.remove_host(fqdn)

    if success:
        click.echo(f"Removed host '{fqdn}' from the database.")
    else:
        click.echo(f"Host '{fqdn}' not found in the database.")


@facts_group.command("show-hosts")
@click.option("--page", is_flag=True, help="Page the output.")
@log_command_call()
def show_known_hosts(page: Optional[bool]) -> None:
    """
    Show all known hosts.

    Args:
        page (Optional[bool]): Page the output.
    """
    hosts: list[AnsibleHostFacts] = facts.get_all_hosts()
    if len(hosts) == 0:
        click.echo(f"No hosts found with session: {config.DB_URL}")
        logger.debug("Command finished: show_known_hosts")
        return

    table_data = []
    for host in hosts:
        table_data.append(
            (
                host.id or "-",
                host.hostname or "-",
                host.fqdn or "-",
                host.distribution or "-",
                host.distribution_version or "-",
                host.os_family or "-",
                host.kernel or "-",
                host.architecture or "-",
                host.default_ipv4 or "-",
            )
        )

    table = tabulate(
        table_data,
        headers=[
            "ID",
            "Hostname",
            "FQDN",
            "Distribution",
            "Version",
            "OS Family",
            "Kernel",
            "Architecture",
            "IPv4",
        ],
        tablefmt=config.TABLE_FORMAT,
        colalign=["left" for _ in range(9)],
        maxcolwidths=[5, 40, 40, 20, 20, 20, 40, 20, 20],
    )
    output = f"Known Hosts:\n{table}"
    echo_or_page(output, page)

    logger.info("Found '%s' hosts in the database.", len(hosts))
    logger.debug("Hosts: %s", [host.fqdn for host in hosts])
