"""Ark."""
__author__ = "Anthony Pagan <Get-Tony@outlook.com>"

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
from ark.logger_config import init_logging
from ark.settings import config


@click.group()
@click.version_option()
def ark_cli() -> None:
    """Ark - Streamline Your Ansible Workflow."""


def main() -> None:
    """Ark - Main entry point."""
    init_logging(
        console_log_level=config.CONSOLE_LOG_LEVEL,
        file_log_level=config.FILE_LOG_LEVEL,
        log_dir=Path(config.PROJECTS_DIR) / "logs",
    )
    logger = logging.getLogger(__name__)
    logger.info("Ark loaded.")
    if any(
        [
            logging.getLevelName(config.CONSOLE_LOG_LEVEL.strip().upper())
            == logging.DEBUG,
            logging.getLevelName(config.FILE_LOG_LEVEL.strip().upper())
            == logging.DEBUG,
        ]
    ):
        logger.warning("Debug mode enabled.")
        logger.warning("Ark settings: '%s'", config.json(indent=4))

    # Add subcommands
    ark_cli.add_command(run_command)
    ark_cli.add_command(lint_command)
    ark_cli.add_command(report_command)
    ark_cli.add_command(facts_group)
    ark_cli.add_command(inventory_group)
    ark_cli.add_command(cron_group)

    # Run the CLI
    ark_cli()


if __name__ == "__main__":
    main()
