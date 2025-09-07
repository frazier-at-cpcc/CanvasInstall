"""
Utility functions for Canvas LMS installer
"""

import os
import subprocess
import logging
from typing import Tuple


class CommandRunner:
    """Utility class for running shell commands with logging and error handling"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def run_command(self, command: str, description: str = "", show_output: bool = True, timeout: int = 600) -> subprocess.CompletedProcess:
        """Execute a shell command with logging and error handling"""
        self.logger.info(f"Executing: {description or command}")
        
        try:
            if show_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    timeout=timeout,
                    text=True,
                    capture_output=False
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    timeout=timeout,
                    text=True,
                    capture_output=True
                )
            
            self.logger.info(f"Command completed successfully: {description or command}")
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {description or command} - Exit code: {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {description or command}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error running command: {description or command} - {e}")
            raise

    def write_config_file(self, filepath: str, content: str, sudo: bool = False):
        """Write configuration file with proper permissions"""
        if sudo:
            # Use sudo to write the file
            cmd = f'echo "{content}" | sudo tee {filepath} > /dev/null'
            self.run_command(cmd, f"Writing config file {filepath}")
            self.run_command(f"sudo chown canvas:canvas {filepath}", f"Setting ownership for {filepath}")
        else:
            # Write file directly
            with open(filepath, 'w') as f:
                f.write(content)


class SystemChecker:
    """Utility class for checking system requirements"""
    
    @staticmethod
    def check_ubuntu_version() -> Tuple[bool, str]:
        """Check if running Ubuntu 22.04"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'Ubuntu' in content and '22.04' in content:
                    return True, "Ubuntu 22.04 LTS detected"
                else:
                    return False, "Ubuntu 22.04 LTS required"
        except:
            return False, "Cannot determine OS version"

    @staticmethod
    def check_sudo_access() -> Tuple[bool, str]:
        """Check sudo access"""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
            if result.returncode == 0:
                return True, "Sudo access confirmed"
            else:
                return False, "Sudo access required"
        except:
            return False, "Cannot verify sudo access"

    @staticmethod
    def check_hardware() -> Tuple[bool, str]:
        """Check hardware requirements"""
        try:
            # Check RAM (8GB = 8,000,000 KB approximately)
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_kb = int(line.split()[1])
                        mem_gb = mem_kb / 1024 / 1024
                        if mem_gb < 7.5:  # Allow some margin
                            return False, f"RAM: {mem_gb:.1f}GB (8GB required)"
                        break
            
            # Check CPU cores
            cpu_count = os.cpu_count()
            if cpu_count < 4:
                return False, f"CPU: {cpu_count} cores (4 required)"
            
            return True, f"RAM: {mem_gb:.1f}GB, CPU: {cpu_count} cores"
        except:
            return False, "Cannot verify hardware specs"

    @staticmethod
    def check_internet() -> Tuple[bool, str]:
        """Check internet connectivity"""
        try:
            result = subprocess.run(['ping', '-c', '1', 'google.com'], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                return True, "Internet connection verified"
            else:
                return False, "No internet connection"
        except:
            return False, "Cannot verify internet connection"

    @staticmethod
    def check_disk_space() -> Tuple[bool, str]:
        """Check available disk space"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                available = parts[3]
                # Parse available space (e.g., "50G" -> 50)
                if 'G' in available:
                    available_gb = float(available.replace('G', ''))
                    if available_gb < 30:
                        return False, f"Available: {available} (30GB required)"
                    return True, f"Available: {available}"
            return False, "Cannot determine disk space"
        except:
            return False, "Cannot check disk space"