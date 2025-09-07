"""
Step 8: Install and Configure Apache
"""

from rich.progress import Progress, SpinnerColumn, TextColumn
from .base_step import BaseStep


class ApacheStep(BaseStep):
    """Setup Apache web server with Passenger"""
    
    @property
    def step_name(self) -> str:
        return "Install & Configure Apache"
    
    @property
    def step_description(self) -> str:
        return "🌐 Setting up Apache..."
    
    def execute(self) -> bool:
        """Execute Apache setup"""
        self.log_start()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                
                task = progress.add_task("Installing Apache...", total=None)
                
                # Install Apache and Passenger
                commands = [
                    "sudo apt-get install -y apache2",
                    "sudo apt-get install -y dirmngr gnupg apt-transport-https ca-certificates",
                    "sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7",
                    "sudo sh -c 'echo deb https://oss-binaries.phusionpassenger.com/apt/passenger $(lsb_release -cs) main > /etc/apt/sources.list.d/passenger.list'",
                    "sudo apt-get update",
                    "sudo apt-get install -y libapache2-mod-passenger"
                ]
                
                for cmd in commands:
                    self.run_command(cmd, "Apache installation")
                
                # Enable Apache modules
                progress.update(task, description="Configuring Apache modules...")
                modules = ["rewrite", "passenger", "ssl", "proxy_http"]
                for module in modules:
                    self.run_command(f"sudo a2enmod {module}", f"Enabling {module} module")
                
                # Configure Passenger
                progress.update(task, description="Configuring Passenger...")
                passenger_config = """PassengerDefaultUser canvas
PassengerStartTimeout 180
PassengerPreloadBundler On
PassengerFriendlyErrorPages On"""
                
                self.run_command(
                    f'echo "{passenger_config}" | sudo tee -a /etc/apache2/mods-available/passenger.conf',
                    "Adding Passenger configuration"
                )
                
                # Restart Apache
                self.run_command("sudo systemctl restart apache2", "Restarting Apache")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False