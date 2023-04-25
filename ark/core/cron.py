"""Ark - Cronjob."""

import logging
from typing import List, Optional

from crontab import CronItem, CronTab

from ark.settings import config

logger = logging.getLogger(__name__)


def create_cronjob(
    project_name: str,
    playbook: str,
    loop: str = "hourly",
    hourly_minute: int = 30,
    daily_hour: int = 4,
) -> Optional[CronItem]:
    """
    Create a new cronjob.

    Args:
        project_name (str): Project name.
        playbook (str): Playbook name.
        loop (str, optional): Either 'hourly' or 'daily'. Defaults to "hourly".
        hourly_minute (int, optional): Which minute of the hour to run the
            cronjob. Defaults to 30.
        daily_hour (int, optional): Which hour of the day to run the cronjob.
            Defaults to 4.

    Raises:
        ValueError: Loop value is not 'hourly' or 'daily'.
        ValueError: Hourly minute is not between 0 and 59.
        ValueError: Daily hour is not between 0 and 23.

    Returns:
        Optional[CronItem]: CronItem object or None if a similar cronjob
            already exists.
    """
    if loop not in ["hourly", "daily"]:
        raise ValueError(
            "Invalid loop value. Choose either 'hourly' or 'daily'."
        )
    if loop == "hourly" and (hourly_minute < 0 or hourly_minute > 59):
        raise ValueError("Invalid minute value. Choose between 0 and 59.")
    if loop == "daily" and (daily_hour < 0 or daily_hour > 23):
        raise ValueError("Invalid hour value. Choose between 0 and 23.")

    cron = CronTab(user=True)

    # Check if a similar cron job already exists
    command = f"{config.RUN_SCRIPT} {project_name} {playbook}"
    schedule = (
        f"{hourly_minute} * * * *"
        if loop == "hourly"
        else f"00 {daily_hour} * * *"
    )
    existing_jobs = [
        job
        for job in cron.find_command(command)
        if str(job.schedule) == schedule
    ]

    if existing_jobs:
        logger.error("A similar cron job already exists. Skipping creation.")
        logger.debug("Existing cron job(s): '%s'", existing_jobs)
        return None

    # Create the new cron job
    job = cron.new(command=command)
    job.setall(schedule)
    job.set_comment(config.CRONJOB_TAG + project_name)
    cron.write()
    logger.info(
        "Added cron job for project '%s' with playbook '%s'",
        project_name,
        playbook,
    )
    logger.debug("Added cron job: '%s'", job)
    return job


def list_ark_cronjobs() -> List[CronItem]:
    """
    List all Ark-managed cronjobs.

    Returns:
        List[CronItem]: List of CronItem objects.
    """
    cron = CronTab(user=True)
    logger.debug("Listing all cron jobs")
    ark_jobs = [
        job for job in cron if job.comment.startswith(config.CRONJOB_TAG)
    ]
    logger.debug("Found '%s' cron job(s).", len(ark_jobs))
    return ark_jobs


def find_cronjobs(pattern: str) -> List[CronItem]:
    """
    Find Ark-managed cronjobs containing the pattern.

    Args:
        pattern (str): Pattern to search for.

    Returns:
        List[CronItem]: List of CronItem objects.
    """
    cron = CronTab(user=True)
    return [
        job
        for job in cron
        if job.comment.startswith(config.CRONJOB_TAG)
        and pattern.lower() in job.comment.lower()
    ]


def remove_cronjob(pattern: str) -> None:
    """
    Remove a cronjob.

    Args:
        pattern (str): Pattern to search for.
    """
    cron = CronTab(user=True)
    matched_jobs = find_cronjobs(pattern)
    for job in matched_jobs:
        cron.remove(job)
    cron.write()
    logger.info(
        "Removed cron job(s) matching pattern '%s' from comment", pattern
    )
    logger.debug("Removed cron job(s): '%s'", matched_jobs)


def remove_all_cronjobs(project_name: Optional[str] = None) -> None:
    """
    Remove all Ark-managed cronjobs.

    Args:
        project_name (Optional[str], optional): Project name.
            Defaults to None.
    """
    cron = CronTab(user=True)
    if not project_name:
        current_jobs = [
            job for job in cron if job.comment.startswith(config.CRONJOB_TAG)
        ]
        for job in current_jobs:
            cron.remove(job)
        logger.info("Removed all Ark-managed cron jobs")
        logger.debug("Removed cron job(s): '%s'", current_jobs)
    else:
        current_jobs = [
            job
            for job in cron
            if job.comment.startswith(config.CRONJOB_TAG + project_name)
        ]
        cron.remove_all(comment=config.CRONJOB_TAG + project_name)
        logger.info("Removed cron job(s) for project '%s'", project_name)
        logger.debug("Removed cron job(s): '%s'", current_jobs)

    cron.write()
