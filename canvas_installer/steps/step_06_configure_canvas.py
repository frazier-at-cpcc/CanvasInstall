"""
Step 6: Configure Canvas Settings
"""

import secrets
from .base_step import BaseStep


class ConfigureCanvasStep(BaseStep):
    """Configure Canvas database, mail, and domain settings"""
    
    @property
    def step_name(self) -> str:
        return "Configure Database, Mail & Domain"
    
    @property
    def step_description(self) -> str:
        return "⚙️  Configuring Canvas..."
    
    def execute(self) -> bool:
        """Execute Canvas configuration"""
        self.log_start()
        
        try:
            config_dir = "/var/canvas/config"
            
            # Configure database.yml
            self.console.print("[cyan]Configuring database settings...[/cyan]")
            database_config = f"""production:
  adapter: postgresql
  encoding: unicode
  database: canvas_production
  pool: 5
  username: canvas
  password: {self.config.canvas_password}
  host: localhost
  timeout: 5000

development:
  adapter: postgresql
  encoding: unicode
  database: canvas_development
  pool: 5
  username: canvas
  password: {self.config.canvas_password}
  host: localhost
  timeout: 5000
"""
            self.write_config_file(f"{config_dir}/database.yml", database_config, sudo=True)
            
            # Configure dynamic_settings.yml
            self.console.print("[cyan]Configuring dynamic settings...[/cyan]")
            dynamic_config = f"""production:
  # tree
  store:
    canvas:
      rich-content-service:
        app-host: "{self.config.domain}"
  
development:
  store:
    canvas:
      rich-content-service:
        app-host: "http://localhost:3001"
"""
            self.write_config_file(f"{config_dir}/dynamic_settings.yml", dynamic_config, sudo=True)
            
            # Configure outgoing_mail.yml if SMTP details provided
            if self.config.smtp_server:
                self.console.print("[cyan]Configuring email settings...[/cyan]")
                mail_config = f"""production:
  address: {self.config.smtp_server}
  port: "{self.config.smtp_port}"
  enable_starttls_auto: false
  ssl: true
  user_name: "{self.config.smtp_username}"
  password: "{self.config.smtp_password}"
  authentication: cram_md5
  domain: {self.config.smtp_server}
  outgoing_address: "{self.config.smtp_from_email}"
  default_name: "{self.config.smtp_from_name}"

development:
  delivery_method: test
"""
                self.write_config_file(f"{config_dir}/outgoing_mail.yml", mail_config, sudo=True)
            
            # Configure domain.yml
            self.console.print("[cyan]Configuring domain settings...[/cyan]")
            domain_config = f"""production:
  domain: "{self.config.domain}"
  ssl: true
  files_domain: "files-{self.config.domain}"

development:
  domain: "canvas.localhost"
  ssl: false
"""
            self.write_config_file(f"{config_dir}/domain.yml", domain_config, sudo=True)
            
            # Configure security.yml
            self.console.print("[cyan]Configuring security settings...[/cyan]")
            encryption_key = secrets.token_hex(32)
            
            security_config = f"""production: &default
  encryption_key: {encryption_key}
  lti_iss: '{self.config.domain}'

development:
  <<: *default
"""
            self.write_config_file(f"{config_dir}/security.yml", security_config, sudo=True)
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False