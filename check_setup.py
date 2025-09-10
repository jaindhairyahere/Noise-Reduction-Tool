import shutil
import os
from constants import FFMPEG_BIN_PATH, FFMPEG_INSTALL_PATH, SOX_DOWNLOAD_URL

def is_tool_installed(tool_name):
    return shutil.which(tool_name) is not None

def download_and_install_ffmpeg(messagebox):
    try:
        zip_path = os.path.join(os.getenv('TEMP'), "ffmpeg.zip")
        urllib.request.urlretrieve(
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(FFMPEG_INSTALL_PATH)

        extracted_folder = next(os.scandir(FFMPEG_INSTALL_PATH))
        extracted_bin = os.path.join(extracted_folder.path, "bin")
        dest_bin_path = os.path.join(FFMPEG_INSTALL_PATH, "bin")

        if os.path.exists(dest_bin_path):
            shutil.rmtree(dest_bin_path)
        shutil.move(extracted_bin, dest_bin_path)

        for item in os.listdir(FFMPEG_INSTALL_PATH):
            full_path = os.path.join(FFMPEG_INSTALL_PATH, item)
            if item != "bin":
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)

        os.remove(zip_path)

        messagebox.showinfo("FFmpeg Installed", f"FFmpeg installed to:\n{dest_bin_path}\n\n"
                                               f"Please add this folder to your system PATH environment variable if not already present.\n"
                                               "After that, restart this tool.")
    except Exception as e:
        messagebox.showerror("Installation Error", f"Error installing FFmpeg:\n{e}")

def check_tools(status_label, root, messagebox):
    ffmpeg_found = is_tool_installed("ffmpeg") or os.path.exists(FFMPEG_BIN_PATH)
    sox_found = is_tool_installed("sox")

    if not ffmpeg_found:
        resp = messagebox.askyesno(
            "FFmpeg Not Found",
            "FFmpeg is required but not found on this system.\n\n"
            "Download and install FFmpeg automatically?")
        if resp:
            status_label.config(text="Downloading and installing FFmpeg...")
            root.update()
            download_and_install_ffmpeg()
            status_label.config(text="Please add FFmpeg bin folder to PATH and restart the tool.")
            return False
        else:
            messagebox.showwarning(
                "Setup Required",
                "FFmpeg is required to run this tool.\nPlease install it manually and add it to PATH.")
            return False

    if not sox_found:
        messagebox.showwarning(
            "SoX Not Found",
            f"SoX is required but not found on this system.\n\n"
            f"Please download and install SoX manually from:\n{SOX_DOWNLOAD_URL}\n\n"
            "After installation, add SoX's bin folder to the PATH environment variable.")
        return False

    status_label.config(text="All required tools found. Ready to process.")
    return True

