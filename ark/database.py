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
    """Inject a function with the current database session."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Create a database session and pass it to the function."""
        engine = create_engine(config.DB_URL)
        with Session(engine) as session:
            return func(*args, session=session, **kwargs)

    logger.debug("Injected '%s' with database session.", func.__name__)
    return wrapper


def init_db(
    db_url: str = config.DB_URL,
) -> None:
    """Initiate database tables."""
    logger.info("Initiating database tables.")
    logger.debug("Database URL: %s", db_url)
    if db_url.startswith("sqlite:///"):
        db_file = Path(db_url.replace("sqlite:///", ""))
        db_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        engine = create_engine(db_url)
        SQLModel.metadata.create_all(engine)
    except OperationalError as error:
        logger.critical("Failed to create database tables: %s", error)
        sys.exit(1)
    logger.info("Database initiated.")
