"""
Base class for installation steps
"""

from abc import ABC, abstractmethod
from rich.console import Console
from rich.progress import Progress
import logging

from ..config import InstallationConfig
from ..utils import CommandRunner


class BaseStep(ABC):
    """Base class for all installation steps"""
    
    def __init__(self, config: InstallationConfig, console: Console, logger: logging.Logger):
        self.config = config
        self.console = console
        self.logger = logger
        self.cmd_runner = CommandRunner(logger)
    
    @property
    @abstractmethod
    def step_name(self) -> str:
        """Return the name of this step"""
        pass
    
    @property
    @abstractmethod
    def step_description(self) -> str:
        """Return a description of what this step does"""
        pass
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the installation step. Returns True if successful, False otherwise."""
        pass
    
    def log_start(self):
        """Log the start of this step"""
        self.console.print(f"\n[bold yellow]{self.step_description}[/bold yellow]")
        self.logger.info(f"Starting step: {self.step_name}")
    
    def log_success(self):
        """Log successful completion of this step"""
        self.console.print(f"[green]✅ {self.step_name} completed successfully[/green]")
        self.logger.info(f"Step completed successfully: {self.step_name}")
    
    def log_failure(self, error: Exception):
        """Log failure of this step"""
        self.console.print(f"[red]❌ {self.step_name} failed: {error}[/red]")
        self.logger.error(f"Step failed: {self.step_name} - {error}")
    
    def run_command(self, command: str, description: str = "", show_output: bool = True, timeout: int = 600):
        """Convenience method to run a command"""
        return self.cmd_runner.run_command(command, description, show_output, timeout)
    
    def write_config_file(self, filepath: str, content: str, sudo: bool = False):
        """Convenience method to write a config file"""
        self.cmd_runner.write_config_file(filepath, content, sudo)