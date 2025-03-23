#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import requests
import zipfile
import tarfile
import tempfile
from tqdm import tqdm

FFMPEG_DOWNLOADS = {
    'Windows': {
        'url': 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
        'bin_path': 'ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'
    },
    'Darwin': {  # macOS
        'url': 'https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip',
        'bin_path': 'ffmpeg'
    }
}

def download_file(url, destination):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(destination, 'wb') as file, tqdm(
            desc=f"Downloading {os.path.basename(destination)}",
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)
    
    return destination

def extract_archive(archive_path, extract_to):
    """Extract zip or tar archive"""
    print(f"Extracting {archive_path}...")
    
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
    
    print(f"Extracted to {extract_to}")

def download_ffmpeg():
    """Download FFmpeg for the current platform"""
    system = platform.system()
    
    if system not in FFMPEG_DOWNLOADS:
        print(f"Error: Unsupported platform {system}")
        return None
    
    ffmpeg_info = FFMPEG_DOWNLOADS[system]
    ffmpeg_url = ffmpeg_info['url']
    bin_path = ffmpeg_info['bin_path']
    
    # Create a directory for FFmpeg binaries
    os.makedirs('ffmpeg_bin', exist_ok=True)
    
    # Download FFmpeg archive
    print(f"Downloading FFmpeg for {system}...")
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Download the archive
        archive_path = os.path.join(temp_dir, 'ffmpeg.zip')
        download_file(ffmpeg_url, archive_path)
        
        # Extract the archive
        extract_to = os.path.join(temp_dir, 'extracted')
        extract_archive(archive_path, extract_to)
        
        # Copy the FFmpeg binary to our directory
        ffmpeg_path = os.path.join(extract_to, bin_path)
        
        if system == 'Windows':
            dest_path = os.path.join('ffmpeg_bin', 'ffmpeg.exe')
        else:  # macOS
            dest_path = os.path.join('ffmpeg_bin', 'ffmpeg')
        
        shutil.copy2(ffmpeg_path, dest_path)
        
        # Make executable on macOS/Linux
        if system != 'Windows':
            os.chmod(dest_path, 0o755)
        
        print(f"FFmpeg binary copied to {dest_path}")
        return dest_path
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Downloading FFmpeg for bundling...")
    ffmpeg_path = download_ffmpeg()
    
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        print(f"FFmpeg successfully downloaded to {ffmpeg_path}")
        print("Ready for bundling with the application")
    else:
        print("Failed to download FFmpeg")
        sys.exit(1) 