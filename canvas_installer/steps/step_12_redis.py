"""
Step 12: Setup Redis Cache
"""

from .base_step import BaseStep


class RedisStep(BaseStep):
    """Setup Redis cache server"""
    
    @property
    def step_name(self) -> str:
        return "Setup Redis Cache"
    
    @property
    def step_description(self) -> str:
        return "⚡ Setting up Redis Cache..."
    
    def execute(self) -> bool:
        """Execute Redis setup"""
        self.log_start()
        
        try:
            # Install Redis
            self.console.print("[cyan]Installing Redis server...[/cyan]")
            commands = [
                "sudo add-apt-repository -y ppa:chris-lea/redis-server",
                "sudo apt-get update",
                "sudo apt-get install -y redis-server"
            ]
            
            for cmd in commands:
                self.run_command(cmd, "Redis installation")
            
            # Start and enable Redis
            self.run_command("sudo systemctl start redis-server", "Starting Redis")
            self.run_command("sudo systemctl enable redis-server", "Enabling Redis")
            
            # Configure cache store
            self.console.print("[cyan]Configuring cache store...[/cyan]")
            cache_config = """test:
  cache_store: redis_cache_store
development:
  cache_store: redis_cache_store
production:
  cache_store: redis_cache_store"""
            
            self.write_config_file("/var/canvas/config/cache_store.yml", cache_config, sudo=True)
            
            # Configure Redis connection
            redis_config = """production:
  url:
    - redis://localhost

development:
  url:
    - redis://localhost

test:
  url:
    - redis://localhost"""
            
            self.write_config_file("/var/canvas/config/redis.yml", redis_config, sudo=True)
            
            # Restart Redis
            self.run_command("sudo systemctl restart redis-server", "Restarting Redis")
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False