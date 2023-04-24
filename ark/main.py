"""Ark - Main Entry Point."""

import logging
from pathlib import Path

import click

from ark.cli import (
    cron_group,
    facts_group,
    inventory_group,
    lint_command,
    report_command,
    run_command,
)
from ark.database import init_db
from ark.log_setup import init_logging
from ark.settings import config


@click.group()
@click.version_option()
def ark_cli() -> None:
    """Ark - Streamline Your Ansible Workflow."""


def main() -> None:
    """Ark main entry point."""
    init_logging(
        console_log_level=config.CONSOLE_LOG_LEVEL,
        file_log_level=config.FILE_LOG_LEVEL,
        log_dir=str(Path(config.PROJECTS_DIR) / "logs"),
    )
    logger = logging.getLogger(__name__)
    logger.info("Ark loaded.")
    logger.debug("Debug mode enabled.")
    logger.debug("Ark settings: '%s'", config.json(indent=4))

    # Add subcommands
    ark_cli.add_command(run_command)
    ark_cli.add_command(lint_command)
    ark_cli.add_command(report_command)
    ark_cli.add_command(facts_group)
    ark_cli.add_command(inventory_group)
    ark_cli.add_command(cron_group)

    # Initialize the database
    init_db()

    # Run the CLI
    ark_cli()


if __name__ == "__main__":
    main()
