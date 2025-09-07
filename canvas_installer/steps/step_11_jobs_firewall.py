"""
Step 11: Setup Automated Jobs and Firewall
"""

from .base_step import BaseStep


class JobsFirewallStep(BaseStep):
    """Setup automated jobs and firewall rules"""
    
    @property
    def step_name(self) -> str:
        return "Setup Jobs & Firewall"
    
    @property
    def step_description(self) -> str:
        return "🔧 Setting up Jobs & Firewall..."
    
    def execute(self) -> bool:
        """Execute jobs and firewall setup"""
        self.log_start()
        
        try:
            # Setup Canvas init script
            self.console.print("[cyan]Setting up Canvas init script...[/cyan]")
            commands = [
                "sudo ln -sf /var/canvas/script/canvas_init /etc/init.d/canvas_init",
                "sudo update-rc.d canvas_init defaults",
                "sudo /etc/init.d/canvas_init start"
            ]
            
            for cmd in commands:
                self.run_command(cmd, "Canvas init setup")
            
            # Setup firewall rules
            self.console.print("[cyan]Configuring firewall rules...[/cyan]")
            firewall_ports = [
                ("80", "HTTP"),
                ("443", "HTTPS"),
                ("5432", "PostgreSQL"),
                ("3000", "Canvas Dev"),
                ("3001", "RCE API"),
                ("6379", "Redis"),
                ("8000", "Alternative HTTP"),
                ("ssh", "SSH")
            ]
            
            for port, desc in firewall_ports:
                self.run_command(f"sudo ufw allow {port}", f"Allowing {desc}")
            
            # Enable firewall
            self.run_command("sudo ufw --force enable", "Enabling firewall")
            self.run_command("sudo ufw reload", "Reloading firewall")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False