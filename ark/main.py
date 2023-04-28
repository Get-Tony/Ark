"""Ark."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from pathlib import Path

from ark.cli import ark_cli
from ark.logger_config import init_logging
from ark.settings import config


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
        logger.debug("Ark settings: '%s'", config.json(indent=4))

    # Start CLI
    ark_cli()


if __name__ == "__main__":
    main()
