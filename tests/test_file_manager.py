import os
import json
from pathlib import Path
from migration_tool.core.file_manager import FileManager

def test_export_json_success(tmp_path):
    """Verify that export_json correctly writes data to a file."""
    data = [{"name": "App1", "version": "1.0"}, {"name": "App2", "version": "2.0"}]
    filepath = tmp_path / "export.json"
    
    result = FileManager.export_json(str(filepath), data)
    
    assert result is True
    assert filepath.exists()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        
    assert saved_data == data

def test_export_json_failure(tmp_path):
    """Verify export_json handles invalid paths gracefully."""
    # Try to write to a directory that doesn't exist to force an IOError/PermissionError/FileNotFoundError
    invalid_path = tmp_path / "nonexistent_dir" / "export.json"
    
    result = FileManager.export_json(str(invalid_path), [])
    
    assert result is False

def test_import_json_success(tmp_path):
    """Verify that import_json correctly reads data from a file."""
    data = [{"name": "TestApp", "version": "1.2.3"}]
    filepath = tmp_path / "import.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        
    result = FileManager.import_json(str(filepath))
    
    assert result == data

def test_import_json_failure(tmp_path):
    """Verify import_json handles missing files gracefully."""
    filepath = tmp_path / "missing.json"
    
    result = FileManager.import_json(str(filepath))
    
    assert result == []

def test_scan_for_installers(tmp_path):
    """Verify that scan_for_installers finds .exe and .msi files but ignores others."""
    # Create some dummy files in the temporary directory
    (tmp_path / "installer1.exe").touch()
    (tmp_path / "INSTALLER2.MSI").touch()
    (tmp_path / "not_an_installer.txt").touch()
    
    # Create a subfolder with its own installer. 
    # Current codebase doesn't scan recursively, so this shouldn't be found.
    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()
    (subfolder / "installer3.exe").touch()
    
    result = FileManager.scan_for_installers(str(tmp_path))
    
    assert len(result) == 2
    assert "installer1.exe" in result
    assert "installer2.msi" in result
    
    # Ensure correct absolute paths are returned
    assert result["installer1.exe"] == str((tmp_path / "installer1.exe").absolute())
    assert result["installer2.msi"] == str((tmp_path / "INSTALLER2.MSI").absolute())

def test_scan_for_installers_invalid_dir(tmp_path):
    """Verify scan_for_installers handles invalid directory paths gracefully."""
    invalid_dir = str(tmp_path / "does_not_exist")
    result = FileManager.scan_for_installers(invalid_dir)
    assert result == {}

from unittest.mock import patch

@patch('pathlib.Path.iterdir')
def test_scan_for_installers_exception(mock_iterdir, tmp_path):
    """Verify scan_for_installers catches and logs OS Exceptions."""
    mock_iterdir.side_effect = Exception("OS Permission Error")
    result = FileManager.scan_for_installers(str(tmp_path))
    assert result == {}
