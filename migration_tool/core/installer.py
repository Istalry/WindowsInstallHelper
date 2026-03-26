"""
Moteur d'exécution des installations batch.
"""

import subprocess
import time
from typing import List, Dict, Callable, Any
from .winget_api import WingetAPI
from ..utils.logger import logger

class BatchInstaller:
    """Manages the sequential installation of multiple applications."""
    
    def __init__(self):
        self._cancel_requested = False
        
    def cancel(self):
        """Requests cancellation of the ongoing batch installation."""
        self._cancel_requested = True
        logger.info("Batch installation cancel requested.")

    def run_batch(self, 
                  apps: List[Dict[str, Any]], 
                  progress_callback: Callable[[int, int, str], None],
                  item_completion_callback: Callable[[int, bool, str], None] = None,
                  location: str = None) -> None:
        """
        Iterates over the list of apps and installs them.
        
        Args:
            apps (list): List of apps to install. Each dictionary must have:
                         - 'name': The name of the software
                         - 'install_method': 'winget' or 'local'
                         - 'winget_id': (optional) ID if method is winget
                         - 'local_path': (optional) Path if method is local
            progress_callback (callable): Function to update UI (current, total, status_text).
            item_completion_callback (callable, optional): Function to notify UI of individual app success/failure (index, success, error_msg).
            location (str, optional): Target installation drive/folder.
        """
        total = len(apps)
        logger.info(f"Starting batch installation for {total} applications.")
        
        for index, app in enumerate(apps):
            if self._cancel_requested:
                logger.info("Batch installation cancelled.")
                progress_callback(index, total, "Installation cancelled.")
                break
                
            name = app.get('name', 'Unknown')
            method = app.get('install_method')
            
            progress_callback(index, total, f"Installing {name}...")
            
            success = False
            install_drive = app.get('install_drive', 'C:\\')
            # Let's cleanly join the drive and Program Files as a fallback directory construct
            import os
            import re
            safe_name = re.sub(r'[\\/*?:"<>|]', "", name)
            app_location = os.path.join(install_drive, "Program Files", safe_name)
            
            if method == 'winget':
                winget_id = app.get('winget_id')
                if winget_id:
                    success = WingetAPI.install(winget_id, app_location)
                else:
                    logger.error(f"Cannot install {name} via winget: No ID provided.")
            elif method == 'local':
                local_path = app.get('local_path')
                if local_path:
                    success = self._install_local(name, local_path, app_location)
                else:
                    logger.error(f"Cannot install {name} locally: No path provided.")
            else:
                logger.warning(f"Skipping {name}: Unknown or unselected installation method '{method}'")
                success = True # Skip means we just move on
                
            if not success:
                logger.error(f"Failed to install {name}.")
                if item_completion_callback:
                    item_completion_callback(index, False, "Failed")
            else:
                logger.info(f"Finished processing {name}.")
                if item_completion_callback:
                    item_completion_callback(index, True, "Success")
                
            # Keep UI responsive and don't spam subprocesses too quickly
            time.sleep(1)
            
        if not self._cancel_requested:
            progress_callback(total, total, "Batch installation completed.")

    def _install_local(self, name: str, filepath: str, location: str) -> bool:
        """
        Executes a local installer. 
        Note: Silent arguments for local installers vary wildly (.exe vs .msi).
        We will attempt standard passive execution for MSI and silent flags string matching for EXE.
        """
        logger.info(f"Running local installer for {name}: {filepath} at {location}")
        try:
            cmd = [filepath]
            if filepath.lower().endswith(".msi"):
                cmd = ["msiexec.exe", "/i", filepath, "/passive", "/norestart", f"INSTALLDIR={location}"]
            elif filepath.lower().endswith(".exe"):
                # Detect installer type by reading binary header
                cmd = [filepath, "/S", f"/D={location}"] # Default fallback (NSIS style)
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(1024 * 500) # Check first 500kb
                        if b"Inno Setup" in header:
                            cmd = [filepath, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", f"/DIR={location}"]
                            logger.debug(f"Detected InnoSetup for {name}")
                        elif b"Nullsoft" in header or b"NSIS" in header:
                            cmd = [filepath, "/S", f"/D={location}"]
                            logger.debug(f"Detected NSIS for {name}")
                        elif b"WiX" in header or b"wix" in header:
                            cmd = [filepath, "/quiet", "-norestart"]
                            logger.debug(f"Detected WiX for {name}")
                except Exception as e:
                    logger.warning(f"Could not read installer heuristics for {name}: {e}")
                
            logger.debug(f"Executing command: {cmd}")
            process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            process.wait()
            
            logger.info(f"Local installer for {name} finished with return code {process.returncode}.")
            return True
        except Exception as e:
            logger.error(f"Error executing local installer {filepath}: {e}")
            return False
