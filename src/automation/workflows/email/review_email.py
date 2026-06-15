"""
ReviewEmailWorkflow - Handles the interactive email review workflow.

Responsibilities:
- Pull emails from session review state
- Coordinate interactive review loop via TUI display
- Transition emails to queued (approve), drafts (reject), or leave in review (skip)
"""

from typing import Tuple
from src.automation.session_state import SessionState
from src.TUI.display.email_review import (
    display_review_header,
    display_review_footer,
    display_email_for_review,
    prompt_review_action,
    display_action_result,
)


class ReviewEmailWorkflow:

    @staticmethod
    def run(session: SessionState, count: int) -> Tuple[int, int, int]:
        """
        Execute the interactive review loop for up to `count` emails.

        Args:
            session: SessionState instance holding review emails
            count: Max number of emails to review in this session

        Returns:
            Tuple of (approved, rejected, skipped) counts
        """
        emails_to_review = list(session.review.items())[:count]
        total = len(emails_to_review)

        if total == 0:
            print("No emails in review queue.")
            return (0, 0, 0)

        display_review_header(total)

        approved = rejected = skipped = 0

        for idx, (email_addr, email_dict) in enumerate(emails_to_review, start=1):
            display_email_for_review(idx, total, email_dict)
            action = prompt_review_action()

            if action == 'a':
                session.move_to_queue(email_addr)
                approved += 1
            elif action == 'r':
                session.move_to_drafts(email_addr)
                rejected += 1
            else:
                skipped += 1

            display_action_result(action, email_addr)

        display_review_footer(approved, rejected, skipped)
        return (approved, rejected, skipped)
