"""Ark - Ansible Linting."""
__author__ = "Anthony Pagan <get-tony@outlook.com>"

import logging
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ansiblelint.constants import DEFAULT_RULESDIR
from ansiblelint.errors import MatchError
from ansiblelint.rules import RulesCollection
from ansiblelint.runner import Runner

from ark.core.run import find_playbooks, get_playbook_path

logger = logging.getLogger(__name__)


def generate_summary_and_stats(matches: List[MatchError]) -> Dict[str, Any]:
    """
    Generate summary and stats from lint matches.

    Args:
        matches (List[MatchError]): Lint matches.

    Returns:
        Dict[str, Any]: Summary and stats.
    """
    stats: Counter[Any] = Counter()
    for match in matches:
        stats[match.rule] += 1

    summary = []

    for rule, count in stats.items():
        summary.append(
            {
                "count": count,
                "tag": rule.id,
                "profile": rule.shortdesc,
                "rule_associated_tags": ",".join(rule.tags),
            }
        )

    return {"summary": summary}


def lint_playbook(
    playbook: Path, verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Lint a playbook.

    Args:
        playbook (Path): Path to playbook.
        verbose (bool, optional): Print verbose output. Defaults to False.

    Returns:
        Optional[Dict[str, Any]]: Lint results.
    """
    logger.info("Linting playbook: '%s'", str(playbook).strip())

    # Load default Ansible lint rules
    rules = RulesCollection(rulesdirs=[DEFAULT_RULESDIR])

    # Create a Runner instance with the playbook and rules
    runner = Runner(str(playbook), rules=rules)

    # Run linting on the playbook
    matches = runner.run()

    result = {}
    logger.debug("Raw lint results: %s", matches)
    if matches:
        lint_results = []
        if verbose:
            for match in matches:
                lint_results.append(
                    {
                        "match": str(match),
                        "linenumber": match.linenumber,
                        "details": match.details,
                    }
                )
        result["lint_results"] = lint_results
        summary = generate_summary_and_stats(matches)
        result["summary"] = summary["summary"]
        return result
    logger.info("No issues found")
    return None


def lint_single_playbook(
    project_name: str, playbook_file: str, verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Lint a single playbook.

    Args:
        project_name (str): Project name.
        playbook_file (str): Playbook file name.
        verbose (bool, optional): Print verbose output. Defaults to False.

    Returns:
        Optional[Dict[str, Any]]: Lint results.
    """
    lint_target = get_playbook_path(project_name, playbook_file)
    if not lint_target:
        logger.critical("Could not find lint target '%s'", playbook_file)
        return None
    return lint_playbook(lint_target, verbose)


def lint_all_playbooks(
    project_name: str, verbose: bool = False
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Lint all playbooks in a project.

    Args:
        project_name (str): Project name.
        verbose (bool, optional): Print verbose output. Defaults to False.

    Returns:
        List[Tuple[str, Dict[str, Any]]]: Lint results.
    """
    playbooks = find_playbooks(project_name)
    results: List[Tuple[str, Dict[str, Any]]] = []

    if not playbooks:
        logger.critical("No playbooks found in project '%s'", project_name)
        return results

    for playbook in playbooks:
        lint_target = get_playbook_path(project_name, playbook)
        if lint_target:
            result = lint_playbook(lint_target, verbose)
            if result:
                results.append((playbook, result))
            else:
                logger.info("No issues found in playbook '%s'.", playbook)
        else:
            logger.error(
                "Failed to lint playbook '%s', continuing with the "
                "next playbook...",
                playbook,
            )

    return results
