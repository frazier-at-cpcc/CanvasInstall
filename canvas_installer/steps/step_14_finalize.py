"""
Step 14: Finalize Installation
"""

from .base_step import BaseStep


class FinalizeStep(BaseStep):
    """Set permissions and final optimization"""
    
    @property
    def step_name(self) -> str:
        return "Set Permissions & Optimization"
    
    @property
    def step_description(self) -> str:
        return "🎯 Finalizing Installation..."
    
    def execute(self) -> bool:
        """Execute finalization steps"""
        self.log_start()
        
        try:
            # Set correct permissions
            self.console.print("[cyan]Setting file permissions...[/cyan]")
            commands = [
                "cd /var/canvas && sudo chown -R canvas:canvas .",
                "sudo find /var/canvas/config/ -type f -exec chmod 400 {} +"
            ]
            
            for cmd in commands:
                self.run_command(cmd, "Setting permissions")
            
            # Optional: Setup X-Sendfile optimization
            if not self.config.skip_optimization:
                self.console.print("[cyan]Setting up file download optimization...[/cyan]")
                opt_commands = [
                    "sudo apt-get install -y libapache2-mod-xsendfile",
                    "sudo systemctl reload apache2"
                ]
                
                for cmd in opt_commands:
                    self.run_command(cmd, "Optimization setup")
                
                # Create production-local.rb config
                prod_local_config = """# X-Sendfile optimization for file downloads
config.action_dispatch.x_sendfile_header = 'X-Sendfile'"""
                
                self.write_config_file("/var/canvas/config/environments/production-local.rb", prod_local_config, sudo=True)
            
            # Final system restart
            self.console.print("[cyan]Performing final system restart...[/cyan]")
            self.run_command("sudo systemctl restart apache2", "Restarting Apache")
            self.run_command("sudo systemctl restart redis-server", "Restarting Redis")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False