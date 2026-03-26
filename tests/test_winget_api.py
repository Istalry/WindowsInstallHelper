import pytest
from unittest.mock import patch, MagicMock
from migration_tool.core.winget_api import WingetAPI

@patch('subprocess.run')
def test_is_available_true(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    assert WingetAPI.is_available() is True
    mock_run.assert_called_once()
    assert "winget" in mock_run.call_args[0][0]

@patch('subprocess.run')
def test_is_available_false_exit_code(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_run.return_value = mock_result
    
    assert WingetAPI.is_available() is False

@patch('subprocess.run')
def test_is_available_not_found(mock_run):
    mock_run.side_effect = FileNotFoundError()
    assert WingetAPI.is_available() is False

@patch('subprocess.run')
def test_search_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    # Simulating a typical winget stdout response format
    mock_result.stdout = """
Name                  Id                Version          Match         Source
------------------------------------------------------------------------------
Mozilla Firefox       Mozilla.Firefox   115.0.0.0                      winget
"""
    mock_run.return_value = mock_result
    
    result = WingetAPI.search("Firefox")
    
    assert result is not None
    assert result["id"] == "Mozilla.Firefox"
    assert result["name"] == "Firefox"
    
@patch('subprocess.run')
def test_search_no_package(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "No package found matching input criteria."
    mock_run.return_value = mock_result
    
    result = WingetAPI.search("NonExistentApp")
    assert result is None

@patch('subprocess.run')
def test_install_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    success = WingetAPI.install("Mozilla.Firefox", location="D:\\Program Files\\Firefox")
    
    assert success is True
    # Verify command string construction
    cmd_args = mock_run.call_args[0][0]
    assert "Mozilla.Firefox" in cmd_args
    assert "--location" in cmd_args
    assert "D:\\Program Files\\Firefox" in cmd_args

@patch('subprocess.run')
def test_install_failure(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 1603 # Typical installer error code
    mock_result.stdout = "Installation failed."
    mock_run.return_value = mock_result
    
    success = WingetAPI.install("Mozilla.Firefox")
    assert success is False
