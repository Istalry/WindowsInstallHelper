"""
Configuration and constants for the Windows Install Helper.
"""

import os
from pathlib import Path

# Application variables
APP_NAME = "Windows Install Helper"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = Path(os.environ.get("TEMP", "C:/Windows/Temp"))
LOG_FILE = TEMP_DIR / "migration_tool.log"

# Registry Paths to scan
REGISTRY_PATHS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
]

# Excluded keywords for filtering system components and updates
EXCLUDED_KEYWORDS = [
    "kb", 
    "security update", 
    "update for windows", 
    "microsoft .net", 
    "microsoft visual c++", 
    "redistributable", 
    "runtime", 
    "service pack", 
    "windows driver package",
    "intel(r)",
    "amd",
    "nvidia",
    "realtek"
]
