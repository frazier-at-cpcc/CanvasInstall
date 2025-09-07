"""
Main Canvas LMS installer with TUI interface
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich import box

from .config import InstallationConfig
from .steps import (
    PrerequisitesStep, CanvasUserStep, PostgreSQLStep, DevToolsStep,
    CloneCanvasStep, ConfigureCanvasStep, DependenciesStep, ApacheStep,
    SSLStep, VirtualHostsStep, JobsFirewallStep, RedisStep, RCEStep, FinalizeStep
)


class CanvasInstaller:
    """Main installer class with TUI interface"""
    
    def __init__(self):
        self.console = Console()
        self.config = InstallationConfig()
        self.log_file = f"canvas_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.state_file = "canvas_install_state.json"
        self.current_step = 0
        self.total_steps = 14
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Installation steps - using modular step classes
        self.steps = [
            ("System Prerequisites Check", PrerequisitesStep),
            ("Create Canvas User", CanvasUserStep),
            ("Install PostgreSQL & Setup Databases", PostgreSQLStep),
            ("Install Git, Ruby, Node.js & Yarn", DevToolsStep),
            ("Clone & Install Canvas LMS", CloneCanvasStep),
            ("Configure Database, Mail & Domain", ConfigureCanvasStep),
            ("Install Dependencies & Compile Assets", DependenciesStep),
            ("Install & Configure Apache", ApacheStep),
            ("Setup SSL Certificate", SSLStep),
            ("Configure Virtual Hosts", VirtualHostsStep),
            ("Setup Jobs & Firewall", JobsFirewallStep),
            ("Setup Redis Cache", RedisStep),
            ("Enable Rich Content Editor", RCEStep),
            ("Set Permissions & Optimization", FinalizeStep)
        ]

    def show_banner(self):
        """Display the installer banner"""
        banner = Panel.fit(
            "[bold cyan]Canvas LMS Automated Installer[/bold cyan]\n"
            "[dim]Ubuntu 22.04 LTS - Comprehensive Installation Guide[/dim]\n\n"
            "[yellow]⚠️  This installer requires root privileges and will modify system configuration[/yellow]",
            box=box.DOUBLE,
            border_style="bright_blue"
        )
        self.console.print(banner)
        self.console.print()

    def collect_configuration(self):
        """Collect configuration from user"""
        self.console.print("\n[bold cyan]📋 Configuration Setup[/bold cyan]")
        self.console.print("Please provide the following information for your Canvas installation:\n")
        
        # Domain configuration
        self.config.domain = Prompt.ask(
            "[yellow]Domain name for Canvas[/yellow] (e.g., canvas.example.com)",
            default=""
        ).strip()
        
        # PostgreSQL password
        self.config.canvas_password = Prompt.ask(
            "[yellow]PostgreSQL password for canvas user[/yellow]",
            password=True
        )
        
        # SMTP Configuration
        if Confirm.ask("\n[cyan]Configure email settings now?[/cyan]", default=True):
            self.console.print("\n[dim]SMTP Configuration (for Canvas notifications)[/dim]")
            self.config.smtp_server = Prompt.ask("SMTP Server", default="smtp.gmail.com")
            self.config.smtp_port = Prompt.ask("SMTP Port", default="465")
            self.config.smtp_username = Prompt.ask("SMTP Username/Email")
            self.config.smtp_password = Prompt.ask("SMTP Password", password=True)
            self.config.smtp_from_email = Prompt.ask("From Email Address")
            self.config.smtp_from_name = Prompt.ask("From Name", default="Canvas LMS")
        
        # API Keys for Rich Content Editor
        if Confirm.ask("\n[cyan]Configure Rich Content Editor API keys?[/cyan]", default=True):
            self.console.print("\n[dim]API Keys for Rich Content Editor[/dim]")
            self.config.flickr_api_key = Prompt.ask("Flickr API Key (optional)", default="")
            self.config.youtube_api_key = Prompt.ask("YouTube API Key (optional)", default="")
        else:
            self.config.skip_rce = True
        
        # Optional features
        self.config.skip_ssl = not Confirm.ask("\n[cyan]Setup SSL certificate with Let's Encrypt?[/cyan]", default=True)
        self.config.skip_optimization = not Confirm.ask("[cyan]Enable file download optimization?[/cyan]", default=True)
        
        self._save_state()

    def _save_state(self):
        """Save current installation state"""
        state = {
            'current_step': self.current_step,
            'config': self.config.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> bool:
        """Load previous installation state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.current_step = state.get('current_step', 0)
                self.config = InstallationConfig.from_dict(state.get('config', {}))
                return True
        except Exception as e:
            self.logger.warning(f"Failed to load state: {e}")
        
        return False

    def run_installation(self):
        """Main installation process"""
        self.show_banner()
        
        # Load previous state if exists
        if os.path.exists(self.state_file):
            if Confirm.ask("\n[cyan]Previous installation found. Resume from where you left off?[/cyan]"):
                self._load_state()
                self.console.print(f"[green]Resuming from step {self.current_step + 1}[/green]")
            else:
                os.remove(self.state_file)
                self.current_step = 0
        
        # Run installation steps
        try:
            for i, (step_name, step_class) in enumerate(self.steps[self.current_step:], self.current_step):
                self.console.print(f"\n[bold blue]📍 Step {i + 1}/{self.total_steps}: {step_name}[/bold blue]")
                
                # Create step instance and execute
                step_instance = step_class(self.config, self.console, self.logger)
                
                if not step_instance.execute():
                    self.console.print(f"\n[red]❌ Installation failed at step: {step_name}[/red]")
                    self.console.print("[yellow]Check the log file for details and run the installer again to resume.[/yellow]")
                    return False
                
                self.current_step = i + 1
                self._save_state()
                
                if i < len(self.steps) - 1:
                    time.sleep(1)  # Brief pause between steps
            
            # Installation completed
            self.console.print("\n" + "="*60)
            success_panel = Panel.fit(
                "[bold green]🎉 Canvas LMS Installation Completed Successfully! 🎉[/bold green]\n\n"
                f"[cyan]Your Canvas instance is available at: https://{self.config.domain}[/cyan]\n"
                f"[dim]Log file: {self.log_file}[/dim]\n\n"
                "[yellow]Next Steps:[/yellow]\n"
                "[dim]1. Access your Canvas installation via the domain above[/dim]\n"
                "[dim]2. Complete the initial Canvas setup wizard[/dim]\n"
                "[dim]3. If you enabled RCE, start it with: cd /var/canvas-rce-api && screen -S canvas-rce-api npm start[/dim]",
                box=box.DOUBLE,
                border_style="bright_green"
            )
            self.console.print(success_panel)
            
            # Clean up state file
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
                
            return True
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]⏸️  Installation interrupted by user[/yellow]")
            self.console.print("[dim]Run the installer again to resume from where you left off.[/dim]")
            return False
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            self.console.print(f"\n[red]❌ Installation failed: {e}[/red]")
            return False


def main():
    """Main entry point"""
    if os.geteuid() != 0 and not os.environ.get('SUDO_USER'):
        print("This installer requires sudo privileges. Please run with sudo.")
        sys.exit(1)
    
    installer = CanvasInstaller()
    
    # Collect configuration if not resuming
    if not os.path.exists(installer.state_file):
        installer.collect_configuration()
    
    # Run the installation
    success = installer.run_installation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()