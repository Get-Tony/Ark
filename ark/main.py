"""Ark - Main Module."""

import logging
from pathlib import Path

import click

from ark.cli.cron import cron_group
from ark.cli.facts import facts_group
from ark.cli.inventory import inventory_group
from ark.cli.projects import projects_group
from ark.database import init_db
from ark.log_conf import init_logging
from ark.settings import config

logger = logging.getLogger(__name__)


@click.group()
def ark_cli() -> None:
    """Ark - Command Line Interface."""


def main() -> None:
    """Ark main entry point."""
    init_logging(
        console_log_level=config.CONSOLE_LOG_LEVEL,
        file_log_level=config.FILE_LOG_LEVEL,
        log_dir=str(Path(config.PROJECTS_DIR) / "logs"),
    )
    init_db()
    logger.info("Ark loaded.")
    if (
        config.CONSOLE_LOG_LEVEL.strip().upper() == "DEBUG"
        or config.FILE_LOG_LEVEL.strip().upper() == "DEBUG"
    ):
        logger.debug("Debug mode enabled.")
        logger.debug("Ark settings: %s", config.json(indent=2))
    ark_cli()


# Add subcommands
ark_cli.add_command(projects_group)
ark_cli.add_command(facts_group)
ark_cli.add_command(inventory_group)
ark_cli.add_command(cron_group)


if __name__ == "__main__":
    main()
