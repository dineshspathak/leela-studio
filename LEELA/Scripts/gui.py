#!/usr/bin/env python3
import os
import sys
import json
import shutil
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Base path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")
METADATA_DIR = os.path.join(BASE_DIR, "Metadata")
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")
EPISODES_DIR = os.path.join(BASE_DIR, "Episodes")
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

# Style Palette
BG_COLOR = "#0f172a"      # Slate 900
CARD_COLOR = "#1e293b"    # Slate 800
ACCENT_COLOR = "#3b82f6"  # Blue 500
TEXT_COLOR = "#f8fafc"    # Slate 50
TEXT_MUTED = "#94a3b8"    # Slate 400
HIGHLIGHT_GOLD = "#fbbf24"# Amber 400

class LeelaDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LEELA Studios — Cinematic Production Suite v1.0")
        self.geometry("900x650")
        self.configure(bg=BG_COLOR)
        
        # Configure custom themes and styles
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_COLOR, relief="flat", borderwidth=1)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 11))
        style.configure("Card.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 11))
        style.configure("Title.TLabel", background=BG_COLOR, foreground=HIGHLIGHT_GOLD, font=("Helvetica", 18, "bold"))
        style.configure("Sub.TLabel", background=BG_COLOR, foreground=TEXT_MUTED, font=("Helvetica", 10, "italic"))
        
        style.configure("TButton", 
                        background=ACCENT_COLOR, 
                        foreground="white", 
                        font=("Helvetica", 11, "bold"),
                        borderwidth=0,
                        focusthickness=0,
                        padding=8)
        style.map("TButton",
                  background=[("active", "#2563eb")]) # Darker blue on hover
                  
    def create_widgets(self):
        # Header Area
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=25, pady=20)
        
        title_lbl = ttk.Label(header_frame, text="LEELA Studios — Production Dashboard", style="Title.TLabel")
        title_lbl.pack(anchor="w")
        
        sub_lbl = ttk.Label(header_frame, text="Automated AI Cinematic Video Compiler for YouTube", style="Sub.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))
        
        # Main Layout: Two Columns
        main_pane = ttk.Frame(self)
        main_pane.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        left_column = ttk.Frame(main_pane)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_column = ttk.Frame(main_pane)
        right_column.pack(side="right", fill="both", padx=(10, 0))
        
        # Left Column: Actions and Logs
        actions_card = ttk.Frame(left_column, style="Card.TFrame")
        actions_card.pack(fill="x", pady=(0, 15))
        
        actions_inner = ttk.Frame(actions_card, style="Card.TFrame")
        actions_inner.pack(padx=15, pady=15, fill="x")
        
        ttk.Label(actions_inner, text="OPERATIONS", style="Card.TLabel", font=("Helvetica", 12, "bold"), foreground=HIGHLIGHT_GOLD).pack(anchor="w", pady=(0, 10))
        
        btn_grid = ttk.Frame(actions_inner, style="Card.TFrame")
        btn_grid.pack(fill="x")
        
        # Scan Assets Button
        scan_btn = ttk.Button(btn_grid, text="Scan Assets Catalog", command=self.run_scanner)
        scan_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Import Asset Button
        import_btn = ttk.Button(btn_grid, text="Import Media File", command=self.import_asset)
        import_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Create Episode Button
        create_btn = ttk.Button(btn_grid, text="Create New Script Template", command=self.create_template)
        create_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Open Output Button
        open_btn = ttk.Button(btn_grid, text="Open Output Folder", command=self.open_output)
        open_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        
        # Render Frame
        render_frame = ttk.Frame(actions_inner, style="Card.TFrame")
        render_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(render_frame, text="Select Episode Script:", style="Card.TLabel").pack(side="left", padx=(0, 5))
        self.script_var = tk.StringVar()
        self.script_dropdown = ttk.Combobox(render_frame, textvariable=self.script_var, width=30)
        self.script_dropdown.pack(side="left", fill="x", expand=True, padx=5)
        self.refresh_scripts()
        
        render_btn = ttk.Button(actions_inner, text="🚀 Render Episode", command=self.start_render_thread)
        render_btn.pack(fill="x", pady=(15, 0))
        
        # Console/Logs Card
        console_card = ttk.Frame(left_column, style="Card.TFrame")
        console_card.pack(fill="both", expand=True)
        
        console_inner = ttk.Frame(console_card, style="Card.TFrame")
        console_inner.pack(padx=15, pady=15, fill="both", expand=True)
        
        ttk.Label(console_inner, text="PROCESS LOGS", style="Card.TLabel", font=("Helvetica", 11, "bold"), foreground=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        
        self.log_text = tk.Text(console_inner, bg="#020617", fg="#10b981", font=("Courier", 10), insertbackground="white", relief="flat")
        self.log_text.pack(fill="both", expand=True)
        
        # Right Column: File Manager Quickview
        quickview_card = ttk.Frame(right_column, style="Card.TFrame", width=250)
        quickview_card.pack(fill="both", expand=True)
        quickview_card.pack_propagate(False)
        
        qv_inner = ttk.Frame(quickview_card, style="Card.TFrame")
        qv_inner.pack(padx=15, pady=15, fill="both", expand=True)
        
        ttk.Label(qv_inner, text="EPISODE REGISTRY", style="Card.TLabel", font=("Helvetica", 12, "bold"), foreground=HIGHLIGHT_GOLD).pack(anchor="w", pady=(0, 10))
        
        self.ep_listbox = tk.Listbox(qv_inner, bg="#0f172a", fg=TEXT_COLOR, font=("Helvetica", 10), selectbackground=ACCENT_COLOR, relief="flat", borderwidth=0)
        self.ep_listbox.pack(fill="both", expand=True, pady=(0, 10))
        self.refresh_episode_list()
        
        refresh_btn = ttk.Button(qv_inner, text="Refresh Data", command=self.refresh_all)
        refresh_btn.pack(fill="x")
        
        self.log("System initialized and ready.")

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def refresh_all(self):
        self.refresh_scripts()
        self.refresh_episode_list()
        self.log("Dashboard view refreshed.")
        
    def refresh_scripts(self):
        scripts = []
        if os.path.exists(EPISODES_DIR):
            for f in os.listdir(EPISODES_DIR):
                if f.endswith(".json"):
                    scripts.append(f)
        self.script_dropdown["values"] = sorted(scripts)
        if scripts:
            self.script_dropdown.current(0)
            
    def refresh_episode_list(self):
        self.ep_listbox.delete(0, tk.END)
        if os.path.exists(EPISODES_DIR):
            for item in sorted(os.listdir(EPISODES_DIR)):
                item_path = os.path.join(EPISODES_DIR, item)
                if os.path.isdir(item_path):
                    self.ep_listbox.insert(tk.END, f"📁 {item}")
                elif item.endswith(".json"):
                    self.ep_listbox.insert(tk.END, f"📄 {item}")
                    
    def run_scanner(self):
        self.log("Scanning assets...")
        script_path = os.path.join(SCRIPTS_DIR, "cataloger.py")
        try:
            res = subprocess.run(["python3", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.log(res.stdout)
            messagebox.showinfo("Scanner", "Asset scanning completed successfully!")
        except Exception as e:
            self.log(f"Scan error: {e}")
            messagebox.showerror("Error", f"Failed to scan assets:\n{e}")
            
    def import_asset(self):
        file_path = filedialog.askopenfilename(title="Select Media File to Import")
        if not file_path:
            return
            
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # Guide user to pick category directory
        categories = ["Characters/BabyKrishna", "Characters/Devaki", "Characters/Vasudeva", "Characters/Kansa", 
                      "Characters/Yashoda", "Characters/Nanda", "Backgrounds/Prison", "Backgrounds/Palace", 
                      "Backgrounds/Gokul", "Backgrounds/Yamuna", "Videos", "Audio/Narration", "Audio/Music", "Audio/SFX"]
                      
        # Category Selector Dialog
        selector = tk.Toplevel(self)
        selector.title("Select Destination Folder")
        selector.geometry("350x450")
        selector.configure(bg=BG_COLOR)
        selector.transient(self)
        selector.grab_set()
        
        ttk.Label(selector, text="Select Destination Category:", style="Title.TLabel", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        dest_var = tk.StringVar(value=categories[0])
        listbox = tk.Listbox(selector, bg="#1e293b", fg="white", selectbackground=ACCENT_COLOR)
        listbox.pack(fill="both", expand=True, padx=15, pady=10)
        for cat in categories:
            listbox.insert(tk.END, cat)
            
        def confirm_import():
            choice = listbox.get(listbox.curselection())
            dest_dir = os.path.join(ASSETS_DIR, choice)
            os.makedirs(dest_dir, exist_ok=True)
            
            dest_file = os.path.join(dest_dir, filename)
            try:
                shutil.copy(file_path, dest_file)
                self.log(f"Imported {filename} -> {choice}")
                self.run_scanner() # Auto-scan on import
                selector.destroy()
                messagebox.showinfo("Success", f"File imported to {choice} successfully!")
            except Exception as e:
                self.log(f"Import failed: {e}")
                messagebox.showerror("Error", f"Copying failed:\n{e}")
                
        ttk.Button(selector, text="Import File", command=confirm_import).pack(pady=15, fill="x", padx=15)
        
    def create_template(self):
        template_name = filedialog.asksaveasfilename(
            initialdir=EPISODES_DIR,
            title="Create Script JSON Template",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not template_name:
            return
            
        template_data = {
            "episode": os.path.splitext(os.path.basename(template_name))[0],
            "music": "MUSIC_001",
            "scenes": [
                {
                    "scene": 1,
                    "narration": "यहाँ अपनी हिंदी कहानी की लाइन लिखें।",
                    "duration": 8.0,
                    "visuals": ["PRISON_001", "DEVAKI_001"],
                    "audio": {
                        "narration": "NARRATION_001",
                        "sfx": "SFX_001"
                    },
                    "effects": {
                        "motion": "zoom_in",
                        "overlays": ["rain", "grain"]
                    }
                }
            ]
        }
        
        try:
            with open(template_name, "w", encoding="utf-8") as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            self.log(f"Template script created at: {template_name}")
            self.refresh_all()
            messagebox.showinfo("Success", "Script template created successfully!")
        except Exception as e:
            self.log(f"Failed to create template: {e}")
            messagebox.showerror("Error", f"Failed to create template:\n{e}")
            
    def open_output(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if sys.platform == "darwin":
            subprocess.run(["open", OUTPUT_DIR])
        elif sys.platform == "win32":
            os.startfile(OUTPUT_DIR)
        else:
            subprocess.run(["xdg-open", OUTPUT_DIR])
            
    def start_render_thread(self):
        script_file = self.script_var.get()
        if not script_file:
            messagebox.showwarning("Warning", "Please select a script json first!")
            return
            
        full_script_path = os.path.join(EPISODES_DIR, script_file)
        self.log(f"Starting render for script: {script_file}...")
        
        # Run in thread so GUI doesn't freeze
        t = threading.Thread(target=self.render, args=(full_script_path, script_file))
        t.daemon = True
        t.start()
        
    def render(self, script_path, filename):
        renderer_script = os.path.join(SCRIPTS_DIR, "renderer.py")
        output_mp4 = f"{os.path.splitext(filename)[0]}.mp4"
        
        cmd = ["python3", renderer_script, script_path, output_mp4]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.log(line.strip())
                
            process.wait()
            if process.returncode == 0:
                self.log(f"\nEpisode rendered successfully to Output/{output_mp4}!")
                messagebox.showinfo("Rendering Complete", f"Successfully rendered episode:\nOutput/{output_mp4}")
            else:
                self.log(f"\nRendering failed with return code {process.returncode}.")
                messagebox.showerror("Error", f"Rendering failed. Check log console.")
        except Exception as e:
            self.log(f"Error during execution: {e}")
            messagebox.showerror("Error", f"Failed to launch renderer:\n{e}")

if __name__ == "__main__":
    app = LeelaDashboard()
    app.mainloop()
