import os
from pathlib import Path
import subprocess

def get_windows_path(folder_id):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        
        if folder_id == "Desktop":
            val, _ = winreg.QueryValueEx(key, "Desktop")
        else:
            return None
        winreg.CloseKey(key)
        import os
        return Path(os.path.expandvars(val))
    except Exception:
        return None

desktop = get_windows_path("Desktop")
if not desktop:
    desktop = Path.home() / "Desktop"

shortcut_path = desktop / "폴더정리 자동화 GUI.lnk"
target_path = "pyw.exe"
base_dir = Path(__file__).parent.resolve()
args_path = str(base_dir / "gui.py")
working_dir = str(base_dir)

ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_path}'
$Shortcut.Arguments = '{args_path}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.WindowStyle = 1
$Shortcut.IconLocation = '{str(base_dir / "app_icon.ico")}'
$Shortcut.Save()
"""
subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True)
print("Shortcut created.")
