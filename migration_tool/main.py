import sys
import os
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Add the parent directory to sys.path if run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from migration_tool.ui.app_window import AppWindow
from migration_tool.utils.logger import logger

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        logger.warning("Application running without Administrator privileges.")
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Privilèges Administrateur Requis", 
            "L'outil s'exécute sans droits d'administrateur. Certaines installations locales risquent d'échouer."
        )
        root.destroy()
        
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
