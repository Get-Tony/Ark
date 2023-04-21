"""Ark - Ansible Facts Models."""

from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, String


class AnsibleHostFacts(SQLModel, table=True):
    """Ansible Host Facts Model."""

    id: int = Field(default=None, primary_key=True)
    hostname: str = Field(
        sa_column=Column(String(255), unique=True), index=True
    )
    facts: str = Field(sa_column=Column(String, nullable=True))
    last_modified: datetime = Field(
        sa_column=Column(DateTime, nullable=False, default=datetime.now)
    )
