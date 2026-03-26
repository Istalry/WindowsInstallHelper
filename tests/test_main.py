import pytest
from unittest.mock import patch, MagicMock
from migration_tool.main import main, is_admin

@patch('migration_tool.main.ctypes')
def test_is_admin_true(mock_ctypes):
    mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = True
    assert is_admin() is True

@patch('migration_tool.main.ctypes')
def test_is_admin_false(mock_ctypes):
    mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = False
    assert is_admin() is False

@patch('migration_tool.main.ctypes')
def test_is_admin_exception(mock_ctypes):
    # Test fallback if ctypes throws an error
    mock_ctypes.windll.shell32.IsUserAnAdmin.side_effect = Exception("Simulated Failure")
    assert is_admin() is False

@patch('migration_tool.main.is_admin')
@patch('migration_tool.main.messagebox')
@patch('migration_tool.main.tk.Tk')
@patch('migration_tool.main.AppWindow')
def test_main_as_admin(mock_appwindow, mock_tk, mock_msgbox, mock_is_admin):
    # Scenario: User is administrator
    mock_is_admin.return_value = True
    
    main()
    
    mock_is_admin.assert_called_once()
    mock_msgbox.showwarning.assert_not_called()
    mock_appwindow.assert_called_once()
    mock_appwindow.return_value.mainloop.assert_called_once()

@patch('migration_tool.main.is_admin')
@patch('migration_tool.main.messagebox')
@patch('migration_tool.main.tk.Tk')
@patch('migration_tool.main.AppWindow')
def test_main_not_admin(mock_appwindow, mock_tk, mock_msgbox, mock_is_admin):
    # Scenario: User is NOT administrator
    mock_is_admin.return_value = False
    
    main()
    
    mock_is_admin.assert_called_once()
    mock_tk.assert_called_once()
    mock_msgbox.showwarning.assert_called_once()
    mock_appwindow.assert_called_once()
    mock_appwindow.return_value.mainloop.assert_called_once()
