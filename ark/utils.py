"""Ark - Utilities."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import click
from tabulate import tabulate

from ark.settings import config

logger = logging.getLogger(__name__)


# Type alias for paths
PathLike = Union[Path, str]


def echo_or_page(content: str, page: Optional[bool]) -> None:
    """
    Echo content to the terminal or page it.

    Args:
        content (str): Content to echo or page.
        page (Optional[bool]): Pages the output if True.
    """
    if page:
        click.echo_via_pager(content)
    else:
        click.echo(content)


def fuzzy_match_strings(string_a: str, string_b: str) -> bool:
    """
    Fuzzy match two strings.

    Args:
        string_a (str): First string to match.
        string_b (str): Second string to match.

    Returns:
        bool: True if the strings match, False otherwise.
    """
    string_a = string_a.lower()
    string_b = string_b.lower()
    return any(
        [
            string_a in string_b,
            string_b in string_a,
            string_a == string_b,
        ]
    )


def convert_bool_to_str(data: Any) -> Any:
    """Convert boolean values to strings."""
    if isinstance(data, bool):
        return str(data)
    if isinstance(data, list):
        return [convert_bool_to_str(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_bool_to_str(value) for key, value in data.items()}
    return data


def project_name_validation_callback(
    ctx: click.Context,  # pylint: disable=unused-argument
    param: click.Parameter,  # pylint: disable=unused-argument
    project_name: str,
) -> Optional[str]:
    """
    Validate a project.

    Args:
        ctx (click.Context): Click context. Do not modify.
        param (click.Parameter): Click parameter. Do not modify.
        project_name (str): Project name to validate.

    Returns:
        Optional[str]: Validated value or None in case of an error.

    Raises:
        click.BadParameter: Raised if the value is invalid.
    """
    if not project_name:
        raise click.BadParameter("Project name is required.")
    logger.debug(
        "Validating project '%s' for the '%s' command.",
        project_name,
        ctx.info_name,
    )
    missing_objects: Optional[
        dict[str, List[Union[str, Path]]]
    ] = validate_project_dir(str(Path(config.PROJECTS_DIR) / project_name))
    if missing_objects:
        click.echo("Project is missing required files or directories:")
        click.echo(f" Path: {Path(config.PROJECTS_DIR) / project_name}")
        for missing_dir in missing_objects["missing_dirs"]:
            click.echo(f" - directory: {missing_dir}")
        for missing_file in missing_objects["missing_files"]:
            click.echo(f" - file: {missing_file}")
        click.echo("Please resolve the issues above and try again.")
        ctx.abort()
    logger.debug("Project validation complete.")
    return project_name


def read_file_contents(
    filepath: PathLike, encoding: str = config.ENCODING
) -> Union[str, None]:
    """Read the content of a file and return it as a string."""
    filepath = Path(filepath)
    logger.debug("Reading file: '%s'", filepath)
    try:
        with open(filepath, "r", encoding=encoding) as current_file:
            content = current_file.read()
    except UnicodeDecodeError:
        logger.error(
            "Could not read file: %s. Error: UnicodeDecodeError", filepath
        )
        return None
    return content


def write_file_contents(
    filepath: PathLike,
    content: str,
    encoding: str = config.ENCODING,
) -> bool:
    """Write the content to a file."""
    filepath = Path(filepath)
    logger.debug("Writing file: '%s'", filepath)
    try:
        with open(filepath, "w", encoding=encoding) as current_file:
            current_file.write(content)
    except PermissionError as permission_error:
        logger.error(
            "Could not write file: %s. Error: '%s'",
            filepath,
            permission_error,
        )
        return False
    logger.debug("Successfully wrote file: '%s'", filepath)
    return True


def validate_project_dir(
    project_name: str,
) -> Optional[dict[str, List[Union[str, Path]]]]:
    """Check if the current directory is a valid Ansible-Runner input tree."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", Path(project_name).name):
        logger.critical(
            "Project name '%s' is not valid. It must only contain "
            "alphanumeric characters, dashes, and underscores.",
            project_name,
        )
        raise click.BadParameter(
            "Project name is not valid. It must only contain alphanumeric "
            "characters, dashes, and underscores."
        )
    required_dirs = [
        Path(config.PROJECTS_DIR) / project_name / "project",
        Path(config.PROJECTS_DIR) / project_name / "inventory",
        Path(config.PROJECTS_DIR) / project_name / "env",
    ]
    required_files = [
        Path(config.PROJECTS_DIR) / project_name / "project" / "main.yml",
        Path(config.PROJECTS_DIR) / project_name / "env" / "envvars",
        Path(config.PROJECTS_DIR) / project_name / "env" / "ssh_key",
    ]

    logger.info("Checking for required files and directories")

    # Check for required directories
    missing_dirs: List[Union[str, Path]] = []
    for required_dir in required_dirs:
        if not required_dir.is_dir():
            missing_dirs.append(required_dir)
    if missing_dirs:
        logger.critical("Required directories are missing: '%s'", missing_dirs)
    else:
        logger.debug("No missing directories found for: '%s'", project_name)

    # Check for required files
    missing_files: List[Union[str, Path]] = []
    for required_file in required_files:
        if not required_file.is_file():
            missing_files.append(required_file)
    if missing_files:
        logger.critical("Required files are missing: '%s'", missing_files)
    else:
        logger.debug("No missing files found for: '%s'", project_name)

    # Return a report if any directories or files are missing
    if any(missing_dirs or missing_files):
        missing_report: dict[str, List[Union[str, Path]]] = {
            "missing_dirs": missing_dirs,
            "missing_files": missing_files,
        }
        return missing_report
    return None


def find_playbooks(project_name: str) -> List[str]:
    """Find all YAML or YML playbooks in the project directory."""
    logger.debug("Finding playbooks for: '%s'", project_name)
    playbooks: List[str] = []
    for playbook in (
        Path(config.PROJECTS_DIR) / project_name / "project"
    ).glob("*.yml"):
        playbooks.append(playbook.name)
    for playbook in (
        Path(config.PROJECTS_DIR) / project_name / "project"
    ).glob("*.yaml"):
        playbooks.append(playbook.name)
    logger.debug(
        "Found playbooks for %s: '%s'", project_name, playbooks or "None"
    )
    return playbooks


def get_playbook_path(project_name: str, playbook_file: str) -> Optional[Path]:
    """Get the path to the playbook file."""

    playbook_path: Path = (
        Path(config.PROJECTS_DIR) / project_name / "project" / playbook_file
    )
    if not playbook_path.is_file():
        logger.error(
            "Playbook '%s' does not exist for Project: '%s'",
            playbook_file,
            project_name,
        )
        return None
    logger.debug("Found playbook: '%s'", playbook_path)
    return playbook_path


def sort_and_limit_artifacts(
    artifact_folders: List[Path], last: Optional[int]
) -> List[Path]:
    """Sort artifacts by timestamp and limit to the last N artifacts."""
    artifact_folders.sort(
        key=lambda folder: folder.stat().st_mtime, reverse=True
    )

    if 0 < last < len(artifact_folders) if last is not None else False:
        artifact_folders = artifact_folders[:last]

    return artifact_folders


def extract_playbook_name_from_file(file_path: str) -> Optional[str]:
    """Extract the playbook name from the command file."""
    file_ = Path(file_path)

    if not file_.exists():
        return None

    content = read_file_contents(file_)
    if not content:
        return None

    data = json.loads(content)
    command_string = " ".join(data["command"])
    match = re.search(
        r"project/([\w-]+\.yml)",
        command_string,
    )

    if match:
        return match.group(1)
    print("Playbook name not found in the command string.")
    return None


def display_artifact_report(artifact_path: Path) -> None:
    """Display the report for a single artifact folder."""
    stdout_path: Path = artifact_path / "stdout"

    content = read_file_contents(stdout_path) or ""

    play_recaps = extract_play_recaps(content)
    timestamp = get_artifact_timestamp(stdout_path)
    playbook_name = extract_playbook_name_from_file(
        str(artifact_path / "command")
    )

    click.echo(f"Report for {artifact_path}:")
    click.echo(f"{playbook_name or 'Playbook'} completed at: {timestamp}")

    headers = ["Host", "ok", "changed", "unreachable", "failed", "skipped"]
    rows = []

    for recap in play_recaps:
        host_stats = extract_host_stats(recap)
        for host, stats in host_stats.items():
            row = [
                host,
                stats.get("ok", 0),
                stats.get("changed", 0),
                stats.get("unreachable", 0),
                stats.get("failed", 0),
                stats.get("skipped", 0),
            ]
            rows.append(row)

    table = tabulate(rows, headers=headers, tablefmt=config.TABLE_FORMAT)
    click.echo(table)
    click.echo("")


def extract_play_recaps(content: str) -> List[str]:
    """Extract the play recap from the stdout file content."""
    play_recap_regex = re.compile(
        r"PLAY RECAP\s+\*+\s+(?P<recap>.*?)(\n\n|$)", re.DOTALL
    )
    play_recaps = play_recap_regex.findall(content)
    return [recap_tuple[0] for recap_tuple in play_recaps]


def get_artifact_timestamp(stdout_path: Path) -> str:
    """Get the timestamp of the artifact's stdout file."""
    mod_time = stdout_path.stat().st_mtime
    return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")


def extract_host_stats(recap: str) -> dict[str, dict[str, int]]:
    """Extract the host stats from the play recap."""
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
