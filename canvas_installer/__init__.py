"""
Canvas LMS Automated Installer for Ubuntu 22.04
A comprehensive guided installer with TUI interface
"""

from .installer import CanvasInstaller
from .config import InstallationConfig

__version__ = "1.0.0"
__author__ = "Canvas Installer Team"

__all__ = ["CanvasInstaller", "InstallationConfig"]