#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil

# Import our FFmpeg downloader
try:
    from bundle_ffmpeg import download_ffmpeg
    BUNDLE_FFMPEG = True
except ImportError:
    print("Warning: bundle_ffmpeg.py not found, FFmpeg won't be bundled")
    BUNDLE_FFMPEG = False

def main():
    print("Building DEBUG version of SoundCloud Downloader App...")
    
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
    
    # Base PyInstaller command - note console=True for debugging
    base_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--name', 'SoundCloudDownloader-Debug',
        '--onefile',
        '--console',  # Enable console output for debugging
        '--add-data', f'README.md{os.pathsep}.',
        '--additional-hooks-dir', '.',
    ]
    
    # Add all the necessary imports
    base_cmd.extend([
        '--hidden-import', 'pkg_resources.py2_warn',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'yt_dlp',
        '--hidden-import', 'yt_dlp.extractor',
        '--hidden-import', 'yt_dlp.downloader',
        '--hidden-import', 'yt_dlp.postprocessor',
        '--hidden-import', 'yt_dlp.utils',
        '--collect-all', 'tkinter',
        '--collect-all', 'yt_dlp',
    ])
    
    # Add FFmpeg to the package
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        base_cmd.extend(['--add-binary', f'{ffmpeg_path}{os.pathsep}.'])
        print(f"Bundling FFmpeg: {ffmpeg_path}")
    
    # Platform-specific options
    if system == 'Windows':
        base_cmd.extend(['--icon=icon.ico'])
    elif system == 'Darwin':  # macOS
        base_cmd.extend([
            '--icon=icon.icns',
            '--osx-bundle-identifier', 'com.soundclouddownloader.app',
        ])
    
    # Add the main script
    base_cmd.append('soundcloud_downloader_gui.py')
    
    print(f"Running command: {' '.join(base_cmd)}")
    subprocess.run(base_cmd)
    
    print("\nDebug build completed!")
    
    if system == 'Windows':
        print("\nYour Windows debug executable is available at: dist/SoundCloudDownloader-Debug.exe")
        print("Run this version to see error messages in the console window.")
    elif system == 'Darwin':
        print("\nYour macOS debug app is available at: dist/SoundCloudDownloader-Debug.app")
    
    print("\nAfter identifying the error, you can rebuild the windowless version with the original build script.")

if __name__ == "__main__":
    main() 