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
                
                # Clone Canvas to /var directory with proper ownership handling
                progress.update(task, description="Preparing Canvas installation...")
                
                # Step 1: Setup Git safe directories and clone as root first
                setup_cmd = """bash -c "
                    # Configure Git to handle ownership issues
                    git config --global --add safe.directory '*' &&
                    git config --global user.name 'Canvas Installer' &&
                    git config --global user.email 'installer@canvas.local' &&
                    
                    # Clone Canvas to /var
                    cd /var &&
                    git clone https://github.com/instructure/canvas-lms.git canvas &&
                    cd /var/canvas &&
                    git checkout prod
                " """
                
                self.run_command(setup_cmd, "Cloning Canvas repository", timeout=600)
                
                # Step 2: Fix ownership after successful clone
                progress.update(task, description="Setting up Canvas permissions...")
                ownership_cmd = """bash -c "
                    # Set proper ownership for canvas user
                    chown -R canvas:canvas /var/canvas &&
                    
                    # Configure Git for canvas user
                    sudo -u canvas git config --global --add safe.directory /var/canvas &&
                    sudo -u canvas git config --global user.name 'Canvas User' &&
                    sudo -u canvas git config --global user.email 'canvas@localhost' &&
                    
                    # Verify we're on the right branch
                    cd /var/canvas &&
                    sudo -u canvas git status
                " """
                
                self.run_command(ownership_cmd, "Setting up ownership and permissions")
                
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