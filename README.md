# SoundCloud Downloader

A desktop application to download high-quality MP3s (326kbps) from SoundCloud URLs. It supports both individual tracks and playlists.

## Features

- Download single tracks or entire playlists from SoundCloud
- High-quality MP3 format (326kbps where available)
- Embeds artwork in the MP3 files
- Simple graphical user interface
- Available for Windows and macOS
- FFmpeg included - no separate installation required!
- Remembers your preferred download location between sessions

## Prerequisites

- FFmpeg (required for audio conversion)
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your PATH
  - **macOS**: `brew install ffmpeg`

## Installation

### Windows
1. Download the latest SoundCloudDownloader.exe from the releases page
2. Run the executable (no installation required)
3. That's it! FFmpeg is bundled with the application

### macOS
1. Download the latest SoundCloudDownloader.dmg from the releases page
2. Mount the disk image and drag the app to your Applications folder
3. That's it! FFmpeg is bundled with the application

## Development Setup

If you want to run from source or contribute:

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Download FFmpeg for development: `python bundle_ffmpeg.py`
6. Run the GUI app: `python soundcloud_downloader_gui.py`

## Building the App

To build standalone executables with bundled FFmpeg:

1. Install the requirements: `pip install -r requirements.txt`
2. Run the build script: `python build_app.py`
3. Find the compiled application in the `dist` directory

## Command-line Usage

The application also provides a command-line interface:

```
python soundcloud_downloader.py https://soundcloud.com/artist/track-name -o output_directory
```

## Notes

- The downloader will attempt to get the highest quality available (up to 326kbps)
- SoundCloud's actual bitrate may vary depending on the source uploaded by the artist
- Downloads will be saved as MP3 files with appropriate metadata when available "# Soundcloud-downloader" 
