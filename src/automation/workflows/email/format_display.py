"""
Format Display Module - Handles all stylistic console output for the cold email automation system.

This module provides color-coded, formatted display functions for various workflow outputs.
"""


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def display_drafted_email(email_dict: dict) -> None:
    """
    Display a drafted email with color-coded formatting.

    Args:
        email_dict: Dictionary containing email fields (to, subject, body, raw_html)
    """
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Email drafted and moved to review{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─' * 80}{Colors.END}")

    # Display recipient
    print(f"{Colors.BOLD}To:{Colors.END} {Colors.BLUE}{email_dict['to']}{Colors.END}")

    # Display subject
    print(f"{Colors.BOLD}Subject:{Colors.END} {Colors.YELLOW}{email_dict['subject']}{Colors.END}")

    # Display body
    print(f"\n{Colors.BOLD}Body:{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")
    print(email_dict['body'])
    print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")

    # Display raw_html if present
    if email_dict.get('raw_html'):
        print(f"\n{Colors.BOLD}Raw HTML:{Colors.END}")
        print(email_dict['raw_html'])


def display_workflow_header(workflow_name: str, email_count: int) -> None:
    """
    Display a workflow header with formatting.

    Args:
        workflow_name: Name of the workflow
        email_count: Target number of emails to process
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}Starting {workflow_name} (Target: {email_count} emails){Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


def display_workflow_footer(workflow_name: str, count: int) -> None:
    """
    Display a workflow footer with formatting.

    Args:
        workflow_name: Name of the workflow
        count: Number of emails processed
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{workflow_name} Complete: Processed {count} emails{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


def display_error(message: str) -> None:
    """
    Display an error message with formatting.

    Args:
        message: Error message to display
    """
    print(f"{Colors.RED}{Colors.BOLD}✗ {message}{Colors.END}")


def display_email_processing_header(counter: int, total: int, email: str, email_type: str = "company") -> None:
    """
    Display header for email processing step.

    Args:
        counter: Current email number (0-indexed)
        total: Total number of emails to process
        email: Email address being processed
        email_type: Type of email ("company" or "recruiter")
    """
    print(f"{Colors.BOLD}[{counter + 1}/{total}]{Colors.END} Processing {email_type} email: {Colors.BLUE}{email}{Colors.END}")


def display_context_info(context: dict, is_recruiter: bool = False) -> None:
    """
    Display context information for the email being drafted.

    Args:
        context: Context dictionary with company/recruiter info
        is_recruiter: True if context includes recruiter info
    """
    company_name = context.get('cname', 'Unknown')
    print(f"  {Colors.BOLD}Company:{Colors.END} {company_name}")

    if is_recruiter:
        fname = context.get('fname', '')
        lname = context.get('lname', '')
        print(f"  {Colors.BOLD}Recruiter:{Colors.END} {fname} {lname}")
