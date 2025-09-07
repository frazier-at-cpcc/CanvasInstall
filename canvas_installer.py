#!/usr/bin/env python3
"""
Canvas LMS Automated Installer for Ubuntu 22.04
A comprehensive guided installer with TUI interface
"""

import os
import sys
import subprocess
import json
import time
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.padding import Padding
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.padding import Padding
    from rich import box

@dataclass
class InstallationConfig:
    """Configuration class to store all installation parameters"""
    domain: str = ""
    canvas_password: str = ""
    smtp_server: str = ""
    smtp_port: str = "465"
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    flickr_api_key: str = ""
    youtube_api_key: str = ""
    skip_ssl: bool = False
    skip_rce: bool = False
    skip_optimization: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InstallationConfig':
        return cls(**data)

class CanvasInstaller:
    """Main installer class with TUI interface"""
    
    def __init__(self):
        self.console = Console()
        self.config = InstallationConfig()
        self.log_file = f"canvas_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.state_file = "canvas_install_state.json"
        self.current_step = 0
        self.total_steps = 13
        
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
        
        # Installation steps
        self.steps = [
            ("System Prerequisites Check", self.check_prerequisites),
            ("Create Canvas User", self.create_canvas_user),
            ("Install PostgreSQL & Setup Databases", self.setup_postgresql),
            ("Install Git, Ruby, Node.js & Yarn", self.install_development_tools),
            ("Clone & Install Canvas LMS", self.clone_canvas),
            ("Configure Database, Mail & Domain", self.configure_canvas),
            ("Install Dependencies & Compile Assets", self.install_dependencies),
            ("Install & Configure Apache", self.setup_apache),
            ("Setup SSL Certificate", self.setup_ssl),
            ("Configure Virtual Hosts", self.configure_virtual_hosts),
            ("Setup Jobs & Firewall", self.setup_jobs_firewall),
            ("Setup Redis Cache", self.setup_redis),
            ("Enable Rich Content Editor", self.setup_rce),
            ("Set Permissions & Optimization", self.finalize_installation)
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

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        self.console.print("[bold yellow]🔍 Checking System Prerequisites...[/bold yellow]")
        
        checks = [
            ("Operating System", self._check_ubuntu_version),
            ("Root/Sudo Access", self._check_sudo_access),
            ("Hardware Requirements", self._check_hardware),
            ("Internet Connectivity", self._check_internet),
            ("Disk Space", self._check_disk_space)
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
        return True

    def _check_ubuntu_version(self) -> Tuple[bool, str]:
        """Check if running Ubuntu 22.04"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'Ubuntu' in content and '22.04' in content:
                    return True, "Ubuntu 22.04 LTS detected"
                else:
                    return False, "Ubuntu 22.04 LTS required"
        except:
            return False, "Cannot determine OS version"

    def _check_sudo_access(self) -> Tuple[bool, str]:
        """Check sudo access"""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
            if result.returncode == 0:
                return True, "Sudo access confirmed"
            else:
                return False, "Sudo access required"
        except:
            return False, "Cannot verify sudo access"

    def _check_hardware(self) -> Tuple[bool, str]:
        """Check hardware requirements"""
        try:
            # Check RAM (8GB = 8,000,000 KB approximately)
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_kb = int(line.split()[1])
                        mem_gb = mem_kb / 1024 / 1024
                        if mem_gb < 7.5:  # Allow some margin
                            return False, f"RAM: {mem_gb:.1f}GB (8GB required)"
                        break
            
            # Check CPU cores
            cpu_count = os.cpu_count()
            if cpu_count < 4:
                return False, f"CPU: {cpu_count} cores (4 required)"
            
            return True, f"RAM: {mem_gb:.1f}GB, CPU: {cpu_count} cores"
        except:
            return False, "Cannot verify hardware specs"

    def _check_internet(self) -> Tuple[bool, str]:
        """Check internet connectivity"""
        try:
            result = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                return True, "Internet connection verified"
            else:
                return False, "No internet connection"
        except:
            return False, "Cannot verify internet connection"

    def _check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                available = parts[3]
                # Parse available space (e.g., "50G" -> 50)
                if 'G' in available:
                    available_gb = float(available.replace('G', ''))
                    if available_gb < 30:
                        return False, f"Available: {available} (30GB required)"
                    return True, f"Available: {available}"
            return False, "Cannot determine disk space"
        except:
            return False, "Cannot check disk space"

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

    def create_canvas_user(self) -> bool:
        """Create canvas user and setup permissions"""
        self.console.print("\n[bold yellow]👤 Creating Canvas User...[/bold yellow]")
        
        try:
            # Check if canvas user already exists
            result = subprocess.run(['id', 'canvas'], capture_output=True)
            if result.returncode == 0:
                self.console.print("[green]Canvas user already exists[/green]")
                return True
            
            # Create canvas user
            cmd = "sudo adduser --disabled-password --gecos '' canvas"
            self._run_command(cmd, "Creating canvas user")
            
            # Add to sudo group
            cmd = "sudo usermod -aG sudo canvas"
            self._run_command(cmd, "Adding canvas user to sudo group")
            
            self.console.print("[green]✅ Canvas user created successfully[/green]")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create canvas user: {e}")
            self.console.print(f"[red]❌ Failed to create canvas user: {e}[/red]")
            return False

    def setup_postgresql(self) -> bool:
        """Setup PostgreSQL and create databases"""
        self.console.print("\n[bold yellow]🗄️  Setting up PostgreSQL...[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                
                # Install PostgreSQL
                task = progress.add_task("Installing PostgreSQL...", total=None)
                
                commands = [
                    "sudo apt-get update",
                    "sudo apt-get install -y wget ca-certificates",
                    "wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/postgresql.asc",
                    "echo \"deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main\" | sudo tee /etc/apt/sources.list.d/pgdg.list",
                    "sudo apt-get update",
                    "sudo apt-get install -y postgresql-14"
                ]
                
                for i, cmd in enumerate(commands):
                    progress.update(task, description=f"Installing PostgreSQL... ({i+1}/{len(commands)})")
                    self._run_command(cmd, f"PostgreSQL install step {i+1}")
                
                # Create PostgreSQL user and databases
                progress.update(task, description="Creating PostgreSQL user and databases...")
                
                # Create canvas user with password
                create_user_cmd = f"sudo -u postgres psql -c \"CREATE USER canvas WITH PASSWORD '{self.config.canvas_password}';\""
                self._run_command(create_user_cmd, "Creating PostgreSQL canvas user", show_output=False)
                
                # Create databases
                db_commands = [
                    "sudo -u postgres createdb canvas_production --owner=canvas",
                    "sudo -u postgres createdb canvas_development --owner=canvas",
                    f"sudo -u postgres createuser {os.environ.get('USER', 'root')}",
                    f"sudo -u postgres psql -c \"alter user {os.environ.get('USER', 'root')} with superuser\" postgres"
                ]
                
                for cmd in db_commands:
                    self._run_command(cmd, "Setting up databases")
            
            self.console.print("[green]✅ PostgreSQL setup completed[/green]")
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL setup failed: {e}")
            self.console.print(f"[red]❌ PostgreSQL setup failed: {e}[/red]")
            return False

    def install_development_tools(self) -> bool:
        """Install Git, Ruby, Node.js, and Yarn"""
        self.console.print("\n[bold yellow]🛠️  Installing Development Tools...[/bold yellow]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                transient=True
            ) as progress:
                
                total_steps = 8
                task = progress.add_task("Installing development tools...", total=total_steps)
                
                steps = [
                    ("sudo apt-get install -y git-core", "Installing Git"),
                    ("sudo apt-get install -y software-properties-common", "Installing software properties"),
                    ("sudo add-apt-repository -y ppa:instructure/ruby", "Adding Ruby PPA"),
                    ("sudo apt-get update", "Updating package lists"),
                    ("sudo apt-get install -y ruby3.3 ruby3.3-dev zlib1g-dev libxml2-dev libsqlite3-dev postgresql libpq-dev libxmlsec1-dev libidn11-dev curl make g++", "Installing Ruby and dependencies"),
                    ("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash", "Installing NVM"),
                    ("bash -c 'export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm install 18.20'", "Installing Node.js 18.20"),
                    ("curl -o- -L https://yarnpkg.com/install.sh | bash -s -- --version 1.19.1", "Installing Yarn")
                ]
                
                for i, (cmd, desc) in enumerate(steps):
                    progress.update(task, description=desc, completed=i)
                    self._run_command(cmd, desc)
                    progress.update(task, completed=i+1)
            
            self.console.print("[green]✅ Development tools installed successfully[/green]")
            return True
            
        except Exception as e:
            self.logger.error(f"Development tools installation failed: {e}")
            self.console.print(f"[red]❌ Development tools installation failed: {e}[/red]")
            return False

    def _run_command(self, command: str, description: str = "", show_output: bool = True, timeout: int = 600) -> subprocess.CompletedProcess:
        """Execute a shell command with logging and error handling"""
        self.logger.info(f"Executing: {description or command}")
        
        try:
            if show_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    timeout=timeout,
                    text=True,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    timeout=timeout,
                    text=True,
                    capture_output=True
                )
            
            self.logger.info(f"Command completed successfully: {description or command}")
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {description or command} - Exit code: {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {description or command}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error running command: {description or command} - {e}")
            raise

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

    # Placeholder methods for remaining steps
    def clone_canvas(self) -> bool:
        """Clone and install Canvas LMS"""
        self.console.print("\n[bold yellow]📦 Cloning Canvas LMS...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def configure_canvas(self) -> bool:
        """Configure Canvas settings"""
        self.console.print("\n[bold yellow]⚙️  Configuring Canvas...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def install_dependencies(self) -> bool:
        """Install Canvas dependencies"""
        self.console.print("\n[bold yellow]📚 Installing Dependencies...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def setup_apache(self) -> bool:
        """Setup Apache web server"""
        self.console.print("\n[bold yellow]🌐 Setting up Apache...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def setup_ssl(self) -> bool:
        """Setup SSL certificate"""
        if self.config.skip_ssl:
            self.console.print("\n[yellow]⏭️  Skipping SSL setup[/yellow]")
            return True
        self.console.print("\n[bold yellow]🔒 Setting up SSL Certificate...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def configure_virtual_hosts(self) -> bool:
        """Configure Apache virtual hosts"""
        self.console.print("\n[bold yellow]🏠 Configuring Virtual Hosts...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def setup_jobs_firewall(self) -> bool:
        """Setup automated jobs and firewall"""
        self.console.print("\n[bold yellow]🔧 Setting up Jobs & Firewall...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def setup_redis(self) -> bool:
        """Setup Redis cache"""
        self.console.print("\n[bold yellow]⚡ Setting up Redis Cache...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def setup_rce(self) -> bool:
        """Setup Rich Content Editor"""
        if self.config.skip_rce:
            self.console.print("\n[yellow]⏭️  Skipping Rich Content Editor setup[/yellow]")
            return True
        self.console.print("\n[bold yellow]📝 Setting up Rich Content Editor...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

    def finalize_installation(self) -> bool:
        """Set permissions and final optimization"""
        self.console.print("\n[bold yellow]🎯 Finalizing Installation...[/bold yellow]")
        # Implementation will be added in next iteration
        return True

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
            for i, (step_name, step_func) in enumerate(self.steps[self.current_step:], self.current_step):
                self.console.print(f"\n[bold blue]📍 Step {i + 1}/{self.total_steps}: {step_name}[/bold blue]")
                
                if not step_func():
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
                f"[dim]Log file: {self.log_file}[/dim]",
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