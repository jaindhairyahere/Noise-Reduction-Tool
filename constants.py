import os

FFMPEG_INSTALL_PATH = os.path.expanduser("~\\ffmpeg")
FFMPEG_BIN_PATH = os.path.join(FFMPEG_INSTALL_PATH, "bin", "ffmpeg.exe")
SOX_DOWNLOAD_URL = "https://sourceforge.net/projects/sox/files/sox/14.4.2/sox-14.4.2-win32.exe/download"

light_themes = [
    'clam', 'clearlooks', 'winxpblue', 'default', 'radiance',
    'breeze', 'equilux', 'plastik', 'arc'
]

dark_themes = [
    'black', 'scidgreen', 'scidgrey', 'scidpink', 'scidpurple',
    'yaru', 'equilux', 'breeze'
]
