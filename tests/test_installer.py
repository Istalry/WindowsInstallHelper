import pytest
from unittest.mock import MagicMock, call, patch
from migration_tool.core.installer import BatchInstaller

@pytest.fixture
def installer():
    """Returns a BatchInstaller instance with time.sleep mocked to run tests fast."""
    with patch('time.sleep', return_value=None):
        yield BatchInstaller()

def test_cancel_installation(installer):
    """Verify that cancellation flag works."""
    installer.cancel()
    assert installer._cancel_requested is True

@patch('migration_tool.core.installer.WingetAPI.install')
def test_run_batch_winget(mock_install, installer):
    """Verify run_batch works for winget method."""
    mock_install.return_value = True
    
    apps = [
        {"name": "App1", "install_method": "winget", "winget_id": "App.One"},
        {"name": "App2", "install_method": "winget", "winget_id": "App.Two"}
    ]
    callback = MagicMock()
    item_callback = MagicMock()
    
    installer.run_batch(apps, progress_callback=callback, item_completion_callback=item_callback)
    
    assert mock_install.call_count == 2
    # Check that callback was called correctly
    assert callback.call_count == 3 # 2 times for apps + 1 time for completion
    
    # Check item completion callback
    item_callback.assert_any_call(0, True, "Success")
    item_callback.assert_any_call(1, True, "Success")
    
@patch('migration_tool.core.installer.WingetAPI.install')
def test_run_batch_failure_callback(mock_install, installer):
    """Verify item_completion_callback reports failures correctly."""
    mock_install.side_effect = [True, False] # 1st success, 2nd fails
    
    apps = [
        {"name": "App1", "install_method": "winget", "winget_id": "App.One"},
        {"name": "App2", "install_method": "winget", "winget_id": "App.Two"}
    ]
    callback = MagicMock()
    item_callback = MagicMock()
    
    installer.run_batch(apps, progress_callback=callback, item_completion_callback=item_callback)
    
    assert mock_install.call_count == 2
    
    # Check item completion callback
    item_callback.assert_any_call(0, True, "Success")
    item_callback.assert_any_call(1, False, "Failed")
    
@patch.object(BatchInstaller, '_install_local')
def test_run_batch_local(mock_local, installer):
    """Verify run_batch works for local method."""
    mock_local.return_value = True
    
    apps = [
        {"name": "App Local", "install_method": "local", "local_path": "C:\\path\\installer.exe"}
    ]
    callback = MagicMock()
    item_callback = MagicMock()
    
    installer.run_batch(apps, progress_callback=callback, item_completion_callback=item_callback)
    
    mock_local.assert_called_once()
    assert mock_local.call_args[0][0] == "App Local"
    assert mock_local.call_args[0][1] == "C:\\path\\installer.exe"
    
    item_callback.assert_called_once_with(0, True, "Success")

@patch('migration_tool.core.installer.WingetAPI.install')
def test_run_batch_cancellation(mock_install, installer):
    """Verify run_batch stops when cancellation is requested mid-process."""
    mock_install.return_value = True
    
    apps = [
        {"name": "App1", "install_method": "winget", "winget_id": "App.One"},
        {"name": "App2", "install_method": "winget", "winget_id": "App.Two"}
    ]
    
    # We create a side_effect for the callback that cancels the installer
    # as soon as the first app starts
    def callback_side_effect(current, total, msg):
        if current == 0:
            installer.cancel()
            
    callback = MagicMock(side_effect=callback_side_effect)
    
    installer.run_batch(apps, progress_callback=callback)
    
    # WingetAPI should only be called once because it cancelled before App2
    assert mock_install.call_count == 1
    # Check that cancellation message was sent (index 1 is where it breaks)
    callback.assert_has_calls([call(1, 2, "Installation cancelled.")])

@patch('subprocess.Popen')
def test_install_local_exe(mock_popen, installer):
    """Verify command formatting for .exe local installers."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    result = installer._install_local("TestApp", "C:\\test.exe", "D:\\InstallDir")
    
    assert result is True
    
    cmd_args = mock_popen.call_args[0][0]
    assert cmd_args[0] == "C:\\test.exe"
    assert "/S" in cmd_args
    assert "/D=D:\\InstallDir" in cmd_args

@patch('subprocess.Popen')
def test_install_local_msi(mock_popen, installer):
    """Verify command formatting for .msi local installers."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    result = installer._install_local("TestApp", "C:\\test.msi", "D:\\InstallDir")
    
    assert result is True
    
    cmd_args = mock_popen.call_args[0][0]
    assert cmd_args[0] == "msiexec.exe"
    assert "/i" in cmd_args
    assert "C:\\test.msi" in cmd_args
    assert "INSTALLDIR=D:\\InstallDir" in cmd_args

@patch('migration_tool.core.installer.WingetAPI.install')
def test_run_batch_missing_info(mock_install, installer):
    """Verify run_batch handles missing winget_id or local_path."""
    mock_install.return_value = True
    
    apps = [
        {"name": "App1", "install_method": "winget"}, # missing winget_id
        {"name": "App2", "install_method": "local"},  # missing local_path
        {"name": "App3", "install_method": "unknown_method"} # Invalid method
    ]
    callback = MagicMock()
    
    with patch('migration_tool.core.installer.logger') as mock_log:
        installer.run_batch(apps, progress_callback=callback)
        assert mock_install.call_count == 0
        assert mock_log.error.call_count >= 2
        
@patch('subprocess.Popen')
def test_install_local_exception(mock_popen, installer):
    """Verify _install_local catches Popen exceptions."""
    mock_popen.side_effect = Exception("Process Error")
    
    result = installer._install_local("TestApp", "C:\\test.exe", "D:\\InstallDir")
    
    assert result is False

from unittest.mock import mock_open

@patch('subprocess.Popen')
def test_install_local_exe_heuristics_inno(mock_popen, installer):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    with patch('builtins.open', mock_open(read_data=b"Some binary junk Inno Setup ...")):
        result = installer._install_local("TestApp", "C:\\test.exe", "D:\\InstallDir")
        
    assert result is True
    cmd_args = mock_popen.call_args[0][0]
    assert cmd_args[1] == "/VERYSILENT"

@patch('subprocess.Popen')
def test_install_local_exe_heuristics_nsis(mock_popen, installer):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    with patch('builtins.open', mock_open(read_data=b"Nullsoft Install System")):
        result = installer._install_local("TestNSIS", "C:\\test2.exe", "D:\\InstallDir")
        
    assert result is True
    cmd_args = mock_popen.call_args[0][0]
    assert cmd_args[1] == "/S"

@patch('subprocess.Popen')
def test_install_local_exe_heuristics_wix(mock_popen, installer):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    with patch('builtins.open', mock_open(read_data=b"WiX Toolset")):
        result = installer._install_local("TestWiX", "C:\\test3.exe", "D:\\InstallDir")
        
    assert result is True
    cmd_args = mock_popen.call_args[0][0]
    assert cmd_args[1] == "/quiet"
