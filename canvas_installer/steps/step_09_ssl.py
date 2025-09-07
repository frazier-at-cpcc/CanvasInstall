"""
Step 9: Setup SSL Certificate
"""

from .base_step import BaseStep


class SSLStep(BaseStep):
    """Setup SSL certificate with Let's Encrypt"""
    
    @property
    def step_name(self) -> str:
        return "Setup SSL Certificate"
    
    @property
    def step_description(self) -> str:
        return "🔒 Setting up SSL Certificate..."
    
    def execute(self) -> bool:
        """Execute SSL setup"""
        if self.config.skip_ssl:
            self.console.print("\n[yellow]⏭️  Skipping SSL setup[/yellow]")
            return True
            
        self.log_start()
        
        try:
            # Install Certbot
            self.console.print("[cyan]Installing Certbot...[/cyan]")
            commands = [
                "sudo apt update",
                "sudo apt install -y certbot python3-certbot-apache"
            ]
            
            for cmd in commands:
                self.run_command(cmd, "Certbot installation")
            
            # Get SSL certificate
            self.console.print("[cyan]Obtaining SSL certificate...[/cyan]")
            self.console.print(f"[yellow]Please follow the Certbot prompts for domain: {self.config.domain}[/yellow]")
            
            ssl_cmd = f"sudo certbot --apache -d {self.config.domain}"
            self.run_command(ssl_cmd, "Getting SSL certificate")
            
            # Setup auto-renewal
            self.console.print("[cyan]Setting up automatic renewal...[/cyan]")
            cron_job = "0 0 * * * /usr/bin/certbot renew --quiet"
            self.run_command(f'(crontab -l 2>/dev/null; echo "{cron_job}") | sudo crontab -', "Adding renewal cron job")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False