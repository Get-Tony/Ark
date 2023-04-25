"""Ark - Ansible Facts."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from ark import utils
from ark.database import get_session, init_db
from ark.models.facts import AnsibleHostFacts
from ark.settings import config

logger = logging.getLogger(__name__)


init_db()


def find_caches(target_dir: Optional[str] = None) -> list[Path]:
    """
    Find all fact cache directories.

    Args:
        target_dir (Optional[str], optional): Target directory.
            Defaults to None.

    Returns:
        list[Path]: List of fact cache directories.
    """
    if target_dir:
        projects_path = Path(target_dir).resolve()
    else:
        projects_path = Path(config.PROJECTS_DIR).resolve()

    logger.info("Loading facts from: '%s'", projects_path)
    cache_list = [
        cache_path
        for cache_path in projects_path.glob("**/fact_cache")
        if cache_path.is_dir()
    ]
    return cache_list


def load_cache_dirs(
    fact_cache_paths: list[Path],
) -> dict[str, AnsibleHostFacts]:
    """
    Load all fact cache directories.

    Args:
        fact_cache_paths (list[Path]): List of fact cache directories.

    Returns:
        dict[str, AnsibleHostFacts]: Dictionary of AnsibleHostFacts objects.
    """

    def create_ansible_host_facts(host_fact_path: Path) -> AnsibleHostFacts:
        """Create AnsibleHostFacts object."""
        hostname = host_fact_path.name.replace(" ", "_").lower()
        logger.debug(
            "Loading facts for '%s' from '%s'", hostname, host_fact_path
        )
        host_facts = json.loads(host_fact_path.read_text())
        new_entry: AnsibleHostFacts = AnsibleHostFacts.from_json(
            json.dumps(host_facts)
        )

        return new_entry

    host_facts = {}
    for fact_cache_path in fact_cache_paths:
        for host_fact_path in fact_cache_path.iterdir():
            if host_fact_path.is_file():
                hostname = host_fact_path.name.replace(" ", "_").lower()
                host_facts[hostname] = create_ansible_host_facts(
                    host_fact_path
                )

    logger.info("Found facts for: '%s' hosts.", len(host_facts))
    logger.debug("Hosts: '%s'", list(host_facts))
    return host_facts


def merge_and_compare_facts(
    existing_facts: str, new_facts: str
) -> Tuple[bool, str]:
    """
    Merge and compare facts.

    Args:
        existing_facts (str): Existing facts.
        new_facts (str): New facts.

    Returns:
        Tuple[bool, str]: _description_
    """
    existing_facts_dict = json.loads(existing_facts)
    new_facts_dict = json.loads(new_facts)
    merged_facts = existing_facts_dict.copy()
    merged_facts.update(new_facts_dict)
    merged_facts_str = json.dumps(merged_facts)
    equality_check: bool = existing_facts_dict == new_facts_dict
    return equality_check, merged_facts_str


@get_session
def store_facts(
    host_facts: Dict[str, AnsibleHostFacts], session: Optional[Session] = None
) -> list[str]:
    """
    Store facts in the database.

    Args:
        host_facts (Dict[str, AnsibleHostFacts]): Host facts.
        session (Optional[Session], optional): Database session.
            Defaults to None.

    Raises:
        ValueError: Session is required.
        integrity_error: Unknown IntegrityError occurred.

    Returns:
        list[str]: List of updated hosts.
    """
    if not session:
        raise ValueError("Session is required.")

    updated_hosts = []
    for host in host_facts.values():
        existing_host = (
            session.query(AnsibleHostFacts).filter_by(fqdn=host.fqdn).first()
        )
        if existing_host:
            equality_check, merged_facts_str = merge_and_compare_facts(
                existing_host.facts, host.facts
            )

            if not equality_check:
                existing_host.facts = merged_facts_str
                existing_host.last_modified = host.last_modified
                updated_hosts.append(host.fqdn)
        else:
            new_host = AnsibleHostFacts.from_json(
                facts_json=host.facts,
            )
            session.add(new_host)
            updated_hosts.append(host.fqdn)
        try:
            session.commit()
        except IntegrityError as integrity_error:
            session.rollback()
            if "unique constraint" in str(integrity_error).lower():
                logger.error(
                    "Host '%s' already exists in the database. : %s",
                    host.fqdn,
                    str(integrity_error),
                )
                continue
            logger.critical(
                "An unknown IntegrityError occurred while processing "
                "host '%s'. "
                "Error: %s",
                host.fqdn,
                str(integrity_error),
            )
            raise integrity_error
    if updated_hosts:
        logger.info("Updated facts for hosts: '%s'", updated_hosts)
    else:
        logger.info("No facts were updated.")
    return updated_hosts


@get_session
def query_host_facts(
    fqdn: str,
    fact_key: Optional[str] = None,
    fuzzy: bool = False,
    session: Optional[Session] = None,
) -> Generator[Tuple[str, Any], None, None]:
    """
    Query host facts.

    Args:
        fqdn (str): Fully qualified domain name.
        fact_key (Optional[str], optional): Ansible fact key.
            Defaults to None.
        fuzzy (bool, optional): Fuzzy match fact key. Defaults to False.
        session (Optional[Session], optional): Database session.
            Defaults to None.

    Raises:
        ValueError: Session is required.

    Yields:
        Generator[Tuple[str, Any], None, None]: Fact key and value.
    """
    if not session:
        raise ValueError("Session is required.")

    host: Optional[AnsibleHostFacts] = (
        session.query(AnsibleHostFacts).filter_by(fqdn=fqdn).first()
    )
    if not host:
        logger.error("Host '%s' not found.", fqdn)
        return
    logger.info("Querying Host: '%s'", host.fqdn)
    facts = json.loads(host.facts)
    logger.debug("Fact count: '%s'", len(facts))
    if fact_key:
        found = False
        if not fuzzy:
            for key, value in facts.items():
                if key.lower() == fact_key.lower():
                    logger.info("Matched '%s' to '%s'.", fact_key, key)
                    found = True
                    yield key, value
        else:
            for key, value in facts.items():
                if utils.fuzzy_match_strings(fact_key, key):
                    logger.info("Matched '%s' to '%s'.", fact_key, key)
                    found = True
                    yield key, value
        if not found:
            logger.warning(
                "Fact key '%s' not found for host '%s'.", fact_key, fqdn
            )
        return
    logger.info("Returning all facts.")
    for key, value in facts.items():
        yield key, value


@get_session
def query_hosts_by_fact(
    fact_key: str,
    fact_value: Any,
    fuzzy: bool = False,
    session: Optional[Session] = None,
) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """
    Query hosts by fact.

    Args:
        fact_key (str): Fact key.
        fact_value (Any): Fact value.
        fuzzy (bool, optional): Fuzzy match fact key. Defaults to False.
        session (Optional[Session], optional): Database session.
            Defaults to None.

    Raises:
        ValueError: Session is required.

    Yields:
        Generator[Tuple[str, Dict[str, Any]], None, None]: Host and facts.
    """
    if not session:
        raise ValueError("Session is required.")

    hosts = session.query(AnsibleHostFacts).all()

    def match_fact_pairs(
        fact_key: str,
        fact_value: Any,
        key: str,
        value: Any,
        fuzzy: bool = False,
    ) -> Optional[Any]:
        """Match a fact key and value to a fact key and value."""
        fact_value_str = str(fact_value)
        match: bool = (
            utils.fuzzy_match_strings(fact_key, key)
            if fuzzy
            else fact_key.lower() == key.lower()
        )
        if match:
            if isinstance(value, list):
                for item in value:
                    if fact_value_str in str(item):
                        logger.debug("Matched '%s' to '%s'.", fact_key, key)
                        return item
            elif fact_value_str in str(value):
                logger.debug("Matched '%s' to '%s'.", fact_key, key)
                return value
        return None

    for host in hosts:
        facts = json.loads(host.facts)
        matching_facts = {
            key: match
            for key, value in facts.items()
            if (
                match := match_fact_pairs(
                    fact_key, fact_value, key, value, fuzzy
                )
            )
            is not None
        }

        if matching_facts:
            yield host.fqdn, matching_facts


@get_session
def remove_host(fqdn: str, session: Optional[Session] = None) -> bool:
    """
    Remove a host from the database.

    Args:
        fqdn (str): Fully qualified domain name.
        session (Optional[Session], optional): Database session.
            Defaults to None.

    Raises:
        ValueError: Session is required.

    Returns:
        bool: True if host was removed, False otherwise.
    """
    if not session:
        raise ValueError("Session is required.")

    host = session.query(AnsibleHostFacts).filter_by(fqdn=fqdn).first()

    if not host:
        logger.warning("Host '%s' not found.", fqdn)
        return False

    session.delete(host)
    session.commit()

    logger.info("Removed host '%s' from the database.", fqdn)
    return True


@get_session
def get_all_hosts(session: Optional[Session] = None) -> list[AnsibleHostFacts]:
    """
    Get all hosts from the database.

    Args:
        session (Optional[Session], optional): Database session.
            Defaults to None.

    Raises:
        ValueError: Session is required.

    Returns:
        list[AnsibleHostFacts]: List of AnsibleHostFacts objects.
    """
    if not session:
        raise ValueError("Session is required.")

    hosts = session.query(AnsibleHostFacts).all()

    if not hosts:
        logger.warning("No hosts found in the database.")
        return []

    return hosts
