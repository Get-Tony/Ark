"""Ark - Logging Configuration."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from ark.settings import config


def init_logging(
    console_log_level: str = config.CONSOLE_LOG_LEVEL,
    file_log_level: str = config.FILE_LOG_LEVEL,
    log_dir: Optional[str] = None,
    backup_count: int = 5,
    max_bytes: int = 15 * 1024 * 1024,
) -> None:
    """
    Initialize logging with separate log levels for console and file logging.

    Logging to file is optional.
            If log_dir is not specified, logging to file is disabled.

    Args:
        console_log_level (str, optional): Log level for console output.
            Defaults to "WARNING".
        file_log_level (str, optional): Log level for file output.
            Defaults to "INFO".
        log_dir (str, optional): Directory to store log files.
            Defaults to None.
        backup_count (int, optional): Number of log files to keep.
            Defaults to 5.
        max_bytes (int, optional): Maximum size of log file.
            Defaults to 15MB.
    """
    valid_console_level: int = getattr(
        logging, console_log_level.strip().upper(), logging.WARNING
    )
    valid_file_level: int = getattr(
        logging, file_log_level.strip().upper(), logging.INFO
    )

    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
    )

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(valid_console_level)
    logger.addHandler(console_handler)

    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "ark.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=config.ENCODING,
            delay=False,
        )
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(valid_file_level)

        logger.addHandler(file_handler)
