"""
Step 4: Install Development Tools
"""

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
try:
    from rich.progress import TaskProgressColumn
    HAS_TASK_PROGRESS = True
except ImportError:
    HAS_TASK_PROGRESS = False
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
            progress_columns = [
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn()
            ]
            if HAS_TASK_PROGRESS:
                progress_columns.append(TaskProgressColumn())
                
            with Progress(*progress_columns, transient=True) as progress:
                
                total_steps = 8
                task = progress.add_task("Installing development tools...", total=total_steps)
                
                # Step 1: Install basic packages
                basic_steps = [
                    ("sudo apt-get install -y git-core", "Installing Git"),
                    ("sudo apt-get install -y software-properties-common", "Installing software properties"),
                    ("sudo add-apt-repository -y ppa:instructure/ruby", "Adding Ruby PPA"),
                    ("sudo apt-get update", "Updating package lists"),
                    ("sudo apt-get install -y ruby3.3 ruby3.3-dev zlib1g-dev libxml2-dev libsqlite3-dev postgresql libpq-dev libxmlsec1-dev libidn11-dev curl make g++", "Installing Ruby and dependencies")
                ]
                
                for i, (cmd, desc) in enumerate(basic_steps):
                    progress.update(task, description=desc, completed=i)
                    self.run_command(cmd, desc)
                    progress.update(task, completed=i+1)
                
                # Step 2: Install NVM and Node.js with proper permissions
                progress.update(task, description="Installing NVM and Node.js...", completed=5)
                nvm_node_cmd = '''bash -c "
                    # Install NVM
                    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash &&
                    
                    # Fix permissions if needed
                    chmod +x $HOME/.nvm/nvm.sh &&
                    
                    # Load NVM and install Node.js
                    export NVM_DIR=\"$HOME/.nvm\" &&
                    [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" &&
                    nvm install 18.20 &&
                    nvm use 18.20 &&
                    node --version &&
                    npm --version
                "'''
                self.run_command(nvm_node_cmd, "Installing NVM and Node.js")
                progress.update(task, completed=6)
                
                # Step 3: Install Yarn with Node.js available and clean install
                progress.update(task, description="Installing Yarn...", completed=6)
                yarn_cmd = '''bash -c "
                    # Clean any existing Yarn installation
                    rm -rf $HOME/.yarn 2>/dev/null || true &&
                    
                    # Load NVM and install Yarn
                    export NVM_DIR=\"$HOME/.nvm\" &&
                    [ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\" &&
                    nvm use 18.20 &&
                    curl -o- -L https://yarnpkg.com/install.sh | bash -s -- --version 1.19.1 &&
                    
                    # Verify installation
                    export PATH=\"$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH\" &&
                    yarn --version
                "'''
                self.run_command(yarn_cmd, "Installing Yarn")
                progress.update(task, completed=7)
                
                # Step 4: Create environment setup script
                progress.update(task, description="Setting up environment...", completed=7)
                env_setup = '''cat >> ~/.bashrc << 'EOF'
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"
EOF'''
                self.run_command(env_setup, "Setting up environment")
                progress.update(task, completed=8)
            
            self.log_success()
            return True
            
        except Exception as e:
            self.log_failure(e)
            return False