"""Ark - Ansible Facts Collector."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Tuple

from sqlmodel import Session

from ark import utils
from ark.database import get_session
from ark.models.facts import AnsibleHostFacts
from ark.settings import config

logger = logging.getLogger(__name__)


def compare_json_facts(existing_facts: str, new_facts: str) -> bool:
    """Compare existing facts to new facts."""
    existing_facts_dict = json.loads(existing_facts)
    new_facts_dict = json.loads(new_facts)
    equality_check: bool = existing_facts_dict == new_facts_dict
    return equality_check


def find_caches(projects_dir: Optional[utils.PathLike] = None) -> list[Path]:
    """Find all fact caches in the projects directory."""
    projects_path = Path(projects_dir or config.PROJECTS_DIR).resolve()
    logger.info("Loading facts from: %s", projects_path)
    project_paths = [
        path
        for path in projects_path.iterdir()
        if path.is_dir()
        if "logs" not in path.parts
    ]
    logger.debug("Found %s projects", len(project_paths))
    return [
        path
        for project_path in project_paths
        for path in project_path.glob("artifacts/*/fact_cache")
    ]


def load_cache_dirs(
    fact_cache_paths: list[Path],
) -> dict[str, AnsibleHostFacts]:
    """Load facts from fact cache directories."""
    logger.debug("Loading facts from: %s", fact_cache_paths)
    host_facts = {
        host_fact_path.stem: AnsibleHostFacts(
            hostname=host_fact_path.stem.replace(" ", "_").lower(),
            facts=json.dumps(
                json.loads(utils.read_file_contents(host_fact_path) or "{}")
            ),
            last_modified=datetime.fromtimestamp(
                host_fact_path.stat().st_mtime
            ),
        )
        for fact_cache_path in fact_cache_paths
        for host_fact_path in fact_cache_path.iterdir()
        if host_fact_path.is_file()
    }
    logger.debug("Found facts for: %s", list(host_facts.keys()))
    return host_facts


def match_fact_pairs(
    fact_key: str, fact_value: Any, key: str, value: Any
) -> Optional[Any]:
    """Match a fact key and value to a fact key and value."""
    if fact_key.lower() in key.lower():
        if isinstance(value, list):
            for item in value:
                if str(fact_value) in str(item):
                    return item
        elif str(fact_value) in str(value):
            return value
    return None


@get_session
def store_facts(
    host_facts: Dict[str, AnsibleHostFacts], session: Optional[Session] = None
) -> list[str]:
    """Store facts in the database."""
    if not session:
        raise ValueError("Session is required.")

    updated_hosts = []
    for host in host_facts.values():
        hostname = host.hostname
        last_modified = host.last_modified
        facts = host.facts
        existing_host = (
            session.query(AnsibleHostFacts)
            .filter_by(hostname=hostname)
            .first()
        )
        if existing_host:
            if not compare_json_facts(existing_host.facts, facts):
                existing_host.facts = facts
                existing_host.last_modified = last_modified
                updated_hosts.append(hostname)
        else:
            new_host = AnsibleHostFacts(
                hostname=hostname,
                facts=facts,
                last_modified=last_modified,
            )
            session.add(new_host)
            updated_hosts.append(hostname)
    session.commit()
    return updated_hosts


@get_session
def query_host_facts(
    hostname: str,
    fact_key: Optional[str] = None,
    session: Optional[Session] = None,
) -> Generator[Tuple[str, Any], None, None]:
    """Query host facts from the database."""
    if not session:
        raise ValueError("Session is required.")

    host = session.query(AnsibleHostFacts).filter_by(hostname=hostname).first()

    if not host:
        logger.debug("Host '%s' not found.", hostname)
        return
    facts = json.loads(host.facts)
    if fact_key:
        found = False
        for key, value in facts.items():
            if fact_key.lower() in key.lower():
                yield key, value
                found = True
        if not found:
            logger.debug(
                "Fact key '%s' not found for host '%s'.", fact_key, hostname
            )
        return
    for key, value in facts.items():
        yield key, value


@get_session
def query_hosts_by_fact(
    fact_key: str, fact_value: Any, session: Optional[Session] = None
) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """Query hosts by fact from the database."""
    if not session:
        raise ValueError("Session is required.")

    hosts = session.query(AnsibleHostFacts).all()

    for host in hosts:
        facts = json.loads(host.facts)
        matching_facts = {
            key: match
            for key, value in facts.items()
            if (match := match_fact_pairs(fact_key, fact_value, key, value))
            is not None
        }

        if matching_facts:
            yield host.hostname, matching_facts


@get_session
def remove_host(hostname: str, session: Optional[Session] = None) -> bool:
    """Remove host from the database."""
    if not session:
        raise ValueError("Session is required.")

    host = session.query(AnsibleHostFacts).filter_by(hostname=hostname).first()

    if not host:
        logger.debug("Host '%s' not found.", hostname)
        return False

    session.delete(host)
    session.commit()

    logger.debug("Removed host '%s' from the database.", hostname)
    return True


@get_session
def list_hosts(session: Optional[Session] = None) -> list[str]:
    """List all hosts in the database."""
    if not session:
        raise ValueError("Session is required.")

    hosts = session.query(AnsibleHostFacts).all()

    if not hosts:
        return []

    return [host.hostname for host in hosts]
