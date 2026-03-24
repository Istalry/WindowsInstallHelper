import threading
import customtkinter as ctk
from typing import List, Dict, Any

from ..core.scanner import RegistryScanner
from ..core.file_manager import FileManager
from ..utils.logger import logger

class ExportView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.scanner = RegistryScanner()
        self.found_apps: List[Dict[str, Any]] = []
        self.app_checkboxes: List[ctk.CTkCheckBox] = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Header
        self.header_label = ctk.CTkLabel(self, text="Export Installed Applications", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Top controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=5)
        
        self.scan_btn = ctk.CTkButton(self.controls_frame, text="Scan Registry", command=self.start_scan)
        self.scan_btn.pack(side="left", padx=(0, 10))
        
        self.select_all_btn = ctk.CTkButton(self.controls_frame, text="Select All", command=self.select_all, state="disabled", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.select_all_btn.pack(side="left", padx=5)
        
        self.deselect_all_btn = ctk.CTkButton(self.controls_frame, text="Deselect All", command=self.deselect_all, state="disabled", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.deselect_all_btn.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Ready", text_color="gray")
        self.status_label.pack(side="right")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=20, pady=(5, 10))
        self.progress_bar.set(0)
        
        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bottom controls
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.export_btn = ctk.CTkButton(self.bottom_frame, text="Export to JSON", command=self.export_json, state="disabled")
        self.export_btn.pack(side="right")
        
    def start_scan(self):
        self.scan_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.status_label.configure(text="Scanning registry...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Clear previous
        for cb in self.app_checkboxes:
            cb.destroy()
        self.app_checkboxes.clear()
        
        # Run in thread
        threading.Thread(target=self._run_scan, daemon=True).start()
        
    def _run_scan(self):
        try:
            self.found_apps = self.scanner.scan()
            # Update UI from main thread using after
            self.after(100, self._on_scan_complete)
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            self.after(100, lambda: self._on_scan_error(str(e)))
            
    def _on_scan_complete(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.status_label.configure(text=f"Found {len(self.found_apps)} applications.")
        
        # Populate list
        for app in self.found_apps:
            display_text = f"{app['name']} (v{app.get('version', 'Unknown')})"
            cb = ctk.CTkCheckBox(self.list_frame, text=display_text)
            cb.pack(anchor="w", pady=2, padx=5)
            cb.select() # Select by default
            cb._app_data = app # Store data directly on checkbox object
            self.app_checkboxes.append(cb)
            
        self.scan_btn.configure(state="normal")
        if self.found_apps:
            self.export_btn.configure(state="normal")
            self.select_all_btn.configure(state="normal")
            self.deselect_all_btn.configure(state="normal")
            
    def _on_scan_error(self, error_msg: str):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.status_label.configure(text="Error during scan.", text_color="red")
        self.scan_btn.configure(state="normal")
        
    def select_all(self):
        for cb in self.app_checkboxes:
            cb.select()
            
    def deselect_all(self):
        for cb in self.app_checkboxes:
            cb.deselect()
            
    def export_json(self):
        selected_apps = []
        for cb in self.app_checkboxes:
            if cb.get() == 1:
                selected_apps.append(cb._app_data)
                
        if not selected_apps:
            self.status_label.configure(text="No applications selected for export.")
            return
            
        filepath = ctk.filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="export.json",
            title="Save Export File",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if filepath:
            success = FileManager.export_json(filepath, selected_apps)
            if success:
                self.status_label.configure(text=f"Successfully exported {len(selected_apps)} apps.")
            else:
                self.status_label.configure(text="Error exporting data.", text_color="red")
