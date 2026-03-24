import customtkinter as ctk
from .export_view import ExportView
from .import_view import ImportView
from ..utils.config import APP_NAME, APP_VERSION

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Create tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_export = self.tabview.add("Export (Source PC)")
        self.tab_import = self.tabview.add("Import & Install (Target PC)")
        
        # Add views to tabs
        self.export_view = ExportView(self.tab_export)
        self.export_view.pack(fill="both", expand=True)
        
        self.import_view = ImportView(self.tab_import)
        self.import_view.pack(fill="both", expand=True)
