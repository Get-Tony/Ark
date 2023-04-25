"""Ark - Database Session Management."""

import logging
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from ark.settings import config

logger = logging.getLogger(__name__)


def get_session(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Create a database session and pass it to the function.

    Args:
        func (Callable[..., Any]): The function to wrap.

    Returns:
        Callable[..., Any]: The wrapped function.
    """

    @wraps(func)
    def session_manager(*args: Any, **kwargs: Any) -> Any:
        """
        Create a database session and pass it to the function.

        Returns:
            Any: The function return value.
        """
        engine = create_engine(config.DB_URL)
        with Session(engine) as session:
            logger.debug(
                "Binding '%s.%s' to session: %s",
                func.__module__,
                func.__name__,
                session.bind,
            )
            return func(*args, session=session, **kwargs)

    return session_manager


def init_db(
    db_url: str = config.DB_URL,
) -> None:
    """
    Create the database tables.

    Args:
        db_url (str, optional): The database URL. Defaults to config.DB_URL.
    """
    logger.debug("Initiating database tables.")
    logger.debug("Database URL: '%s'", db_url)
    if db_url.startswith("sqlite:///"):
        logger.debug("Using SQLite database.")
        db_file = Path(db_url.replace("sqlite:///", ""))
        logger.debug("Ensuring parent directory exists: '%s'", db_file.parent)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        logger.debug("Creating database engine.")
        engine = create_engine(db_url)
        logger.debug("Creating database tables.")
        SQLModel.metadata.create_all(engine)
    except OperationalError as error:
        logger.critical("Failed to create database tables: '%s'", error)
        sys.exit(1)
    logger.info("Database ready.")
