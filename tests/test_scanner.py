import pytest
from unittest.mock import MagicMock, patch
from migration_tool.core.scanner import RegistryScanner

@pytest.fixture
def scanner():
    return RegistryScanner()

def test_is_valid_app_success(scanner):
    app_info = {"name": "My Valid Application", "version": "1.0", "publisher": "Me"}
    assert scanner._is_valid_app(app_info) is True

def test_is_valid_app_excluded(scanner):
    # Tests that filtering works (e.g. "kb" or "update")
    app_info1 = {"name": "KB5001234 Security Update", "version": "1.0"}
    app_info2 = {"name": "Microsoft Visual C++ 2015 Redistributable"}
    
    assert scanner._is_valid_app(app_info1) is False
    assert scanner._is_valid_app(app_info2) is False

def test_is_valid_app_empty(scanner):
    assert scanner._is_valid_app({}) is False
    assert scanner._is_valid_app({"name": ""}) is False

@patch('migration_tool.core.scanner.winreg')
def test_extract_app_info_success(mock_winreg, scanner):
    # Mock behavior of QueryValueEx to simulate generic registry reads
    def side_effect(key, value_name):
        if value_name == "DisplayName":
            return ("Test Application", 1)
        elif value_name == "DisplayVersion":
            return ("2.5.0", 1)
        elif value_name == "Publisher":
            return ("Test Publisher", 1)
        raise OSError("Value not found")
        
    mock_winreg.QueryValueEx.side_effect = side_effect
    
    mock_key = MagicMock()
    app_info = scanner._extract_app_info(mock_key)
    
    assert app_info is not None
    assert app_info['name'] == "Test Application"
    assert app_info['version'] == "2.5.0"
    assert app_info['publisher'] == "Test Publisher"

@patch('migration_tool.core.scanner.winreg')
def test_extract_app_info_no_name(mock_winreg, scanner):
    # If DisplayName is missing, it should return None
    mock_winreg.QueryValueEx.side_effect = OSError("Value not found")
    
    mock_key = MagicMock()
    app_info = scanner._extract_app_info(mock_key)
    
    assert app_info is None

@patch('migration_tool.core.scanner.winreg')
def test_scan_key(mock_winreg, scanner):
    # Let's say we have 1 subkey inside our mocked path
    mock_winreg.QueryInfoKey.return_value = (1, 0, 0)
    mock_winreg.EnumKey.return_value = "SubKey1"
    
    # Mocking extraction
    def query_side_effect(key, value_name):
        if value_name == "DisplayName":
            return ("Mock App", 1)
        raise OSError()
    
    mock_winreg.QueryValueEx.side_effect = query_side_effect
    
    # Setup standard mocked OpenKey that succeeds
    mock_winreg.OpenKey.return_value = MagicMock()
    
    scanner._scan_key(mock_winreg.HKEY_LOCAL_MACHINE, "HKLM", "Software\\Test")
    
    # It should have added 1 app
    assert len(scanner._installed_apps) == 1
    assert scanner._installed_apps[0]["name"] == "Mock App"

@patch('migration_tool.core.scanner.winreg')
def test_scan_key_not_found(mock_winreg, scanner):
    # Simulate a non-existent registry path
    mock_winreg.OpenKey.side_effect = OSError("Path not found")
    
    # Should not crash, just return without adding apps
    scanner._scan_key(mock_winreg.HKEY_LOCAL_MACHINE, "HKLM", "Software\\NonExistent")
    assert len(scanner._installed_apps) == 0

@patch.object(RegistryScanner, '_scan_key')
def test_scan_main_method(mock_scan_key, scanner):
    # Simulate that we found some apps when _scan_key is called
    def populate_apps(*args, **kwargs):
        scanner._installed_apps.append({"name": "B App", "version": "1.0", "publisher": "P1"})
        scanner._installed_apps.append({"name": "Z App", "version": "0.1", "publisher": "P3"})
        scanner._installed_apps.append({"name": "A App", "version": "2.0", "publisher": "P2"})
        # Duplicate to test deduplication
        scanner._installed_apps.append({"name": "A App", "version": "2.0", "publisher": "P2"})
        
    mock_scan_key.side_effect = populate_apps
    
    apps = scanner.scan()
    
    # Deduplication and Alphabetical Sorting
    assert len(apps) == 3
    assert apps[0]["name"] == "A App"
    assert apps[1]["name"] == "B App"
    assert apps[2]["name"] == "Z App"
