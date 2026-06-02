import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from prompt_toolkit import PromptSession
import time

from src.TUI.commands import CommandHandler
from src.oauth import authenticate_gmail

# handles the interactive shell

app = typer.Typer(help="Automation Agent - Personalized Cold-Email Internship Tool")
console = Console()


def main():
    """
    Main entry point for the interactive REPL shell.
    """
    console.print("[bold green]Welcome to Automation Agent![/bold green]")
    console.print("Personalized Cold-Email Internship Automation Tool\n")

    console.print("[cyan]Available commands:[/cyan]")
    console.print("  • stats - View email and company statistics")
    console.print("  • create_drafts <count> - Create email drafts from database")
    console.print("  • review_drafts <count> - Review draft emails")
    console.print("  • queue_reviewed_emails <count> - Queue reviewed emails to be sent")
    console.print("  • find_emails - Research companies and find emails")
    console.print("  • send_emails - Send personalized cold emails")
    console.print("  • clean_raw_data - Clean and validate data.json")
    console.print("  • clear_database - Clear all data from the database")
    console.print("  • clear_session - Clear all data from email_session.json")
    console.print("  • open_scraper - Launch the clothing scraper tool")
    console.print("  • clear - Clear the terminal screen")
    console.print("  • help - Show available commands")
    console.print("  • exit - Exit the shell\n")

    # Authenticate Gmail service before initializing anything else
    gmail_service = authenticate_gmail()

    # Initialize prompt session and command handler
    session = PromptSession()
    handler = CommandHandler(gmail_service)

    # REPL Loop
    while True:
        try:
            # Get user input
            user_input = session.prompt("> ")

            # Skip empty input
            if not user_input.strip():
                continue

            # Exit condition
            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            # Clear screen
            if user_input.strip().lower() == "clear":
                console.clear()
                continue

            # Execute command
            handler.execute(user_input)

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            continue
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break


if __name__ == "__main__":
    main() 