"""
Orchestration Layer for Cold Email Automation System

This module manages high-level workflows for the personalized cold-email internship automation tool.
It acts as the entry point for workflow requests and coordinates agents/services to complete tasks.

Responsibilities:
- Coordinate workflow execution
- Manage session state (DRAFT, REVIEW, QUEUED)
- Invoke appropriate agents and services
- Enforce rate limiting and boundaries(but how?)

Boundaries:
- Only knows which workflows can be used and when to use them
- Interacts with service layer and agents to complete tasks
- Does not directly call Gmail API or database operations
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enum import Enum
from typing import Dict, List, Any
from src.automation.workflows.draft_email import DraftEmailWorkflow
from src.automation.session_state import SessionState
from src.automation.agents.agent_manager import AgentManager
from src.automation.format_display import (
    display_drafted_email,
    display_workflow_header,
    display_workflow_footer,
    display_error,
    display_email_processing_header,
    display_context_info
)
from db.connection import get_session



class OrchestrationLayer:
  """
  Main orchestration class that manages all workflows for the cold email automation system.

  This class coordinates between agents, services, and the database to execute
  complete workflows such as company research, email drafting, sending, and follow-ups.

  Everything from this pulls directly from the 
  """

  def __init__(self, email_service: Any):
    """
    Initialize the orchestration layer with authenticated Gmail service.

    Args:
        email_service: Authenticated Gmail API service object
    """
    self.session = SessionState()
    self.session.add_gmail_service(email_service)

    self.agents = AgentManager() 
    # TODO later: 
    # read config.json for rate-limiting capabilities 

  def run_research_workflow(self): # might complete in future, depending on if its needed
    """
    Execute company research workflow.
    """
    pass

  def _filter_reviewed_emails(self, emails: List[str], email_ids: List[int]) -> tuple:
    """
    Filter out emails that already exist in the review section to avoid redrafting.

    Args:
      emails: List of email addresses to check
      email_ids: List of corresponding company IDs

    Returns:
      Tuple of (filtered_emails, filtered_ids) with reviewed emails removed
    """
    reviewed_emails = set(self.session.review.keys())
    filtered_emails = []
    filtered_ids = []

    for email, email_id in zip(emails, email_ids):
      if email not in reviewed_emails:
        filtered_emails.append(email)
        filtered_ids.append(email_id)

    return filtered_emails, filtered_ids

  def run_draft_email_workflow(self, email_count : int):
    display_workflow_header("Draft Email Workflow", email_count)

    with get_session() as db_session:
      all_emails = DraftEmailWorkflow.query_database(db_session)
      company_emails = all_emails[0]
      company_email_ids = all_emails[1]
      recruiter_emails = all_emails[2]
      recruiter_email_company_ids = all_emails[3]

      # Filter out emails already in review to avoid redrafting
      company_emails, company_email_ids = self._filter_reviewed_emails(company_emails, company_email_ids)
      recruiter_emails, recruiter_email_company_ids = self._filter_reviewed_emails(recruiter_emails, recruiter_email_company_ids)

      num_to_draft = min(len(recruiter_emails) + len(company_emails), email_count)
      print(f"Found {len(company_emails)} company emails and {len(recruiter_emails)} recruiter emails")
      print(f"Processing {num_to_draft} emails total\n")

      counter = 0

      # Process company emails
      for c_idx, company_email in enumerate(company_emails):
        if counter >= num_to_draft:
          break

        display_email_processing_header(counter, num_to_draft, company_email, "company")
        context = DraftEmailWorkflow.get_company_context(db_session, company_email, company_email_ids[c_idx])
        display_context_info(context, is_recruiter=False)

        # Process email through workflow (resume selection -> draft)
        success, email_dict = DraftEmailWorkflow.process_and_add_to_session(
          context=context,
          resume_selector_agent=self.agents.resume_selector_agent,
          email_personalization_agent=self.agents.email_personalization_agent,
          session_state=self.session,
          is_recruiter=False
        )

        if success and email_dict:
          # Add to session as draft, then move to review
          if self.session.add_draft(email_dict):
            if self.session.move_to_review(email_dict['to']):
              display_drafted_email(email_dict)
            else:
              display_error("Failed to move email to review")
          else:
            display_error("Failed to add draft to session")
        else:
          display_error("Failed to generate email draft")

        print()
        counter += 1

      # Process recruiter emails
      for r_idx, recruiter_email in enumerate(recruiter_emails):
        if counter >= num_to_draft:
          break

        display_email_processing_header(counter, num_to_draft, recruiter_email, "recruiter")
        company_context = DraftEmailWorkflow.get_company_context(db_session, recruiter_email, recruiter_email_company_ids[r_idx])
        recruiter_context = DraftEmailWorkflow.get_recruiter_context(db_session, recruiter_email)
        context = {**company_context, **recruiter_context}
        display_context_info(context, is_recruiter=True)

        # Process email through workflow (resume selection -> draft)
        success, email_dict = DraftEmailWorkflow.process_and_add_to_session(
          context=context,
          resume_selector_agent=self.agents.resume_selector_agent,
          email_personalization_agent=self.agents.email_personalization_agent,
          session_state=self.session,
          is_recruiter=True
        )

        if success and email_dict:
          # Add to session as draft, then move to review
          if self.session.add_draft(email_dict):
            if self.session.move_to_review(email_dict['to']):
              display_drafted_email(email_dict)
            else:
              display_error("Failed to move email to review")
          else:
            display_error("Failed to add draft to session")
        else:
          display_error("Failed to generate email draft")

        print()
        counter += 1

      display_workflow_footer("Draft Workflow", counter) 
  
  def run_review_email_workflow(self): 
    pass
  
  def run_queue_email_workflow(self):
    pass

  def run_cold_email_workflow(self):
    """
    Execute personalized cold email generation and sending workflow. This is for later, when the testing for the individual
    components work well such as the draft, review, and queue workflow are fully functional, then this will
    use an agent to execute the given tasks. 
    """
    pass

  def run_follow_up_email_workflow(self):
    """
    Execute follow-up email workflow for sent emails without replies.
    """
    pass

  def run_check_replies_workflow(self):
    """
    Execute workflow to check for email replies and update database.
    """
    pass 