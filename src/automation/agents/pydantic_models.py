from pydantic import BaseModel, Field
from typing import Literal


class ResumeSelection(BaseModel):
    """Model for resume selection agent output."""
    resume_type: Literal['Backend', 'Fullstack', 'AI Engineer', 'Solutions', 'Machine Learning'] = Field(
        description="The most appropriate resume type for the company"
    )
    reasoning: str


class EmailDraft(BaseModel):
    """Model for email draft agent output. Contains bare minimum for review and Gmail API sending."""

    to: str = Field(
        description="Recipient email address"
    )
    subject: str = Field(
        description="Email subject line"
    )
    body: str = Field(
        description="Full email body text in plain text format"
    )
    raw_html: str = Field(
        description="Full email body in HTML format (for future use, can be empty for now)"
    )
