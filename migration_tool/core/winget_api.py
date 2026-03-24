"""
Wrapper for Windows Package Manager (winget) commands.
"""

import subprocess
from typing import Dict, Optional
from ..utils.logger import logger

class WingetAPI:
    """Class to interact with the winget CLI."""
    
    @staticmethod
    def is_available() -> bool:
        """Checks if winget is available on the system."""
        try:
            result = subprocess.run(
                ["winget", "--version"], 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("Winget is not installed or not in PATH.")
            return False

    @staticmethod
    def search(query: str) -> Optional[Dict[str, str]]:
        """
        Searches for a package using winget.
        """
        logger.info(f"Searching winget for: {query}")
        try:
            cmd = ["winget", "search", query, "--accept-source-agreements", "--source", "winget"]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and "No package found" not in result.stdout:
                lines = result.stdout.splitlines()
                started = False
                for line in lines:
                    if line.startswith("---") or line.startswith("==="):
                        started = True
                        continue
                    if started and len(line.strip()) > 0:
                        parts = line.split()
                        if len(parts) >= 2:
                            for part in parts:
                                if "." in part and len(part) > 3:
                                    logger.info(f"Found match for {query}: {part}")
                                    return {"id": part, "name": query}
                            # fallback: take second column
                            logger.info(f"Found potential match for {query}: {parts[1]}")
                            return {"id": parts[1], "name": query}
            return None
        except Exception as e:
            logger.error(f"Error executing winget search for {query}: {e}")
            return None

    @staticmethod
    def install(package_id: str, location: Optional[str] = None) -> bool:
        """
        Installs a package silently using winget.
        """
        logger.info(f"Installing package via winget: {package_id}")
        try:
            # We remove --id to allow Winget to use Name or Moniker as a fallback search
            cmd = [
                "winget", "install", package_id, 
                "--silent", "--accept-package-agreements", "--accept-source-agreements"
            ]
            
            if location:
                cmd.extend(["--location", location])
                
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {package_id}")
                return True
            else:
                logger.error(f"Failed to install {package_id}. Exit code: {result.returncode}. Output: {result.stdout}")
                return False
        except Exception as e:
            logger.error(f"Error executing winget install for {package_id}: {e}")
            return False
