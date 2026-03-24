"""
Module responsible for scanning the Windows Registry to identify installed software.
"""

import winreg
from typing import List, Dict, Any, Optional
from ..utils.logger import logger
from ..utils.config import REGISTRY_PATHS, EXCLUDED_KEYWORDS

class RegistryScanner:
    """Class to handle Windows Registry scanning for installed applications."""
    
    def __init__(self):
        """Initialize the scanner."""
        self._installed_apps: List[Dict[str, str]] = []

    def scan(self) -> List[Dict[str, str]]:
        """
        Scans HKLM and HKCU registry hives for installed applications.
        
        Returns:
            list[dict]: A list of dictionaries containing 'name', 'version', and 'publisher'.
        """
        logger.info("Starting registry scan for installed applications.")
        self._installed_apps.clear()
        
        # Hive roots to check
        hives = [
            (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
            (winreg.HKEY_CURRENT_USER, "HKCU")
        ]
        
        for hive, hive_name in hives:
            for path in REGISTRY_PATHS:
                self._scan_key(hive, hive_name, path)
                
        # Remove duplicates based on Name
        unique_apps = {app['name']: app for app in self._installed_apps if app.get('name')}
        self._installed_apps = list(unique_apps.values())
        
        # Sort alphabetically
        self._installed_apps.sort(key=lambda x: x['name'].lower())
        
        logger.info(f"Registry scan completed. Found {len(self._installed_apps)} unique applications.")
        return self._installed_apps

    def _scan_key(self, hive: int, hive_name: str, path: str) -> None:
        """
        Scans a specific registry key and extracts application details.
        
        Args:
            hive (int): The registry hive constant (e.g., winreg.HKEY_LOCAL_MACHINE).
            hive_name (str): Label for the hive for logging.
            path (str): The subkey path to scan.
        """
        try:
            # We use KEY_READ and KEY_WOW64_64KEY to access the 64-bit registry branch
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        except OSError:
            logger.debug(f"Registry path not found: {hive_name}\\{path}")
            return

        try:
            num_subkeys = winreg.QueryInfoKey(key)[0]
            for i in range(num_subkeys):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    app_info = self._extract_app_info(subkey)
                    if app_info and self._is_valid_app(app_info):
                        self._installed_apps.append(app_info)
                        
                    winreg.CloseKey(subkey)
                except OSError:
                    continue
        except OSError as e:
            logger.error(f"Error enumerating keys in {hive_name}\\{path}: {e}")
        finally:
            winreg.CloseKey(key)

    def _extract_app_info(self, key: winreg.HKEYType) -> Optional[Dict[str, Any]]:
        """
        Extracts application name, version, and publisher from an open registry key.
        
        Args:
            key (HKEYType): Open registry key.
            
        Returns:
            Optional[dict]: Application details, or None if the key doesn't contain a Name.
        """
        app_info = {}
        try:
            app_info['name'], _ = winreg.QueryValueEx(key, "DisplayName")
        except OSError:
            return None # If there's no display name, we ignore it
            
        try:
            app_info['version'], _ = winreg.QueryValueEx(key, "DisplayVersion")
        except OSError:
            app_info['version'] = "Unknown"
            
        try:
            app_info['publisher'], _ = winreg.QueryValueEx(key, "Publisher")
        except OSError:
            app_info['publisher'] = "Unknown"
            
        return app_info

    def _is_valid_app(self, app_info: Dict[str, str]) -> bool:
        """
        Filters out system components and updates based on EXCLUDED_KEYWORDS.
        
        Args:
            app_info (dict): The application info dictionary.
            
        Returns:
            bool: True if the app should be included, False otherwise.
        """
        name = app_info.get('name', '').lower()
        if not name:
            return False
            
        for keyword in EXCLUDED_KEYWORDS:
            if keyword in name:
                # Uncomment the line below for super verbose debugging
                # logger.debug(f"Filtered out application: {app_info.get('name')} (matched keyword: {keyword})")
                return False
                
        return True
