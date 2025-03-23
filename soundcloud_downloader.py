import os
import re
import sys
import argparse
import subprocess
import shutil
import platform
import yt_dlp as youtube_dl
import traceback

def get_bundled_ffmpeg_path():
    """Get the path to the bundled FFmpeg binary if available."""
    # Check if we're running from a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running from a PyInstaller bundle
        if platform.system() == 'Windows':
            ffmpeg_path = os.path.join(os.path.dirname(sys.executable), 'ffmpeg.exe')
        else:  # macOS or Linux
            ffmpeg_path = os.path.join(os.path.dirname(sys.executable), 'ffmpeg')
    else:
        # Running from source
        if platform.system() == 'Windows':
            ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_bin', 'ffmpeg.exe')
        else:  # macOS or Linux
            ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_bin', 'ffmpeg')
    
    print(f"DEBUG: Looking for FFmpeg at: {ffmpeg_path}")
    result = ffmpeg_path if os.path.exists(ffmpeg_path) else None
    print(f"DEBUG: FFmpeg found: {result is not None}")
    return result

def check_dependencies():
    """Check if necessary dependencies are installed or bundled."""
    missing_deps = []
    
    # First check for bundled FFmpeg
    bundled_ffmpeg = get_bundled_ffmpeg_path()
    
    # If no bundled FFmpeg, check system PATH
    if not bundled_ffmpeg:
        print("DEBUG: Bundled FFmpeg not found, checking PATH")
        ffmpeg_in_path = shutil.which('ffmpeg')
        print(f"DEBUG: FFmpeg in PATH: {ffmpeg_in_path}")
        if ffmpeg_in_path is None:
            missing_deps.append("FFmpeg")
    
    # Check for AtomicParsley on macOS (needed for embedding thumbnails)
    if platform.system() == 'Darwin':
        atomicparsley = shutil.which('AtomicParsley')
        print(f"DEBUG: AtomicParsley in PATH: {atomicparsley}")
        if atomicparsley is None:
            missing_deps.append("AtomicParsley")
    
    if missing_deps:
        print("ERROR: The following dependencies are missing:")
        for dep in missing_deps:
            if dep == "FFmpeg":
                print("  - FFmpeg: Download from https://ffmpeg.org/download.html and add to PATH")
                print("    - Windows: Download and add to PATH")
                print("    - macOS: Use 'brew install ffmpeg'")
                print("    - Linux: Use 'sudo apt install ffmpeg' or equivalent")
            elif dep == "AtomicParsley":
                print("  - AtomicParsley: Required for embedding thumbnails on macOS")
                print("    - macOS: Use 'brew install atomicparsley'")
        return False
    return True

def is_valid_soundcloud_url(url):
    """Check if the provided URL is a valid SoundCloud URL."""
    pattern = r'^https?://(?:www\.)?soundcloud\.com/[\w-]+(?:/(?:sets/)?[\w-]+)*(?:\?.*)?$'
    result = bool(re.match(pattern, url))
    print(f"DEBUG: URL validation for {url}: {result}")
    return result

def setup_youtube_dl_options(download_path='.'):
    """Configure youtube-dl options for SoundCloud downloads."""
    # Check for bundled FFmpeg and use it if available
    bundled_ffmpeg = get_bundled_ffmpeg_path()
    
    options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Set to highest available quality
            },
            {
                'key': 'EmbedThumbnail',  # Embed artwork as metadata
            },
            {
                'key': 'FFmpegMetadata',  # Add metadata to file
            }
        ],
        'writethumbnail': True,  # Write the thumbnail to disk
        'prefer_ffmpeg': True,
        'keepvideo': False,
        'verbose': True,
        'ignoreerrors': True,  # Skip unavailable tracks in playlists
        'logger': CustomLogger(),  # Add custom logger for debug output
    }
    
    # Add bundled FFmpeg path if available
    if bundled_ffmpeg:
        ffmpeg_dir = os.path.dirname(bundled_ffmpeg)
        print(f"DEBUG: Setting FFmpeg location to: {ffmpeg_dir}")
        options['ffmpeg_location'] = ffmpeg_dir
    
    return options

class CustomLogger:
    """Custom logger for yt-dlp to print debugging info."""
    def debug(self, msg):
        print(f"YT-DLP DEBUG: {msg}")
        
    def info(self, msg):
        print(f"YT-DLP INFO: {msg}")
        
    def warning(self, msg):
        print(f"YT-DLP WARNING: {msg}")
        
    def error(self, msg):
        print(f"YT-DLP ERROR: {msg}")

def download_soundcloud(url, download_path='.'):
    """Download audio from SoundCloud URL (single track or playlist)."""
    print(f"DEBUG: Starting download from {url} to {download_path}")
    
    if not is_valid_soundcloud_url(url):
        print(f"Error: '{url}' is not a valid SoundCloud URL.")
        return False
    
    if not check_dependencies():
        return False
    
    options = setup_youtube_dl_options(download_path)
    
    try:
        print("DEBUG: Initializing YoutubeDL")
        with youtube_dl.YoutubeDL(options) as ydl:
            print("DEBUG: Extracting info and downloading")
            info = ydl.extract_info(url, download=True)
            
            # Check if download was successful
            if info is None:
                print("Error: Failed to extract information from URL")
                return False
            
            # Print details about what was downloaded
            if '_type' in info and info['_type'] == 'playlist':
                print(f"Downloaded playlist: {info.get('title', 'Unknown')}")
                print(f"Total tracks: {len(info.get('entries', []))}")
            else:
                print(f"Downloaded: {info.get('title', 'Unknown')}")
                
        return True
    except youtube_dl.utils.DownloadError as e:
        print(f"Error downloading from {url}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error downloading from {url}: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='Download SoundCloud tracks or playlists at high quality')
    parser.add_argument('url', help='SoundCloud URL (track or playlist)')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory (default: downloads)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Download from the provided URL
    if download_soundcloud(args.url, args.output):
        print(f"Download completed. Files saved to {os.path.abspath(args.output)}")
    else:
        print("Download failed.")

if __name__ == "__main__":
    main() 