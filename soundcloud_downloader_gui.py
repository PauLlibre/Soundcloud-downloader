import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import platform
import json

# Try to import soundcloud_downloader functions, with fallback for PyInstaller bundle
try:
    from soundcloud_downloader import download_soundcloud, check_dependencies, is_valid_soundcloud_url
except ModuleNotFoundError:
    # If running from PyInstaller bundle, we need to handle imports differently
    try:
        # Add current directory to path to find modules
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller bundle
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        sys.path.insert(0, base_dir)
        
        # Try to import yt_dlp directly
        try:
            import yt_dlp
        except ModuleNotFoundError:
            messagebox.showerror("Error", "Required module 'yt_dlp' not found. Please reinstall the application.")
            sys.exit(1)
            
        # Now try importing from soundcloud_downloader
        from soundcloud_downloader import download_soundcloud, check_dependencies, is_valid_soundcloud_url
    except Exception as e:
        # Show error and exit if we can't import the required modules
        if 'tkinter' in sys.modules:
            # If Tkinter is available, show a message box
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", f"Failed to import required modules: {str(e)}\n\n"
                                "Please reinstall the application.")
            root.destroy()
        else:
            # Otherwise, print to console
            print(f"Error: Failed to import required modules: {str(e)}")
        sys.exit(1)

class SoundCloudDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bertux best DJ Songs Downloader")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Config file path
        self.config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else 
            os.path.dirname(sys.executable),
            'soundcloud_downloader_config.json'
        )
        
        # Load saved settings
        self.settings = self.load_settings()
        
        # Set app icon if available
        try:
            if platform.system() == "Windows":
                self.root.iconbitmap("icon.ico")
            elif platform.system() == "Darwin":  # macOS
                # macOS handles icons differently
                pass
        except:
            pass  # Ignore if icon not found
        
        self.create_widgets()
        
    def load_settings(self):
        """Load saved settings from config file"""
        default_settings = {
            'output_dir': os.path.join(os.path.expanduser("~"), "Downloads", "SoundCloud")
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                    # Ensure all default settings exist
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(url_frame, text="SoundCloud URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        url_entry.focus()
        
        # Output directory selection
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 10))
        self.dir_var = tk.StringVar(value=self.settings['output_dir'])
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT)
        
        # Status and progress
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=550)
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn = ttk.Button(btn_frame, text="Download", command=self.start_download)
        self.download_btn.pack(side=tk.RIGHT, padx=5)
        
        quit_btn = ttk.Button(btn_frame, text="Quit", command=self.root.destroy)
        quit_btn.pack(side=tk.RIGHT, padx=5)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(
            initialdir=self.dir_var.get(),
            title="Select Output Directory"
        )
        if directory:
            self.dir_var.set(directory)
            # Save the new directory in settings
            self.settings['output_dir'] = directory
            self.save_settings()
    
    def start_download(self):
        url = self.url_var.get().strip()
        output_dir = self.dir_var.get()
        
        # Save the current output directory
        if output_dir != self.settings['output_dir']:
            self.settings['output_dir'] = output_dir
            self.save_settings()
        
        if not url:
            messagebox.showerror("Error", "Please enter a SoundCloud URL")
            return
            
        if not is_valid_soundcloud_url(url):
            messagebox.showerror("Error", f"Invalid SoundCloud URL: {url}")
            return
            
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create output directory: {e}")
                return
        
        # Check dependencies
        if not check_dependencies():
            messagebox.showerror("Error", "Missing dependencies. Please check console output.")
            return
        
        # Disable UI during download
        self.download_btn.config(state=tk.DISABLED)
        self.status_var.set("Downloading... This may take a while.")
        self.progress.start()
        
        # Start download in a separate thread to avoid freezing the UI
        threading.Thread(target=self.download_thread, args=(url, output_dir), daemon=True).start()
    
    def download_thread(self, url, output_dir):
        try:
            success = download_soundcloud(url, output_dir)
            
            # Update UI in the main thread
            self.root.after(0, self.download_complete, success, output_dir)
        except Exception as e:
            self.root.after(0, self.download_error, str(e))
    
    def download_complete(self, success, output_dir):
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)
        
        if success:
            self.status_var.set(f"Download completed. Files saved to {os.path.abspath(output_dir)}")
            messagebox.showinfo("Success", f"Download completed.\nFiles saved to {os.path.abspath(output_dir)}")
        else:
            self.status_var.set("Download failed. Check console for details.")
    
    def download_error(self, error_msg):
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Error", f"Download failed: {error_msg}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundCloudDownloaderGUI(root)
    root.mainloop() 