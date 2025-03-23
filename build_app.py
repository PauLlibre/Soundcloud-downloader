#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import glob

# Import our FFmpeg downloader
try:
    from bundle_ffmpeg import download_ffmpeg
    BUNDLE_FFMPEG = True
except ImportError:
    print("Warning: bundle_ffmpeg.py not found, FFmpeg won't be bundled")
    BUNDLE_FFMPEG = False

def main():
    print("Building SoundCloud Downloader App...")
    
    # Determine OS
    system = platform.system()
    
    # Clean dist and build directories
    for dir_name in ['dist', 'build']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    # Download FFmpeg if possible
    ffmpeg_path = None
    if BUNDLE_FFMPEG:
        print("Downloading FFmpeg for bundling...")
        ffmpeg_path = download_ffmpeg()
        if not ffmpeg_path:
            print("Warning: Failed to download FFmpeg. The app will require manual FFmpeg installation.")
    
    # Base PyInstaller command
    base_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--name', 'SoundCloudDownloader',
        '--onefile',
        '--windowed',
        '--add-data', f'README.md{os.pathsep}.',
        '--additional-hooks-dir', '.',  # Look for hook files in current directory
    ]
    
    # Windows-specific fixes for DLL issues
    if system == 'Windows':
        base_cmd.extend([
            '--hidden-import', 'pkg_resources.py2_warn',
            '--hidden-import', 'PIL._tkinter_finder',
            '--hidden-import', 'yt_dlp',
            '--hidden-import', 'yt_dlp.extractor',
            '--hidden-import', 'yt_dlp.downloader',
            '--hidden-import', 'yt_dlp.postprocessor',
            '--hidden-import', 'yt_dlp.utils',
            '--collect-all', 'tkinter',
        ])
    
    # Add FFmpeg to the package
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        # Get just the filename (ffmpeg or ffmpeg.exe)
        ffmpeg_filename = os.path.basename(ffmpeg_path)
        
        # Add FFmpeg to PyInstaller command
        base_cmd.extend(['--add-binary', f'{ffmpeg_path}{os.pathsep}.'])
        print(f"Bundling FFmpeg: {ffmpeg_path}")
    
    # Platform-specific options
    if system == 'Darwin':  # macOS
        base_cmd.extend([
            '--icon=icon.icns',
            '--osx-bundle-identifier', 'com.soundclouddownloader.app',
        ])
    elif system == 'Windows':
        base_cmd.extend([
            '--icon=icon.ico',
        ])
    
    # Add the main script
    base_cmd.append('soundcloud_downloader_gui.py')
    
    print(f"Running command: {' '.join(base_cmd)}")
    subprocess.run(base_cmd)
    
    print("\nBuild completed!")
    
    if system == 'Darwin':
        print("\nYour macOS app is available at: dist/SoundCloudDownloader.app")
    elif system == 'Windows':
        print("\nYour Windows executable is available at: dist/SoundCloudDownloader.exe")
        print("\nIf you encounter 'ordinal not found' errors, install the latest Visual C++ Redistributable:")
        print("https://aka.ms/vs/17/release/vc_redist.x64.exe")
    
    if ffmpeg_path:
        print("\nFFmpeg is bundled with the application - no separate installation required.")
    else:
        print("\nNOTE: Users will need to install FFmpeg separately.")

if __name__ == "__main__":
    main() 