"""
Email Review Display - Handles all TUI output and interactive input for the review workflow.
"""

from typing import Dict, Tuple


class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def display_review_header(total: int) -> None:
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}Review Workflow — {total} email(s) pending review{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


def display_review_footer(approved: int, rejected: int, skipped: int) -> None:
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}Review Complete — "
          f"{Colors.GREEN}Approved: {approved}{Colors.END}  "
          f"{Colors.RED}Rejected: {rejected}{Colors.END}  "
          f"{Colors.YELLOW}Skipped: {skipped}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


def display_email_for_review(counter: int, total: int, email_dict: Dict) -> None:
    print(f"{Colors.BOLD}[{counter}/{total}]{Colors.END} Reviewing: {Colors.BLUE}{email_dict['to']}{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")
    print(f"{Colors.BOLD}To:{Colors.END}      {Colors.BLUE}{email_dict['to']}{Colors.END}")
    print(f"{Colors.BOLD}Subject:{Colors.END} {Colors.YELLOW}{email_dict['subject']}{Colors.END}")
    print(f"{Colors.BOLD}Resume:{Colors.END}  {email_dict.get('resume_type', 'N/A')}")
    print(f"\n{Colors.BOLD}Body:{Colors.END}")
    print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")
    print(email_dict['body'])
    print(f"{Colors.CYAN}{'─' * 80}{Colors.END}")


def prompt_review_action() -> str:
    """
    Prompt user for review action. Returns 'a', 'r', or 's'.
    Loops until a valid input is given.
    """
    while True:
        raw = input(
            f"\n{Colors.BOLD}Action:{Colors.END} "
            f"[{Colors.GREEN}a{Colors.END}]pprove  "
            f"[{Colors.RED}r{Colors.END}]eject  "
            f"[{Colors.YELLOW}s{Colors.END}]kip  > "
        ).strip().lower()

        if raw in ('a', 'r', 's'):
            return raw

        print(f"{Colors.RED}Invalid input — enter 'a', 'r', or 's'{Colors.END}")


def display_action_result(action: str, email: str) -> None:
    if action == 'a':
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Approved — moved to queue:{Colors.END} {email}\n")
    elif action == 'r':
        print(f"{Colors.RED}{Colors.BOLD}✗ Rejected — returned to drafts:{Colors.END} {email}\n")
    elif action == 's':
        print(f"{Colors.YELLOW}{Colors.BOLD}→ Skipped — left in review:{Colors.END} {email}\n")
