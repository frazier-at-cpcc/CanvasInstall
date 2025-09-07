"""
Step 5: Clone and Install Canvas LMS
"""

from rich.progress import Progress, SpinnerColumn, TextColumn
from .base_step import BaseStep


class CloneCanvasStep(BaseStep):
    """Clone Canvas LMS repository and setup initial configuration"""
    
    @property
    def step_name(self) -> str:
        return "Clone & Install Canvas LMS"
    
    @property
    def step_description(self) -> str:
        return "📦 Cloning Canvas LMS..."
    
    def execute(self) -> bool:
        """Execute Canvas cloning and setup"""
        self.log_start()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                
                task = progress.add_task("Cloning Canvas LMS...", total=None)
                
                # Navigate to /var directory and clone Canvas
                progress.update(task, description="Cloning Canvas repository...")
                commands = [
                    "cd /var",
                    "sudo git clone https://github.com/instructure/canvas-lms.git canvas",
                    f"sudo chown -R canvas:canvas /var/canvas",
                    "cd /var/canvas",
                    "sudo -u canvas git checkout prod"
                ]
                
                for cmd in commands:
                    self.run_command(cmd, "Canvas clone step")
                
                # Copy configuration files
                progress.update(task, description="Setting up configuration files...")
                config_files = [
                    "amazon_s3", "database", "delayed_jobs", "vault_contents", 
                    "domain", "file_store", "outgoing_mail", "security", "external_migration"
                ]
                
                for config in config_files:
                    cmd = f"cd /var/canvas && sudo -u canvas cp config/{config}.yml.example config/{config}.yml"
                    self.run_command(cmd, f"Copying {config} config")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False