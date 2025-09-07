"""
Step 10: Configure Virtual Hosts
"""

from .base_step import BaseStep


class VirtualHostsStep(BaseStep):
    """Configure Apache virtual hosts for Canvas"""
    
    @property
    def step_name(self) -> str:
        return "Configure Virtual Hosts"
    
    @property
    def step_description(self) -> str:
        return "🏠 Configuring Virtual Hosts..."
    
    def execute(self) -> bool:
        """Execute virtual hosts configuration"""
        self.log_start()
        
        try:
            # Disable default sites
            self.console.print("[cyan]Disabling default Apache sites...[/cyan]")
            default_sites = ["000-default", "default-ssl", "000-default-le-ssl"]
            for site in default_sites:
                self.run_command(f"sudo a2dissite {site} 2>/dev/null || true", f"Disabling {site}")
            
            # Create Canvas HTTP virtual host
            self.console.print("[cyan]Creating Canvas virtual host...[/cyan]")
            http_vhost = f"""<VirtualHost *:80>
    ServerName {self.config.domain}
    DocumentRoot /var/canvas/public
    PassengerRuby /usr/bin/ruby3.3
    PassengerAppEnv production
    RailsEnv production
    <Directory /var/canvas/public>
        AllowOverride all
        Options -MultiViews
        Require all granted
    </Directory>
</VirtualHost>"""
            
            self.write_config_file("/etc/apache2/sites-available/canvas.conf", http_vhost, sudo=True)
            
            # Create Canvas HTTPS virtual host if SSL is enabled
            if not self.config.skip_ssl:
                self.console.print("[cyan]Creating Canvas HTTPS virtual host...[/cyan]")
                https_vhost = f"""<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName {self.config.domain}
    DocumentRoot /var/canvas/public
    PassengerRuby /usr/bin/ruby3.3
    PassengerAppEnv production
    RailsEnv production
    SSLEngine On
    SSLCertificateFile /etc/letsencrypt/live/{self.config.domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{self.config.domain}/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf
    <Directory /var/canvas/public>
        AllowOverride all
        Options -MultiViews
        Require all granted
    </Directory>
    XSendFile On
    XSendFilePath /var/canvas
    
    # Proxy for Rich Content Editor
    ProxyPass /api/session http://localhost:3001/api/session
    ProxyPassReverse /api/session http://localhost:3001/api/session
</VirtualHost>
</IfModule>"""
                
                self.write_config_file("/etc/apache2/sites-available/canvas-ssl.conf", https_vhost, sudo=True)
                self.run_command("sudo a2ensite canvas-ssl.conf", "Enabling HTTPS site")
            
            # Enable Canvas site
            self.run_command("sudo a2ensite canvas.conf", "Enabling Canvas HTTP site")
            
            # Restart Apache
            self.run_command("sudo systemctl restart apache2", "Restarting Apache")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False