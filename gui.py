import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import yaml
from datetime import datetime
import subprocess
import queue

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.config import load_config
from scripts.renamer import ImageRenamer
from scripts.scanner import ImageScanner
from scripts.logger import RenameLogger

class FMSFolderTaxonomyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FMS Folder Taxonomy - Image Renaming Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Create message queue for thread communication
        self.message_queue = queue.Queue()
        
        # Load config
        self.config = self.load_config()
        
        # Create UI
        self.create_widgets()
        
        # Periodically check message queue
        self.check_message_queue()
        
    def load_config(self):
        """Load config file"""
        try:
            return load_config("config.yaml")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config file: {e}")
            return {
                "input_folder": "images/",
                "output_renamed": "output/renamed/",
                "output_dnu": "output/dnu/",
                "output_review": "output/review/",
                "log_file": "output/rename_log.csv"
            }
    
    def save_config(self):
        """Save config file"""
        try:
            config_data = {
                "input_folder": self.input_folder_var.get(),
                "output_renamed": self.output_renamed_var.get(),
                "output_dnu": self.output_dnu_var.get(),
                "output_review": self.output_review_var.get(),
                "log_file": self.log_file_var.get(),
                "use_ai": self.use_ai_var.get(),
                "ai_confidence_threshold": float(self.ai_threshold_var.get()),
                "ai_source": self.ai_source_var.get(),
                "default_version": int(self.default_version_var.get()),
                "version_format": self.version_format_var.get(),
                "publish_values": ["yes", "y", "true"]
            }
            
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            messagebox.showinfo("Success", "Config saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def create_widgets(self):
        """Create UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid weight
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="FMS Folder Taxonomy", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Main tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Main")
        
        # Config tab
        config_tab = ttk.Frame(notebook)
        notebook.add(config_tab, text="Config")
        
        # Log tab
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text="Log")
        
        # Setup tabs
        self.setup_main_tab(main_tab)
        self.setup_config_tab(config_tab)
        self.setup_log_tab(log_tab)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        main_frame.rowconfigure(1, weight=1)
    
    def setup_main_tab(self, parent):
        """Setup main tab"""
        # Directory frame
        dir_frame = ttk.LabelFrame(parent, text="Directory Settings", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # Input folder
        ttk.Label(dir_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_folder_var = tk.StringVar(value=self.config.get("input_folder", "images/"))
        input_entry = ttk.Entry(dir_frame, textvariable=self.input_folder_var, width=50)
        input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_input_folder).grid(row=0, column=2, pady=2)
        
        # Output folder
        ttk.Label(dir_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_renamed_var = tk.StringVar(value=self.config.get("output_renamed", "output/renamed/"))
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_renamed_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_frame, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, pady=2)
        
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Scan button
        self.scan_btn = ttk.Button(button_frame, text="Scan Images", 
                                  command=self.scan_images, style="Accent.TButton")
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Rename button
        self.rename_btn = ttk.Button(button_frame, text="Start Rename", 
                                    command=self.start_rename, style="Accent.TButton")
        self.rename_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Preview button
        self.preview_btn = ttk.Button(button_frame, text="Preview Rename", 
                                     command=self.preview_rename)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open output folder button
        self.open_output_btn = ttk.Button(button_frame, text="Open Output Folder", 
                                         command=self.open_output_folder)
        self.open_output_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Log area
        log_frame = ttk.LabelFrame(parent, text="Operation Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
    
    def setup_config_tab(self, parent):
        """Setup config tab"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Directory config frame
        dir_config_frame = ttk.LabelFrame(scrollable_frame, text="Directory Config", padding="10")
        dir_config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_config_frame.columnconfigure(1, weight=1)
        
        # DNU output folder
        ttk.Label(dir_config_frame, text="DNU Output Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.output_dnu_var = tk.StringVar(value=self.config.get("output_dnu", "output/dnu/"))
        dnu_entry = ttk.Entry(dir_config_frame, textvariable=self.output_dnu_var, width=50)
        dnu_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="Browse", command=self.browse_dnu_folder).grid(row=0, column=2, pady=2)
        
        # Review output folder
        ttk.Label(dir_config_frame, text="Review Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_review_var = tk.StringVar(value=self.config.get("output_review", "output/review/"))
        review_entry = ttk.Entry(dir_config_frame, textvariable=self.output_review_var, width=50)
        review_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="Browse", command=self.browse_review_folder).grid(row=1, column=2, pady=2)
        
        # Log file
        ttk.Label(dir_config_frame, text="Log File:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.log_file_var = tk.StringVar(value=self.config.get("log_file", "output/rename_log.csv"))
        log_entry = ttk.Entry(dir_config_frame, textvariable=self.log_file_var, width=50)
        log_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(dir_config_frame, text="Browse", command=self.browse_log_file).grid(row=2, column=2, pady=2)
        
        # AI config frame
        ai_config_frame = ttk.LabelFrame(scrollable_frame, text="AI Config", padding="10")
        ai_config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_config_frame.columnconfigure(1, weight=1)
        
        # Enable AI
        self.use_ai_var = tk.BooleanVar(value=self.config.get("use_ai", True))
        ttk.Checkbutton(ai_config_frame, text="Enable AI fallback", 
                       variable=self.use_ai_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # AI confidence threshold
        ttk.Label(ai_config_frame, text="AI Confidence Threshold:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ai_threshold_var = tk.StringVar(value=str(self.config.get("ai_confidence_threshold", 0.8)))
        ttk.Entry(ai_config_frame, textvariable=self.ai_threshold_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # AI source
        ttk.Label(ai_config_frame, text="AI Source:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ai_source_var = tk.StringVar(value=self.config.get("ai_source", "deepseek"))
        ai_source_combo = ttk.Combobox(ai_config_frame, textvariable=self.ai_source_var, 
                                      values=["deepseek", "blip"], state="readonly", width=20)
        ai_source_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Version config frame
        version_config_frame = ttk.LabelFrame(scrollable_frame, text="Version Config", padding="10")
        version_config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        version_config_frame.columnconfigure(1, weight=1)
        
        # Default version
        ttk.Label(version_config_frame, text="Default Version:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.default_version_var = tk.StringVar(value=str(self.config.get("default_version", 1)))
        ttk.Entry(version_config_frame, textvariable=self.default_version_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Version format
        ttk.Label(version_config_frame, text="Version Format:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.version_format_var = tk.StringVar(value=self.config.get("version_format", "_v{n}"))
        ttk.Entry(version_config_frame, textvariable=self.version_format_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Save button
        save_btn = ttk.Button(scrollable_frame, text="Save Config", 
                             command=self.save_config, style="Accent.TButton")
        save_btn.grid(row=3, column=0, pady=20)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_log_tab(self, parent):
        """Setup log tab"""
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        button_frame = ttk.Frame(log_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Refresh Log", command=self.refresh_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export Log", command=self.export_log).pack(side=tk.LEFT)
        
        self.log_display = scrolledtext.ScrolledText(log_frame, height=25, width=80)
        self.log_display.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        self.refresh_log()
    
    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder_var.set(folder)
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_renamed_var.set(folder)
    
    def browse_dnu_folder(self):
        folder = filedialog.askdirectory(title="Select DNU Output Folder")
        if folder:
            self.output_dnu_var.set(folder)
    
    def browse_review_folder(self):
        folder = filedialog.askdirectory(title="Select Review Output Folder")
        if folder:
            self.output_review_var.set(folder)
    
    def browse_log_file(self):
        file = filedialog.asksaveasfilename(title="Select Log File", 
                                          defaultextension=".csv",
                                          filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file:
            self.log_file_var.set(file)
    
    def scan_images(self):
        def scan_thread():
            try:
                self.log_message("Start scanning images...")
                self.status_var.set("Scanning images...")
                
                self.update_config()
                scanner = ImageScanner("config.yaml")
                image_paths = scanner.scan_image_paths()
                
                self.log_message(f"Scan complete, found {len(image_paths)} images")
                self.status_var.set(f"Scan complete, found {len(image_paths)} images")
                
            except Exception as e:
                self.log_message(f"Scan failed: {e}")
                self.status_var.set("Scan failed")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def start_rename(self):
        def rename_thread():
            try:
                self.log_message("Start renaming images...")
                self.status_var.set("Renaming images...")
                self.progress_var.set(0)
                
                self.update_config()
                renamer = ImageRenamer("config.yaml")
                renamer.rename_images(dry_run=False)
                
                self.log_message("Rename complete")
                self.status_var.set("Rename complete")
                self.progress_var.set(100)
                
            except Exception as e:
                self.log_message(f"Rename failed: {e}")
                self.status_var.set("Rename failed")
        
        threading.Thread(target=rename_thread, daemon=True).start()
    
    def preview_rename(self):
        def preview_thread():
            try:
                self.log_message("Start preview rename...")
                self.status_var.set("Previewing rename...")
                self.progress_var.set(0)
                
                self.update_config()
                renamer = ImageRenamer("config.yaml")
                renamer.rename_images(dry_run=True)
                
                self.log_message("Preview complete")
                self.status_var.set("Preview complete")
                self.progress_var.set(100)
                
            except Exception as e:
                self.log_message(f"Preview failed: {e}")
                self.status_var.set("Preview failed")
        
        threading.Thread(target=preview_thread, daemon=True).start()
    
    def open_output_folder(self):
        output_dir = self.output_renamed_var.get()
        if os.path.exists(output_dir):
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
        else:
            messagebox.showwarning("Warning", "Output folder does not exist")
    
    def update_config(self):
        try:
            config_data = {
                "input_folder": self.input_folder_var.get(),
                "output_renamed": self.output_renamed_var.get(),
                "output_dnu": self.output_dnu_var.get(),
                "output_review": self.output_review_var.get(),
                "log_file": self.log_file_var.get(),
                "use_ai": self.use_ai_var.get(),
                "ai_confidence_threshold": float(self.ai_threshold_var.get()),
                "ai_source": self.ai_source_var.get(),
                "default_version": int(self.default_version_var.get()),
                "version_format": self.version_format_var.get(),
                "publish_values": ["yes", "y", "true"]
            }
            
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                
        except Exception as e:
            self.log_message(f"Failed to update config: {e}")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.message_queue.put(log_entry)
    
    def check_message_queue(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.check_message_queue)
    
    def refresh_log(self):
        try:
            log_file = self.log_file_var.get()
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_display.delete(1.0, tk.END)
                self.log_display.insert(1.0, content)
            else:
                self.log_display.delete(1.0, tk.END)
                self.log_display.insert(1.0, "Log file does not exist")
        except Exception as e:
            self.log_display.delete(1.0, tk.END)
            self.log_display.insert(1.0, f"Failed to read log: {e}")
    
    def clear_log(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the log?"):
            try:
                log_file = self.log_file_var.get()
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write("")
                self.refresh_log()
                messagebox.showinfo("Success", "Log cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear log: {e}")
    
    def export_log(self):
        file = filedialog.asksaveasfilename(title="Export Log", 
                                          defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            try:
                content = self.log_display.get(1.0, tk.END)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", "Log exported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log: {e}")

def main():
    root = tk.Tk()
    app = FMSFolderTaxonomyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 