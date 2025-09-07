"""
Step 4: Install Development Tools
"""

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from .base_step import BaseStep


class DevToolsStep(BaseStep):
    """Install Git, Ruby, Node.js, and Yarn"""
    
    @property
    def step_name(self) -> str:
        return "Install Git, Ruby, Node.js & Yarn"
    
    @property
    def step_description(self) -> str:
        return "🛠️  Installing Development Tools..."
    
    def execute(self) -> bool:
        """Execute development tools installation"""
        self.log_start()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                transient=True
            ) as progress:
                
                total_steps = 8
                task = progress.add_task("Installing development tools...", total=total_steps)
                
                steps = [
                    ("sudo apt-get install -y git-core", "Installing Git"),
                    ("sudo apt-get install -y software-properties-common", "Installing software properties"),
                    ("sudo add-apt-repository -y ppa:instructure/ruby", "Adding Ruby PPA"),
                    ("sudo apt-get update", "Updating package lists"),
                    ("sudo apt-get install -y ruby3.3 ruby3.3-dev zlib1g-dev libxml2-dev libsqlite3-dev postgresql libpq-dev libxmlsec1-dev libidn11-dev curl make g++", "Installing Ruby and dependencies"),
                    ("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash", "Installing NVM"),
                    ("bash -c 'export NVM_DIR=\"$HOME/.nvm\" && [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" && nvm install 18.20'", "Installing Node.js 18.20"),
                    ("curl -o- -L https://yarnpkg.com/install.sh | bash -s -- --version 1.19.1", "Installing Yarn")
                ]
                
                for i, (cmd, desc) in enumerate(steps):
                    progress.update(task, description=desc, completed=i)
                    self.run_command(cmd, desc)
                    progress.update(task, completed=i+1)
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False