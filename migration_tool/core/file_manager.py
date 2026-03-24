"""
File manager module for handling JSON import/export and local folder scanning.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from ..utils.logger import logger

class FileManager:
    """Handles JSON persistence and local file scanning."""

    @staticmethod
    def export_json(filepath: str, data: List[Dict[str, Any]]) -> bool:
        """
        Exports the selected applications to a JSON file.
        
        Args:
            filepath (str): The destination file path.
            data (list): List of dictionaries containing application info.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Exporting data to JSON: {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("Export successful.")
            return True
        except Exception as e:
            logger.error(f"Error exporting JSON to {filepath}: {e}")
            return False

    @staticmethod
    def import_json(filepath: str) -> List[Dict[str, Any]]:
        """
        Imports applications from a JSON file.
        
        Args:
            filepath (str): The source JSON file path.
            
        Returns:
            list: List of dictionaries containing application info. Empty if error.
        """
        logger.info(f"Importing data from JSON: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Import successful. Loaded {len(data)} items.")
            return data
        except Exception as e:
            logger.error(f"Error importing JSON from {filepath}: {e}")
            return []

    @staticmethod
    def scan_for_installers(directory: str) -> Dict[str, str]:
        """
        Scans a directory for .exe and .msi files to automatically link them.
        
        Args:
            directory (str): The folder path to scan.
            
        Returns:
            dict: Mapping of installer filenames (without extension or lowercase) to their full paths.
        """
        logger.info(f"Scanning directory for installers: {directory}")
        installers = {}
        target_dir = Path(directory)
        
        if not target_dir.is_dir():
            logger.warning(f"Directory not found: {directory}")
            return installers
            
        try:
            for file_path in target_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ['.exe', '.msi']:
                    # We store the base filename lowercase as key, to help exact matches if possible
                    installers[file_path.name.lower()] = str(file_path.absolute())
            
            logger.info(f"Found {len(installers)} potential installers in directory.")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            
        return installers
