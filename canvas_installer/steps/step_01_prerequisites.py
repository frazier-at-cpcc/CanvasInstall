"""
Step 1: System Prerequisites Check
"""

from rich.table import Table
from .base_step import BaseStep
from ..utils import SystemChecker


class PrerequisitesStep(BaseStep):
    """Check system prerequisites before installation"""
    
    @property
    def step_name(self) -> str:
        return "System Prerequisites Check"
    
    @property
    def step_description(self) -> str:
        return "🔍 Checking System Prerequisites..."
    
    def execute(self) -> bool:
        """Execute prerequisites check"""
        self.log_start()
        
        try:
            checks = [
                ("Operating System", SystemChecker.check_ubuntu_version),
                ("Root/Sudo Access", SystemChecker.check_sudo_access),
                ("Hardware Requirements", SystemChecker.check_hardware),
                ("Internet Connectivity", SystemChecker.check_internet),
                ("Disk Space", SystemChecker.check_disk_space)
            ]
            
            table = Table(title="System Prerequisites Check")
            table.add_column("Check", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Details", style="dim")
            
            all_passed = True
            for check_name, check_func in checks:
                try:
                    result, details = check_func()
                    status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
                    table.add_row(check_name, status, details)
                    if not result:
                        all_passed = False
                except Exception as e:
                    table.add_row(check_name, "[red]✗ ERROR[/red]", str(e))
                    all_passed = False
            
            self.console.print(table)
            
            if not all_passed:
                self.console.print("\n[red]❌ Prerequisites check failed. Please resolve the issues above before continuing.[/red]")
                return False
                
            self.console.print("\n[green]✅ All prerequisites passed![/green]")
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False