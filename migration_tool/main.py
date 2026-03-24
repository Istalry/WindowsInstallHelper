import sys
import os
from pathlib import Path

# Add the parent directory to sys.path if run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from migration_tool.ui.app_window import AppWindow

def main():
    app = AppWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
