"""
Session State Management for Cold Email Automation

This module manages temporary storage for email workflows during a session.
Emails are stored in three states: DRAFT, REVIEW, QUEUED.

The session state is automatically persisted to disk and loaded on initialization.
"""

import json
from pathlib import Path
from typing import Dict, Any
from functools import wraps


def auto_save(method):
    """
    Decorator to automatically save session state after any modification.

    Usage:
        @auto_save
        def some_method(self):
            # modify state
            pass
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self._save_to_cache()
        return result
    return wrapper


class SessionState:
    """
    Manages local draft, review, and queued email states with automatic persistence.

    Data structure:
        All data follows the same hashing pattern:
        email_address : { Dict }

        Where email_address is the key to identify entries, and the value contains metadata:
        {
            'to': 'recruiter@company.com',
            'subject': 'Interest in Backend Role',
            'body': 'Dear ...',
            'resume': 'path/to/resume.pdf'
        }
    """

    CACHE_FILE = Path("MCPServer/email_session.json")

    def __init__(self):
        """Initialize session state and load from cache if available."""
        self.drafts: Dict[str, Dict[str, Any]] = {}
        self.review: Dict[str, Dict[str, Any]] = {}
        self.queued: Dict[str, Dict[str, Any]] = {}
        self.email_service: Any = None
        self._load_from_cache()

    def add_gmail_service(self, gmail_service: Any) -> None:
        """
        Store the authenticated Gmail service for persistence across the app.

        Args:
            gmail_service: Authenticated Gmail API service object from authenticate_gmail()
        """
        self.email_service = gmail_service 

    def _load_from_cache(self):
        """Load session state from cache file if it exists."""
        if self.CACHE_FILE.exists():
            data = json.loads(self.CACHE_FILE.read_text())
            self.drafts = data.get('drafts', {})
            self.review = data.get('review', {})
            self.queued = data.get('queued', {})

    def _save_to_cache(self):
        """Save current session state to cache file."""
        data = {
            'drafts': self.drafts,
            'review': self.review,
            'queued': self.queued
        }
        self.CACHE_FILE.write_text(json.dumps(data, indent=2))

    @auto_save
    def add_draft(self, draft: Dict[str, Any]) -> bool:
        """
        Add an email draft to the session.

        Args:
            draft: Dictionary containing email data with structure:
                {
                    'to': 'recruiter@company.com',
                    'subject': 'Interest in Backend Role',
                    'body': 'Dear ...',
                    'resume_path': 'path/to/resume.pdf',
                    'resume_type': 'Backend',
                    'raw_html': ''
                }

        Returns:
            True if successfully added, False otherwise
        """
        try:
            email_key = draft.get('to')
            if not email_key:
                print("Error: Draft missing 'to' field")
                return False

            self.drafts[email_key] = draft
            return True
        except Exception as e:
            print(f"Error adding draft: {str(e)}")
            return False

    @auto_save
    def remove_draft(self, email: str) -> bool:
        """
        Remove a draft by email address.

        Args:
            email: Email address key to remove

        Returns:
            True if successfully removed, False otherwise
        """
        try:
            if email not in self.drafts:
                print(f"Error: Email '{email}' not found in drafts")
                return False
            del self.drafts[email]
            return True
        except Exception as e:
            print(f"Error removing draft: {str(e)}")
            return False

    @auto_save
    def move_to_review(self, email: str) -> bool:
        """
        Move an email from drafts to review state.

        Args:
            email: Email address key to move

        Returns:
            True if successfully moved, False otherwise
        """
        try:
            if email not in self.drafts:
                print(f"Error: Email '{email}' not found in drafts")
                return False

            # Move from drafts to review
            self.review[email] = self.drafts[email]
            del self.drafts[email]
            return True
        except Exception as e:
            print(f"Error moving to review: {str(e)}")
            return False

    @auto_save
    def move_to_queue(self, email: str) -> bool:
        """
        Move an email from review to queued state.

        Args:
            email: Email address key to move

        Returns:
            True if successfully moved, False otherwise
        """
        try:
            if email not in self.review:
                print(f"Error: Email '{email}' not found in review")
                return False
            self.queued[email] = self.review[email]
            del self.review[email]
            return True
        except Exception as e:
            print(f"Error moving to queue: {str(e)}")
            return False

    @auto_save
    def move_to_drafts(self, email: str) -> bool:
        """
        Move an email from review back to drafts for regeneration.

        Args:
            email: Email address key to move

        Returns:
            True if successfully moved, False otherwise
        """
        try:
            if email not in self.review:
                print(f"Error: Email '{email}' not found in review")
                return False
            self.drafts[email] = self.review[email]
            del self.review[email]
            return True
        except Exception as e:
            print(f"Error moving to drafts: {str(e)}")
            return False

    @auto_save
    def clear_session(self):
        """Clear all session state (drafts, review, queued) and persist to cache."""
        self.drafts = {}
        self.review = {}
        self.queued = {}

    def get_stats(self) -> Dict[str, int]:
        """
        Get current session statistics.

        Returns:
            Dictionary with counts for each state
        """
        return {
            'drafts': len(self.drafts),
            'review': len(self.review),
            'queued': len(self.queued)
        }
