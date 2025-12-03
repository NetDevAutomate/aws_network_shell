"""Organization module"""

from typing import Optional, Dict, List
import boto3
from rich.table import Table

from ..core import BaseClient, ModuleInterface, run_with_spinner, Context


class OrgModule(ModuleInterface):
    @property
    def name(self) -> str:
        return "org"

    @property
    def commands(self) -> Dict[str, str]:
        return {"org": "Enter Organization context"}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        return {}

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        return {None: ["accounts"], "org": ["detail"]}

    def complete_org(self, text, line, begidx, endidx):
        """Tab completion for org command"""
        # org command takes no arguments currently
        return []

    def execute(self, shell, command: str, args: str):
        """Enter Organization context"""
        if shell.ctx_type is not None:
            shell.console.print("[red]Use 'end' to return to top level first[/]")
            return

        # Get organization details
        client = OrgClient(shell.profile, shell.session)
        try:
            org = run_with_spinner(
                lambda: client.get_organization(),
                "Fetching organization details",
                console=shell.console,
            )
        except Exception as e:
            shell.console.print(f"[red]Error fetching organization: {e}[/]")
            return

        shell.context_stack = [
            Context("org", org["Id"], org.get("DisplayName") or org["Id"], org)
        ]
        shell._update_prompt()


class OrgClient(BaseClient):
    def __init__(
        self, profile: Optional[str] = None, session: Optional[boto3.Session] = None
    ):
        super().__init__(profile, session)

    def get_organization(self) -> dict:
        """Get organization details"""
        org_client = self.session.client("organizations")
        try:
            resp = org_client.describe_organization()
            return resp["Organization"]
        except org_client.exceptions.AWSOrganizationsNotInUseException:
            raise Exception("Your account is not a member of an AWS Organization")
        except Exception as e:
            raise Exception(f"Failed to get organization: {e}")

    def list_accounts(self) -> List[dict]:
        """List all accounts in the organization"""
        org_client = self.session.client("organizations")
        accounts = []
        try:
            paginator = org_client.get_paginator("list_accounts")
            for page in paginator.paginate():
                for account in page["Accounts"]:
                    accounts.append(
                        {
                            "Id": account["Id"],
                            "Name": account.get("Name", ""),
                            "Status": account["Status"],
                            "Arn": account["Arn"],
                            "Email": account["Email"],
                        }
                    )
        except org_client.exceptions.AWSOrganizationsNotInUseException:
            raise Exception("Your account is not a member of an AWS Organization")
        except Exception as e:
            raise Exception(f"Failed to list accounts: {e}")
        return accounts


class OrgDisplay:
    def __init__(self, console):
        self.console = console

    def show_accounts(self, accounts: List[dict]):
        """Display accounts in a table"""
        if not accounts:
            self.console.print("[yellow]No accounts found[/]")
            return

        table = Table(
            title="Organization Accounts", show_header=True, header_style="bold"
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Account ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Email", style="white")

        for i, account in enumerate(accounts, 1):
            status_style = "green" if account["Status"] == "ACTIVE" else "red"
            table.add_row(
                str(i),
                account["Id"],
                account["Name"] or "-",
                f"[{status_style}]{account['Status']}[/]",
                account["Email"],
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(accounts)} account(s)[/]")
