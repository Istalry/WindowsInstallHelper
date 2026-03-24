import threading
import customtkinter as ctk
from typing import List, Dict, Any

from ..core.file_manager import FileManager
from ..core.installer import BatchInstaller
from ..utils.logger import logger

class ImportView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.installer = BatchInstaller()
        self.apps_to_install: List[Dict[str, Any]] = []
        self.list_items: List[ctk.CTkFrame] = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Header
        self.header_label = ctk.CTkLabel(self, text="Import & Install Applications", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Top controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=5)
        
        self.load_btn = ctk.CTkButton(self.controls_frame, text="Load JSON Export", command=self.load_json)
        self.load_btn.pack(side="left", padx=(0, 10))
        
        self.scan_folder_btn = ctk.CTkButton(self.controls_frame, text="Scan Local Folder", command=self.scan_local_folder, state="disabled", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.scan_folder_btn.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(self.controls_frame, text="Ready", text_color="gray")
        self.status_label.pack(side="right")
        
        # Scrollable list for review
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bottom controls for installation
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=5)
        
        self.install_progress = ctk.CTkProgressBar(self.bottom_frame)
        self.install_progress.pack(fill="x", pady=(0, 10))
        self.install_progress.set(0)
        
        self.install_status_label = ctk.CTkLabel(self.bottom_frame, text="")
        self.install_status_label.pack(side="left")
        
        self.install_btn = ctk.CTkButton(self.bottom_frame, text="Start Installation", command=self.start_installation, state="disabled", fg_color="#2FA572", hover_color="#107548")
        self.install_btn.pack(side="right")
        
        self.cancel_btn = ctk.CTkButton(self.bottom_frame, text="Cancel", command=self.cancel_installation, state="disabled", fg_color="#D14848", hover_color="#9C3434")
        self.cancel_btn.pack(side="right", padx=10)

    def load_json(self):
        filepath = ctk.filedialog.askopenfilename(
            title="Select Export JSON",
            filetypes=[("JSON Files", "*.json")]
        )
        if not filepath:
            return
            
        data = FileManager.import_json(filepath)
        if data:
            self.apps_to_install = []
            import string
            import os
            # Get default drive C:\ or similar
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            default_drive = drives[0] if drives else "C:\\"

            for item in data:
                app_entry = item.copy()
                app_entry['install_method'] = 'winget'
                app_entry['winget_id'] = item['name'] 
                app_entry['local_path'] = ''
                app_entry['install_drive'] = default_drive
                self.apps_to_install.append(app_entry)
                
            self.status_label.configure(text=f"Loaded {len(data)} apps. Verifying Winget availability...")
            self._refresh_list()
            self.scan_folder_btn.configure(state="normal")
            self.install_btn.configure(state="normal")
            
            # Start background winget verification
            threading.Thread(target=self._verify_winget_apps, daemon=True).start()
        else:
            self.status_label.configure(text="Failed to load file or file empty.", text_color="red")
            
    def scan_local_folder(self):
        folder = ctk.filedialog.askdirectory(title="Select Folder With Local Installers")
        if not folder:
            return
            
        self.status_label.configure(text="Scanning folder...")
        
        def _scan():
            installers = FileManager.scan_for_installers(folder)
            linked_count = 0
            for app in self.apps_to_install:
                app_name_lower = app['name'].lower()
                # Better fuzzy matching: extract the first significant word (e.g., 'vlc' from 'vlc media player')
                words = [w for w in app_name_lower.split() if w.isalnum() and len(w) >= 3]
                significant_word = words[0] if words else app_name_lower[:5]
                
                for inst_name, inst_path in installers.items():
                    if significant_word in inst_name:
                        app['install_method'] = 'local'
                        app['local_path'] = inst_path
                        linked_count += 1
                        break
                        
            self.after(0, lambda: self._on_scan_complete(linked_count))
            
        threading.Thread(target=_scan, daemon=True).start()
        
    def _on_scan_complete(self, linked_count):
        self.status_label.configure(text=f"Scan complete. Linked {linked_count} local installers.")
        self._refresh_list()
        
    def _refresh_list(self):
        import string
        import os
        drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
        if not drives: drives = ["C:\\"]

        for item in self.list_items:
            item.destroy()
        self.list_items.clear()
        self.row_widgets = []
        
        for index, app in enumerate(self.apps_to_install):
            frame = ctk.CTkFrame(self.list_frame, fg_color=("gray90", "gray20"))
            frame.pack(fill="x", pady=2, padx=5)
            
            # Limit name length so it fits alongside the drive combo
            name_text = f"{app['name']} (v{app.get('version', 'Unknown')})"
            if len(name_text) > 35: name_text = name_text[:32] + "..."
            name_lbl = ctk.CTkLabel(frame, text=name_text, width=220, anchor="w")
            name_lbl.pack(side="left", padx=10, pady=5)
            
            method_var = ctk.StringVar(value=app.get('install_method', 'winget'))
            method_combo = ctk.CTkComboBox(frame, values=["winget", "local", "skip"], variable=method_var, width=80,
                                           command=lambda val, idx=index: self._update_method(idx, val))
            method_combo.pack(side="left", padx=5)
            
            drive_var = ctk.StringVar(value=app.get('install_drive', drives[0]))
            drive_combo = ctk.CTkComboBox(frame, values=drives, variable=drive_var, width=60,
                                           command=lambda val, idx=index: self._update_drive(idx, val))
            drive_combo.pack(side="left", padx=5)
            
            path_text = app.get('local_path', '')
            if path_text and len(path_text) > 25:
                path_text = "..." + path_text[-22:]
            path_lbl = ctk.CTkLabel(frame, text=path_text, text_color="gray", width=180, anchor="w")
            path_lbl.pack(side="left", padx=5)
            
            self.list_items.append(frame)
            self.row_widgets.append({'method_var': method_var, 'status_lbl': path_lbl})

    def _verify_winget_apps(self):
        from ..core.winget_api import WingetAPI
        for index, app in enumerate(self.apps_to_install):
            if app['install_method'] == 'winget':
                self.after(0, lambda idx=index: self._update_row_status(idx, "Verifying Winget..."))
                result = WingetAPI.search(app['name'])
                if not result:
                    self.after(0, lambda idx=index: self._update_row_status(idx, "Not found. Switch to local.", error=True))
                else:
                    self.after(0, lambda idx=index: self._update_row_status(idx, "Winget OK!", error=False))
        self.after(0, lambda: self.status_label.configure(text=f"Verification complete for {len(self.apps_to_install)} applications."))

    def _update_row_status(self, index, text, error=False):
        try:
            if hasattr(self, 'row_widgets') and index < len(self.row_widgets):
                widgets = self.row_widgets[index]
                widgets['status_lbl'].configure(text=text[:40], text_color="#D14848" if error else "#2FA572")
                if error:
                    widgets['method_var'].set("local")
                    self.apps_to_install[index]['install_method'] = 'local'
        except Exception:
            pass

    def _update_drive(self, index, new_drive):
        self.apps_to_install[index]['install_drive'] = new_drive

    def _update_method(self, index, new_method):
        self.apps_to_install[index]['install_method'] = new_method
        
    def start_installation(self):
        self.install_btn.configure(state="disabled")
        self.load_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.installer = BatchInstaller()
        
        apps_to_run = [a for a in self.apps_to_install if a.get('install_method') != 'skip']
        
        if not apps_to_run:
            self.install_status_label.configure(text="No apps queued for installation.")
            self.install_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.load_btn.configure(state="normal")
            return
            
        threading.Thread(target=self._run_installation, args=(apps_to_run,), daemon=True).start()
        
    def _run_installation(self, apps_to_run):
        def progress_callback(current, total, text):
            self.after(0, lambda: self._update_progress(current, total, text))
            
        self.installer.run_batch(apps_to_run, progress_callback)
        self.after(0, self._on_installation_complete)
        
    def _update_progress(self, current, total, text):
        if total > 0:
            self.install_progress.set(current / total)
        self.install_status_label.configure(text=f"[{current}/{total}] {text}")
        
    def _on_installation_complete(self):
        self.install_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.load_btn.configure(state="normal")

    def cancel_installation(self):
        self.installer.cancel()
        self.cancel_btn.configure(state="disabled")
        self.install_status_label.configure(text="Cancelling... Please wait.")
