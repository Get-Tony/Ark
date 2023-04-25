"""Ark - Reporting."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ark.settings import config
from ark.utils import read_file_contents

logger = logging.getLogger(__name__)


def sort_and_limit_artifacts(
    artifact_folders: List[Path], last: Optional[int]
) -> List[Path]:
    """
    Sort and limit the number of artifacts to display.

    Args:
        artifact_folders (List[Path]): List of artifact folders.
        last (Optional[int]): The number of artifacts to display.
            Returns all artifacts if None.

    Returns:
        List[Path]: The sorted and limited list of artifact folders.
    """
    logger.debug("Sorting and limiting artifacts")
    artifact_folders.sort(
        key=lambda folder: folder.stat().st_mtime, reverse=True
    )

    if 0 < last < len(artifact_folders) if last is not None else False:
        artifact_folders = artifact_folders[:last]
    logger.debug("Artifacts: %s", artifact_folders)
    return artifact_folders


def extract_play_recaps(content: str) -> List[str]:
    """
    Extract the play recaps from the content.

    Args:
        content (str): The content to extract the play recaps from.

    Returns:
        List[str]: The list of play recaps.
    """
    play_recap_regex = re.compile(
        r"PLAY RECAP\s+\*+\s+(?P<recap>.*?)(\n\n|$)", re.DOTALL
    )
    play_recaps = play_recap_regex.findall(content)
    if not play_recaps:
        logger.warning("Could not find play recap.")
        return []
    return [recap_tuple[0] for recap_tuple in play_recaps]


def get_artifact_timestamp(stdout_path: Path) -> str:
    """
    Get the timestamp of the artifact.

    Args:
        stdout_path (Path): The path to the stdout file.

    Returns:
        str: The timestamp of the artifact.
    """
    mod_time = stdout_path.stat().st_mtime
    time_stamp = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
    return time_stamp


def extract_playbook_name_from_file(file_path: str) -> Optional[str]:
    """
    Extract the playbook name from the file.

    Args:
        file_path (str): The path to the file.

    Returns:
        Optional[str]: The playbook name or None if it could not be found.
    """
    file_ = Path(file_path)
    logger.debug("Extracting playbook name from file: '%s'", file_)
    if not file_.exists():
        logger.warning("File does not exist: '%s'", file_)
        return None

    content = read_file_contents(file_)
    if not content:
        logger.warning("Could not read file: '%s'", file_)
        return None

    data = json.loads(content)
    command_string = " ".join(data["command"])
    match = re.search(
        r"project/([\w-]+\.yml)",
        command_string,
    )

    if match:
        logger.debug("Extracted playbook name: '%s'", match.group(1))
        return match.group(1)
    logger.warning("Could not extract playbook name from file: '%s'", file_)
    return None


def extract_host_stats(recap: str) -> dict[str, dict[str, int]]:
    """
    Extract the host stats from the recap.

    Args:
        recap (str): The recap to extract the host stats from.

    Returns:
        dict[str, dict[str, int]]: The host stats.
    """
    lines = recap.strip().split("\n")
    host_stats = {}

    for line in lines:
        host, stats = line.strip().split(":", 1)
        stats_dict = {}
        for stat in stats.strip().split(" "):
            if "=" in stat:
                key_, value_ = stat.split("=")
                stats_dict[key_] = int(value_)
        host_stats[host.strip()] = stats_dict

    return host_stats


def find_artifacts(project_name: str) -> List[Path]:
    """
    Find the artifacts for the project.

    Args:
        project_name (str): The name of the project.

    Returns:
        List[Path]: The list of artifact folders.
    """
    artifact_root_path = Path(config.PROJECTS_DIR) / project_name / "artifacts"
    logger.debug(
        "Checking project for artifact directories: '%s'", project_name
    )
    artifact_folders = [
        path
        for path in artifact_root_path.glob("**")
        if (path / "stdout").is_file()
    ]
    logger.debug(
        "Found '%s' artifact directories for project: '%s'",
        len(artifact_folders),
        project_name,
    )
    return artifact_folders
