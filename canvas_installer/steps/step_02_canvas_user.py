"""
Step 2: Create Canvas User
"""

import subprocess
from .base_step import BaseStep


class CanvasUserStep(BaseStep):
    """Create canvas user and setup permissions"""
    
    @property
    def step_name(self) -> str:
        return "Create Canvas User"
    
    @property
    def step_description(self) -> str:
        return "👤 Creating Canvas User..."
    
    def execute(self) -> bool:
        """Execute canvas user creation"""
        self.log_start()
        
        try:
            # Check if canvas user already exists
            result = subprocess.run(['id', 'canvas'], capture_output=True)
            if result.returncode == 0:
                self.console.print("[green]Canvas user already exists[/green]")
                self.log_success()
                return True
            
            # Create canvas user
            cmd = "sudo adduser --disabled-password --gecos '' canvas"
            self.run_command(cmd, "Creating canvas user")
            
            # Add to sudo group
            cmd = "sudo usermod -aG sudo canvas"
            self.run_command(cmd, "Adding canvas user to sudo group")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False