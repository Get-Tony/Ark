"""Ark - Ansible Facts Commands."""

import ast
import getpass
import json
import logging
from typing import Any, Optional

import click

from ark import utils
from ark.core import facts
from ark.settings import config

logger = logging.getLogger(__name__)


@click.group("facts")
def facts_group() -> None:
    """Ansible Facts operations."""


@facts_group.command()
@click.option(
    "-d",
    "--directory",
    default=config.PROJECTS_DIR,
    help="Directory to search for facts.",
)
def collect(directory: Optional[str]) -> None:
    """Collect facts from the specified directory."""
    logger.info(
        "Command: collect, User: %s, Directory: %s",
        getpass.getuser(),
        directory,
    )
    fact_cache_paths = facts.find_caches(projects_dir=directory)
    host_facts = facts.load_cache_dirs(fact_cache_paths)
    updated_hosts = facts.store_facts(host_facts)

    if updated_hosts:
        click.echo(f"Collected facts from {directory}:")
        for hostname in updated_hosts:
            click.echo(f"  {hostname}")
    else:
        click.echo(f"No new or modified facts found in {directory}.")
    logger.debug("Command finished: collect")


@facts_group.command()
@click.argument("hostname")
@click.argument("fact-key", default=None, required=False)
@click.option("--page", is_flag=True, help="Page the output.")
def query(
    hostname: str, fact_key: Optional[str], page: Optional[bool]
) -> None:
    """Query facts for a specific host."""
    logger.info(
        "Command: query, User: %s, Hostname: %s",
        getpass.getuser(),
        hostname,
    )
    output = "\n".join(
        f"{key}: {value}"
        for key, value in facts.query_host_facts(hostname, fact_key)
    )
    utils.echo_or_page(output, page)
    logger.debug("Command finished: query")


@facts_group.command()
@click.argument("fact_key")
@click.argument("fact_value")
@click.option("--page", is_flag=True, help="Page the output.")
def find(fact_key: str, fact_value: str, page: Optional[bool]) -> None:
    """Find all hosts with a given key, value pair."""
    logger.info(
        "Command: find, User: %s, Fact key: %s, Fact value: %s",
        getpass.getuser(),
        fact_key,
        fact_value,
    )
    try:
        fact_value = ast.literal_eval(fact_value)
    except (ValueError, SyntaxError):
        pass  # Leaving fact_value as a string if it cannot be converted
    hosts: list[tuple[str, dict[str, Any]]] = list(
        facts.query_hosts_by_fact(fact_key, fact_value)
    )
    if len(hosts) == 0:
        click.echo(
            f"No hosts found with '{fact_key}' containing '{fact_value}'."
        )
        logger.debug("Command finished: find")
        return
    output_lines = []
    output_lines.append(f"Hosts with '{fact_key}' containing '{fact_value}':")
    for hostname, fact_data in hosts:
        output_lines.append(f"  Hostname: {hostname}")
        output_lines.append("  Matching Fact(s):")
        output_lines.append(json.dumps(fact_data, indent=4))
    output = "\n".join(output_lines)

    utils.echo_or_page(output, page)
    logger.debug("Command finished: find")


@facts_group.command()
@click.argument("hostname")
def remove(hostname: str) -> None:
    """Remove a host entry from the database."""
    logger.info(
        "Command: remove, User: %s, Hostname: %s",
        getpass.getuser(),
        hostname,
    )
    success = facts.remove_host(hostname)

    if success:
        click.echo(f"Removed host '{hostname}' from the database.")
    else:
        click.echo(f"Host '{hostname}' not found in the database.")
    logger.debug("Command finished: remove")


@facts_group.command()
@click.option("--page", is_flag=True, help="Page the output.")
def list_hosts(page: Optional[bool]) -> None:
    """List all hosts in the database."""
    logger.info(
        "Command: list_hosts, User: %s",
        getpass.getuser(),
    )
    logger.debug("Command called: list_hosts")
    hosts = facts.list_hosts()
    if not hosts:
        click.echo(f"No hosts found with session: {config.DB_URL}")
        logger.debug("Command finished: list_hosts")
        return
    output = "\n".join(f"  {host}" for host in hosts)
    utils.echo_or_page(output, page)
    logger.debug("Command finished: list_hosts")
