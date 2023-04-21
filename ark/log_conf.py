"""Ark - Logging Configuration."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def init_logging(
    log_dir: Optional[str] = None,
    log_level: str = "WARNING",
    backup_count: int = 5,
    max_bytes: int = 15 * 1024 * 1024,
    encoding: str = "utf-8",
) -> None:
    """
    Initialize logging.

    Logging to file is optional.
            If log_dir is not specified, logging to file is disabled.

    Args:
        log_dir (str, optional): Directory to store log files.
                Defaults to None.
        log_level (str, optional): Log level.
                Defaults to "INFO".
        backup_count (int, optional): Number of log files to keep.
                Defaults to 5.
        max_bytes (int, optional): Maximum size of log file.
                Defaults to 15MB.
        encoding (str, optional): Log file encoding.
                Defaults to "utf-8".
    """
    valid_level: int = getattr(
        logging, log_level.strip().upper(), logging.ERROR
    )

    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger()
    logger.setLevel(valid_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "ark.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
            delay=False,
        )
        file_handler.setFormatter(log_formatter)

        logger.addHandler(file_handler)
