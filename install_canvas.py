#!/usr/bin/env python3
"""
Canvas LMS Installer Entry Point
Run this script to start the Canvas LMS installation process
"""

import sys
import os

# Add the canvas_installer package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from canvas_installer.installer import main

if __name__ == "__main__":
    main()