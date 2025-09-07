"""
Step 3: PostgreSQL Installation and Setup
"""

import os
from rich.progress import Progress, SpinnerColumn, TextColumn
from .base_step import BaseStep


class PostgreSQLStep(BaseStep):
    """Setup PostgreSQL and create databases"""
    
    @property
    def step_name(self) -> str:
        return "Install PostgreSQL & Setup Databases"
    
    @property
    def step_description(self) -> str:
        return "🗄️  Setting up PostgreSQL..."
    
    def execute(self) -> bool:
        """Execute PostgreSQL setup"""
        self.log_start()
        
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
                    self.run_command(cmd, f"PostgreSQL install step {i+1}")
                
                # Create PostgreSQL user and databases
                progress.update(task, description="Creating PostgreSQL user and databases...")
                
                # Create canvas user with password
                create_user_cmd = f"sudo -u postgres psql -c \"CREATE USER canvas WITH PASSWORD '{self.config.canvas_password}';\""
                self.run_command(create_user_cmd, "Creating PostgreSQL canvas user", show_output=False)
                
                # Create databases
                db_commands = [
                    "sudo -u postgres createdb canvas_production --owner=canvas",
                    "sudo -u postgres createdb canvas_development --owner=canvas",
                    f"sudo -u postgres createuser {os.environ.get('USER', 'root')}",
                    f"sudo -u postgres psql -c \"alter user {os.environ.get('USER', 'root')} with superuser\" postgres"
                ]
                
                for cmd in db_commands:
                    self.run_command(cmd, "Setting up databases")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False