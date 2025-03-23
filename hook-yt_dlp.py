from PyInstaller.utils.hooks import collect_all

# Tell PyInstaller to collect all of yt_dlp's files and dependencies
datas, binaries, hiddenimports = collect_all('yt_dlp')

# Add additional hidden imports
hiddenimports += [
    'yt_dlp.extractor',
    'yt_dlp.downloader',
    'yt_dlp.postprocessor',
    'yt_dlp.utils',
] 