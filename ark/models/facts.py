"""Ark - Ansible Host Facts."""

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, String


class AnsibleHostFacts(SQLModel, table=True):
    """Ansible Host Facts Model."""

    id: int = Field(default=None, primary_key=True)
    hostname: str = Field(
        sa_column=Column(String(255), unique=True), index=True
    )

    fqdn: str = Field(sa_column=Column(String(255), unique=True), index=True)

    distribution: str = Field(sa_column=Column(String, nullable=True))
    distribution_version: str = Field(sa_column=Column(String, nullable=True))
    os_family: str = Field(sa_column=Column(String, nullable=True))
    kernel: str = Field(sa_column=Column(String, nullable=True))
    architecture: str = Field(sa_column=Column(String, nullable=True))
    default_ipv4: str = Field(sa_column=Column(String, nullable=True))
    default_ipv6: str = Field(sa_column=Column(String, nullable=True))
    facts: str = Field(sa_column=Column(String, nullable=False))
    last_modified: datetime = Field(
        sa_column=Column(DateTime, nullable=False, default=datetime.now)
    )

    @classmethod
    def from_json(
        cls, facts_json: str, hostname: Optional[str] = None
    ) -> "AnsibleHostFacts":
        """
        Create a new AnsibleHostFacts object from a JSON string.

        Args:
            facts_json (str): JSON string containing Ansible facts.
            hostname (Optional[str], optional): Override Hostname to use.
                Defaults to None.

        Returns:
            AnsibleHostFacts: New AnsibleHostFacts object.
        """
        facts = json.loads(facts_json)

        return cls(
            hostname=hostname or facts.get("ansible_hostname"),
            fqdn=facts.get("ansible_fqdn"),
            distribution=facts.get("ansible_distribution"),
            distribution_version=facts.get("ansible_distribution_version"),
            os_family=facts.get("ansible_os_family"),
            kernel=facts.get("ansible_kernel"),
            architecture=facts.get("ansible_architecture"),
            default_ipv4=facts.get("ansible_default_ipv4", {}).get("address"),
            default_ipv6=facts.get("ansible_default_ipv6", {}).get("address"),
            last_modified=datetime.now(),
            facts=facts_json,
        )
