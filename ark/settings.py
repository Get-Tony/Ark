"""Ark - Settings."""
__author__ = "Anthony Pagan <Get-Tony@outlook.com>"

import logging
import os
import sys
from pathlib import Path

import dotenv
from pydantic import BaseSettings, ValidationError, validator

logger = logging.getLogger(__name__)


def load_env_file(projects_dir: str, file_name: str = ".env") -> None:
    """
    Load environment variables from a file.

    Args:
        projects_dir (str): The projects directory.
        file_name (str, optional): The name of the environment file.
            Defaults to ".env".
    """
    env_file = Path(projects_dir) / file_name
    if env_file.is_file():
        dotenv.load_dotenv(str(env_file))


def get_projects_dir() -> str:
    """
    Check for a projects directory environment variable.

    Custom projects directory can be set with the environment variable
    ARK_PROJECTS_DIR. If not set, the default projects directory is
    $HOME/ark_projects.

    If a defined custom projects directory does not exist,
    Ark will exit with an error.
    """
    default_projects_dir = str(Path.home().resolve() / "ark_projects")
    projects_dir = os.environ.get("ARK_PROJECTS_DIR", default_projects_dir)

    if projects_dir == default_projects_dir:
        if not Path(projects_dir).is_dir():
            print(
                f"Creating default projects directory '{projects_dir}'.",
                file=sys.stderr,
            )
            Path(projects_dir).mkdir(parents=True, exist_ok=True)
    if not Path(projects_dir).is_dir():
        print(
            f"Error: The projects directory '{projects_dir}' does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)
    return projects_dir


class ARKSettings(BaseSettings):  # pylint: disable=too-few-public-methods
    """Ark settings."""

    PROJECTS_DIR: str = get_projects_dir()
    DB_URL: str = f"sqlite:///{Path(PROJECTS_DIR) / 'ark.db'}"
    CONSOLE_LOG_LEVEL: str = "WARNING"
    FILE_LOG_LEVEL: str = "INFO"
    ENCODING: str = "utf-8"
    CRONJOB_TAG: str = "#Ark-"
    RUN_SCRIPT: str = str(Path(PROJECTS_DIR) / "ark_run_script.sh")
    DNS_SERVERS: str = "8.8.8.8"  # Google DNS
    TABLE_FORMAT: str = "psql"

    class Config:  # pylint: disable=too-few-public-methods
        """Ark settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "ARK_"

    @validator("ENCODING", pre=True)
    @classmethod
    def validate_encoding(cls, value: str) -> str:
        """Validate Encoding."""
        try:
            "test".encode(value)
        except LookupError as lookup_error:
            raise ValueError(f"Invalid encoding: {value}") from lookup_error
        return value

    @classmethod
    def load_from_env(cls) -> "ARKSettings":
        """Load settings from environment variables."""
        projects_dir = get_projects_dir()
        load_env_file(projects_dir)

        try:
            loaded_settings = cls()
        except ValidationError as validation_error:
            logger.critical(validation_error)
            sys.exit(1)
        return loaded_settings


config = ARKSettings.load_from_env()
