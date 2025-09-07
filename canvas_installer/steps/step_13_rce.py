"""
Step 13: Setup Rich Content Editor
"""

import secrets
from .base_step import BaseStep


class RCEStep(BaseStep):
    """Setup Rich Content Editor API"""
    
    @property
    def step_name(self) -> str:
        return "Enable Rich Content Editor"
    
    @property
    def step_description(self) -> str:
        return "📝 Setting up Rich Content Editor..."
    
    def execute(self) -> bool:
        """Execute RCE setup"""
        if self.config.skip_rce:
            self.console.print("\n[yellow]⏭️  Skipping Rich Content Editor setup[/yellow]")
            return True
            
        self.log_start()
        
        try:
            # Clone RCE API with proper ownership handling
            self.console.print("[cyan]Cloning Canvas RCE API...[/cyan]")
            
            # Step 1: Clone RCE repository with Git configuration
            clone_cmd = '''bash -c "
                # Configure Git for root user
                git config --global --add safe.directory '*' &&
                
                # Clone RCE API
                cd /var &&
                git clone https://github.com/instructure/canvas-rce-api.git &&
                
                # Set proper ownership immediately
                chown -R canvas:canvas /var/canvas-rce-api
            "'''
            
            self.run_command(clone_cmd, "Cloning RCE API repository", timeout=300)
            
            # Step 2: Install npm packages as canvas user
            npm_cmd = '''bash -c "
                cd /var/canvas-rce-api &&
                sudo -u canvas npm install --production &&
                sudo -u canvas npm audit fix --force
            "'''
            
            self.run_command(npm_cmd, "Installing RCE API dependencies", timeout=900)
            
            # Generate secrets
            self.console.print("[cyan]Generating RCE secrets...[/cyan]")
            ecosystem_secret = secrets.token_hex(32)
            ecosystem_key = secrets.token_hex(32)
            cipher_password = secrets.token_hex(16)
            
            # Create .env file for RCE API
            rce_env = f"""NODE_ENV=production
ECOSYSTEM_SECRET={ecosystem_secret}
ECOSYSTEM_KEY={ecosystem_key}
CIPHER_PASSWORD={cipher_password}
FLICKR_API_KEY={self.config.flickr_api_key}
YOUTUBE_API_KEY={self.config.youtube_api_key}"""
            
            self.write_config_file("/var/canvas-rce-api/.env", rce_env, sudo=True)
            
            # Configure vault_contents.yml
            self.console.print("[cyan]Configuring Canvas vault contents...[/cyan]")
            vault_config = f"""production:
  'sts/testaccount/sts/canvas-shards-lookupper-dev':
    access_key: 'fake-access-key'
    secret_key: 'fake-secret-key'
    security_token: 'fake-security-token'
  'sts/testaccount/sts/canvas-release-notes':
    access_key: 'fake-access-key'
    secret_key: 'fake-secret-key'
    security_token: 'fake-security-token'
  'app-canvas/data/secrets':
    data:
      canvas_security:
        encryption_secret: "{ecosystem_key}"
        signing_secret: "{ecosystem_secret}"
"""
            
            self.write_config_file("/var/canvas/config/vault_contents.yml", vault_config, sudo=True)
            
            # Install screen for background process
            self.run_command("sudo apt install -y screen", "Installing screen")
            
            self.log_success()
            self.console.print("[yellow]Note: You'll need to manually start the RCE server with:[/yellow]")
            self.console.print("[dim]cd /var/canvas-rce-api && screen -S canvas-rce-api npm start[/dim]")
            
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False