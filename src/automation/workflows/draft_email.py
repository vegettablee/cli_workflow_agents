"""
DraftEmailWorkflow - Handles the email drafting workflow.

Responsibilities:
- Query database for emails that can be sent
- Find valid emails (company vs recruiter emails)
- Get company/recruiter context for personalization
- Draft personalized emails using AI agents
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Tuple
from db.connection import get_session
from db.queries import find_valid_emails, get_company, get_recruiter, get_recruiter_email
from src.automation.agents.email_personalization import run_draft_agent
from src.automation.agents.resume_selection import run_resume_selection_agent


class DraftEmailWorkflow:
    """
    Workflow class for helping draft personalized cold emails.

    This class coordinates the process of:
    1. Querying the database for valid emails
    2. Separating company emails from recruiter emails
    3. Getting context for personalization
    4. Structuring context for agent 
    """

    def __init__(self, rate_limit: int = 20):
        """
        Initialize the draft email workflow.

        Args:
            rate_limit: Number of emails to draft per batch (default: 20)
        """
        self.rate_limit = rate_limit

    @staticmethod
    def query_database(session) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Query database for all emails that can be sent.

        This only gets run once for a batch of emails.

        Args:
            session: SQLAlchemy session

        Returns:
            Tuple containing:
            - company_emails: List of company email addresses
            - company_ids: List of company IDs for company emails
            - recruiter_emails: List of recruiter email addresses
            - recruiter_company_ids: List of company IDs for recruiter emails
        """
        return find_valid_emails(session)

    @staticmethod
    def find_valid_emails(emails: List[str]) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Takes a list of emails to check and separates them into company vs recruiter emails.

        Args:
            emails: List of email addresses to validate

        Returns:
            Tuple containing:
            - company_emails: List of email addresses tied directly to companies
            - company_ids: List of company IDs from the actual email (for context injection)
            - recruiter_emails: List of recruiter email addresses
            - recruiter_company_ids: List of company IDs tied to the recruiter emails

        Note:
            Since checking if an email exists in the recruiter_email table is a binary operation,
            these can be easily separated. Need to keep track of the IDs for context injection
            later for email personalization and other purposes.
        """
        # TODO: Implement logic to validate emails and separate them
        # This is a placeholder implementation
        pass

    @staticmethod
    def get_company_context(session, company_email: str, company_id: int) -> Dict:
        """
        Get company context for email personalization.

        Uses the company_id to query the company table and pull relevant data.

        Args:
            session: SQLAlchemy session
            company_email: The company email address
            company_id: The company ID to query

        Returns:
            Dictionary with the same fields as the COMPANY entity in the DDL script plus the email
        """
        company_context = get_company(session, company_id)
        # Add the email address to the context
        company_context['email'] = company_email
        return company_context

    @staticmethod
    def get_recruiter_context(session, recruiter_email: str) -> Dict:
        """
        Get recruiter context for email personalization.

        Uses the recruiter_email on the recruiter_emails table to get the recruiter_id and then find the recruiter_id information

        Args:
            session: SQLAlchemy session
            recruiter_email: The recruiter email address

        Returns:
            Dictionary containing recruiter information
        """
        # First get the recruiter_id from the recruiter_email
        recruiter_id = get_recruiter_email(session, recruiter_email)

        if not recruiter_id:
            return None

        # Then get the full recruiter information
        return get_recruiter(session, recruiter_id)

    @staticmethod
    def process_and_add_to_session(
        context: Dict,
        resume_selector_agent: any,
        email_personalization_agent: any,
        session_state: any,
        is_recruiter: bool
    ) -> Tuple[bool, Dict]:
        """
        Process a single email: select resume and draft email.

        This method encapsulates the workflow for a single email:
        1. Select appropriate resume based on context
        2. Generate personalized email draft

        Args:
            context: Context dictionary containing company/recruiter information
            resume_selector_agent: Agent for selecting resume type
            email_personalization_agent: Agent for generating personalized emails
            session_state: SessionState instance (unused, for consistency)
            is_recruiter: True if drafting for recruiter, False if for company

        Returns:
            Tuple of (success: bool, email_dict: Dict or None)
            - success: True if the workflow completed successfully
            - email_dict: The generated email dictionary if successful, None otherwise
        """
        try:
            # Step 1: Select appropriate resume
            success, selected_resume = run_resume_selection_agent(
                context=context,
                agent=resume_selector_agent,
                is_recruiter=is_recruiter
            )

            if not success:
                return (False, None)

            # Step 2: Generate personalized email draft
            draft_success, email_dict = run_draft_agent(
                context=context,
                agent=email_personalization_agent,
                resume_type=selected_resume,
                is_recruiter=is_recruiter
            )

            if not draft_success:
                return (False, None)

            return (True, email_dict)

        except Exception as e:
            print(f"Error in process_and_add_to_session: {str(e)}")
            return (False, None)

    def run(self, count: int = None) -> Dict:
        """
        Execute the draft email workflow.

        Args:
            count: Number of emails to draft (defaults to rate_limit if not specified)

        Returns:
            Dictionary with workflow results:
            {
                'success': bool,
                'drafts_created': int,
                'company_drafts': int,
                'recruiter_drafts': int,
                'error': str | None
            }
        """
        if count is None:
            count = self.rate_limit

        result = {
            'success': False,
            'drafts_created': 0,
            'company_drafts': 0,
            'recruiter_drafts': 0,
            'error': None
        }

        try:
            # TODO: Implement workflow execution
            # 1. Query database
            # 2. Get contexts
            # 3. Draft emails
            # 4. Save drafts to session state

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result
