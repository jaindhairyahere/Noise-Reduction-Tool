import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import shutil
import urllib.request
import zipfile
import threading
import time
from ttkthemes import ThemedTk

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
current_light_index = 0
current_dark_index = 0
dark_mode = False

def update_theme_label():
    theme_list = dark_themes if dark_mode else light_themes
    idx = current_dark_index if dark_mode else current_light_index
    theme_btn.config(text=f"Theme: {theme_list[idx]} {'(Dark)' if dark_mode else '(Light)'}")

def cycle_theme():
    global current_light_index, current_dark_index
    if dark_mode:
        current_dark_index = (current_dark_index + 1) % len(dark_themes)
        root.set_theme(dark_themes[current_dark_index])
    else:
        current_light_index = (current_light_index + 1) % len(light_themes)
        root.set_theme(light_themes[current_light_index])
    update_theme_label()

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.set_theme(dark_themes[current_dark_index])
    else:
        root.set_theme(light_themes[current_light_index])
    update_theme_label()

def is_tool_installed(tool_name):
    return shutil.which(tool_name) is not None

def download_and_install_ffmpeg():
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

def check_tools():
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
            disable_all_controls()
            return False
        else:
            messagebox.showwarning(
                "Setup Required",
                "FFmpeg is required to run this tool.\nPlease install it manually and add it to PATH.")
            disable_all_controls()
            return False

    if not sox_found:
        messagebox.showwarning(
            "SoX Not Found",
            f"SoX is required but not found on this system.\n\n"
            f"Please download and install SoX manually from:\n{SOX_DOWNLOAD_URL}\n\n"
            "After installation, add SoX's bin folder to the PATH environment variable.")
        disable_all_controls()
        return False

    enable_all_controls()
    status_label.config(text="All required tools found. Ready to process.")
    return True

def disable_all_controls():
    widgets = [single_browse_btn, single_process_btn, single_entry,
        single_trim_start_entry, single_trim_end_entry,
        single_output_entry, single_browse_output_btn,
        single_overwrite_check,
        batch_browse_files_btn, batch_clear_files_btn,
        batch_file_listbox, batch_output_folder_entry,
        batch_browse_output_folder_btn,
        batch_create_folder_check, batch_prefix_entry, batch_suffix_entry,
        batch_trim_start_entry, batch_trim_end_entry,
        batch_process_btn,
        split_browse_btn, split_entry, split_start_entry, split_end_entry,
        split_output_entry, split_browse_output_btn, split_process_btn,
        merge_add_btn, merge_clear_btn, merge_file_listbox,
        merge_output_entry, merge_browse_output_btn, merge_process_btn
    ]
    for w in widgets:
        w.config(state=tk.DISABLED)

    status_label.config(
        text="Setup in progress... Please wait and do NOT close this window.",
        fg="orange"
    )
    progress_bar['value'] = 0
    est_time_label.config(text="")
    subtle_output_warning.config(text="")
    batch_folder_warning_label.config(text="")

def enable_all_controls():
    widgets = [single_browse_btn, single_process_btn, single_entry,
        single_trim_start_entry, single_trim_end_entry,
        single_output_entry, single_browse_output_btn,
        single_overwrite_check,
        batch_browse_files_btn, batch_clear_files_btn,
        batch_file_listbox, batch_output_folder_entry,
        batch_browse_output_folder_btn,
        batch_create_folder_check, batch_prefix_entry, batch_suffix_entry,
        batch_trim_start_entry, batch_trim_end_entry,
        batch_process_btn,
        split_browse_btn, split_entry, split_start_entry, split_end_entry,
        split_output_entry, split_browse_output_btn, split_process_btn,
        merge_add_btn, merge_clear_btn, merge_file_listbox,
        merge_output_entry, merge_browse_output_btn, merge_process_btn
    ]
    for w in widgets:
        w.config(state=tk.NORMAL)

    status_label.config(text="Ready", fg="blue")
    progress_bar['value'] = 0
    est_time_label.config(text="")
    subtle_output_warning.config(text="")
    batch_folder_warning_label.config(text="")

def color_listbox_rows(listbox):
    for i in range(listbox.size()):
        bg = "#e6f2ff" if i % 2 == 0 else "#f9fbfd"
        listbox.itemconfig(i, {'bg': bg})

# ----------- Main window creation -------------
root = ThemedTk(theme="plastik")
root.title("Noise Reduction Tool - Single & Batch Mode")
root.iconbitmap('noise_reduction_tool.ico')  # Set window icon here

root.geometry("900x650")
root.minsize(700, 500)
root.resizable(True, True)

# Configure grid for fixed toolbar and expanding notebook
root.rowconfigure(0, weight=0)  # Toolbar row
root.rowconfigure(1, weight=1)  # Notebook row grows
root.columnconfigure(0, weight=1)

# Set window background color
root.configure(bg="white")

style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook', background='white')
style.configure('TFrame', background='white')
style.configure('TNotebook.Tab', padding=10, background='white')
style.map('TNotebook.Tab',
          background=[('selected', '#b3d7ff'), ('active', '#d0e7ff')],
          foreground=[('selected', 'black'), ('active', 'black')])

# Create Tkinter variables AFTER root creation
single_overwrite_var = tk.IntVar(master=root, value=1)
batch_create_folder_var = tk.IntVar(master=root, value=1)

# Create a top toolbar frame for theme controls
top_frame = ttk.Frame(root)
top_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)

theme_btn = ttk.Button(top_frame, text="Theme: plastik (Light)", command=cycle_theme)
theme_btn.grid(row=0, column=0, sticky='ew', padx=5)
dark_mode_toggle = ttk.Checkbutton(top_frame, text="Dark Mode", command=toggle_dark_mode)
dark_mode_toggle.grid(row=0, column=1, sticky='ew', padx=5)

update_theme_label()

# Create notebook below toolbar
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

# ---------- Single Mode Functions ----------

def single_browse_file():
    filename = filedialog.askopenfilename(
        title="Select MP4 Video File",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if filename:
        single_entry.delete(0, tk.END)
        single_entry.insert(0, filename)
        single_update_output_default()

def single_update_output_default():
    input_path = single_entry.get().strip()
    if not input_path:
        return

    default_output = os.path.splitext(input_path)[0] + "_denoised.mp4"
    current_output = single_output_entry.get().strip()

    if current_output == "" or current_output.startswith(os.path.splitext(input_path)[0]):
        single_output_entry.delete(0, tk.END)
        single_output_entry.insert(0, default_output)

    single_check_output_file_exists_warning()

def single_browse_output_file():
    filename = filedialog.asksaveasfilename(
        title="Save Output Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if filename:
        single_output_entry.delete(0, tk.END)
        single_output_entry.insert(0, filename)
        single_check_output_file_exists_warning()

def single_check_output_file_exists_warning(*args):
    filepath = single_output_entry.get().strip()
    if filepath != "" and os.path.exists(filepath):
        subtle_output_warning.config(
            text="⚠️ Output file exists, will overwrite if enabled",
            fg="orange"
        )
        single_overwrite_var.set(1)
        single_overwrite_check.config(state=tk.NORMAL)
    else:
        subtle_output_warning.config(text="")
        single_overwrite_check.config(state=tk.NORMAL)

def run_noise_reduction(input_path, trim_start, trim_end, output_path, overwrite, progress_update_callback):
    folder = os.path.dirname(input_path)
    audio_wav = os.path.join(folder, "__tmp_audio.wav")
    cleaned_audio_wav = os.path.join(folder, "__tmp_cleaned_audio.wav")
    noise_prof = os.path.join(folder, "__tmp_noise.prof")

    if os.path.exists(output_path) and not overwrite:
        messagebox.showerror(
            "Error",
            f"Output file already exists:\n{output_path}\nEnable overwrite to replace existing file."
        )
        return False

    if trim_end <= trim_start:
        messagebox.showerror(
            "Error",
            f"Trim End Time ({trim_end}) must be greater than Trim Start Time ({trim_start})."
        )
        return False

    try:
        steps = [
            ("Extracting audio from video...", 0.25, ['ffmpeg', '-y', '-i', input_path, '-q:a', '0', '-map', 'a', audio_wav]),
            ("Generating noise profile...", 0.30, ['sox', audio_wav, '-n', 'trim', str(trim_start), str(trim_end - trim_start), 'noiseprof', noise_prof]),
            ("Reducing noise in audio...", 0.30, ['sox', audio_wav, cleaned_audio_wav, 'noisered', noise_prof, '0.21']),
            ("Merging cleaned audio back to video...", 0.15, ['ffmpeg', '-y', '-i', input_path, '-i', cleaned_audio_wav, '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', output_path])
        ]

        elapsed_start = time.time()
        progress = 0.0

        for desc, portion, cmd in steps:
            progress_update_callback(f"{desc}", progress)
            subprocess.run(cmd, check=True)
            progress += portion

        elapsed_total = time.time() - elapsed_start

        progress_update_callback(f"Finished in ~{int(elapsed_total)} seconds.", 1.0)

        for f in [audio_wav, cleaned_audio_wav, noise_prof]:
            if os.path.exists(f):
                os.remove(f)

        return True

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred during processing:\n{e}")
        return False

def single_start_processing():
    input_path = single_entry.get().strip()
    output_path = single_output_entry.get().strip()

    try:
        trim_start = float(single_trim_start_entry.get().strip())
        trim_end = float(single_trim_end_entry.get().strip())
        if trim_start < 0 or trim_end <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive numbers for Trim Start and End times.")
        return

    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Please select a valid input video file.")
        return
    if output_path == "":
        messagebox.showerror("Error", "Please specify an output file path.")
        return

    overwrite = bool(single_overwrite_var.get())

    disable_all_controls()
    progress_bar['value'] = 0
    est_time_label.config(text="Estimated remaining time: calculating...")
    status_label.config(text="Processing... Please wait.", fg="orange")
    root.update()

    def progress_update(desc, progress_value):
        progress_percent = progress_value * 100
        progress_bar['value'] = progress_percent
        status_label.config(text=desc)
        elapsed = time.time() - single_start_processing.start_time
        if progress_value > 0:
            estimated_total = elapsed / progress_value
            remaining = int(estimated_total - elapsed)
            est_time_label.config(text=f"Estimated remaining time: {remaining} s")
        else:
            est_time_label.config(text="Estimated remaining time: calculating...")

    single_start_processing.start_time = time.time()

    def process_thread():
        success = run_noise_reduction(input_path, trim_start, trim_end, output_path, overwrite, progress_update)
        enable_all_controls()
        est_time_label.config(text="")
        if success:
            single_update_output_default()
            messagebox.showinfo("Success", f"Noise reduction completed.\nOutput saved at:\n{output_path}")

    threading.Thread(target=process_thread, daemon=True).start()

# ---------- Batch Mode Functions ----------

def batch_browse_files():
    files = filedialog.askopenfilenames(
        title="Select Multiple MP4 Video Files",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if files:
        batch_file_listbox.delete(0, tk.END)
        for file in files:
            batch_file_listbox.insert(tk.END, file)
        if files:
            batch_output_folder_entry.delete(0, tk.END)
            batch_output_folder_entry.insert(0, os.path.dirname(files[0]))
            batch_check_output_folder_existence()

def batch_clear_files():
    batch_file_listbox.delete(0, tk.END)

def batch_browse_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        batch_output_folder_entry.delete(0, tk.END)
        batch_output_folder_entry.insert(0, folder)
        batch_check_output_folder_existence()

def batch_check_output_folder_existence(*args):
    folder_path = batch_output_folder_entry.get().strip()
    if folder_path == "":
        batch_folder_warning_label.config(text="")
        batch_create_folder_check.config(state=tk.DISABLED)
        return

    if not os.path.exists(folder_path):
        batch_folder_warning_label.config(text="⚠️ Output folder does not exist. Will create if checkbox is selected.")
        batch_create_folder_check.config(state=tk.NORMAL)
        batch_create_folder_var.set(1)
    else:
        batch_folder_warning_label.config(text="")
        batch_create_folder_check.config(state=tk.DISABLED)
        batch_create_folder_var.set(0)

def batch_run_noise_reduction_for_file(input_path, prefix, suffix, output_folder, trim_start, trim_end, progress_callback):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_name = f"{prefix}{base_name}{suffix}.mp4"
    output_path = os.path.join(output_folder, output_name)
    # Overwrite always on for batch mode
    return run_noise_reduction(input_path, trim_start, trim_end, output_path, True, progress_callback)

def batch_start_processing():
    files = batch_file_listbox.get(0, tk.END)
    if not files:
        messagebox.showerror("Error", "Please add at least one input video file.")
        return

    output_folder = batch_output_folder_entry.get().strip()
    create_folder = bool(batch_create_folder_var.get())

    if output_folder == "":
        messagebox.showerror("Error", "Please specify a valid output folder.")
        return

    if not os.path.exists(output_folder):
        if create_folder:
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output folder:\n{e}")
                return
        else:
            messagebox.showerror("Error", "Output folder does not exist and 'Create output folder' is not checked.")
            return

    prefix = batch_prefix_entry.get()
    suffix = batch_suffix_entry.get()

    try:
        trim_start = float(batch_trim_start_entry.get().strip())
        trim_end = float(batch_trim_end_entry.get().strip())
        if trim_start < 0 or trim_end <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter valid positive numbers for Trim Start and End times.")
        return

    if trim_end <= trim_start:
        messagebox.showerror("Error", "Trim End Time must be greater than Trim Start Time.")
        return

    disable_all_controls()
    progress_bar['value'] = 0
    est_time_label.config(text="Starting batch processing...")
    status_label.config(text="Processing batch files... Please wait.", fg="orange")
    root.update()

    total_files = len(files)

    def progress_update(desc, progress_value):
        progress_percent = ((batch_start_processing.files_done + progress_value) / total_files) * 100
        progress_bar['value'] = progress_percent
        status_label.config(text=f"{desc} (File {batch_start_processing.files_done+1}/{total_files})")
        elapsed = time.time() - batch_start_processing.start_time
        if progress_percent > 0:
            estimated_total = elapsed * 100 / progress_percent
            remaining = int(estimated_total - elapsed)
            est_time_label.config(text=f"Estimated remaining time: {remaining} s")
        else:
            est_time_label.config(text="Estimated remaining time: calculating...")

    batch_start_processing.start_time = time.time()
    batch_start_processing.files_done = 0

    def batch_process_thread():
        success_all = True
        for f in files:
            progress_update(f"Processing {os.path.basename(f)}", 0)
            success = batch_run_noise_reduction_for_file(
                f, prefix, suffix, output_folder, trim_start, trim_end, progress_update)
            if not success:
                success_all = False
                break
            batch_start_processing.files_done += 1

        enable_all_controls()
        est_time_label.config(text="")
        if success_all:
            messagebox.showinfo("Batch Complete", "Batch noise reduction completed for all files.")
        else:
            messagebox.showwarning("Batch Stopped", "Batch processing stopped due to error.")

    threading.Thread(target=batch_process_thread, daemon=True).start()

# ---------- Split Mode Functions ----------
def split_browse_file():
    filename = filedialog.askopenfilename(title="Select MP4 Video File", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if filename:
        split_entry.delete(0, tk.END)
        split_entry.insert(0, filename)

def split_browse_output_file():
    filename = filedialog.asksaveasfilename(title="Save Split Video As", defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if filename:
        split_output_entry.delete(0, tk.END)
        split_output_entry.insert(0, filename)

def split_process():
    input_file = split_entry.get()
    start_time = split_start_entry.get()
    end_time = split_end_entry.get()
    output_file = split_output_entry.get()
    if not os.path.exists(input_file):
        messagebox.showerror("Error", "Please select a valid input video file.")
        return
    if not output_file:
        messagebox.showerror("Error", "Please specify an output file.")
        return
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-ss", start_time, "-to", end_time, "-c", "copy", output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Split completed.\nOutput saved to:\n{output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Split failed. Check ffmpeg installation and input values.")

# ---------- Merge Mode Functions ----------
def merge_add_files():
    files = filedialog.askopenfilenames(title="Select MP4 Video Files to Merge", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    for file in files:
        merge_file_listbox.insert(tk.END, file)
def merge_clear_files():
    merge_file_listbox.delete(0, tk.END)
def merge_browse_output_file():
    filename = filedialog.asksaveasfilename(title="Save Merged Video As", defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if filename:
        merge_output_entry.delete(0, tk.END)
        merge_output_entry.insert(0, filename)

def move_selection(lstbox, direction):
    sel = lstbox.curselection()
    if not sel:
        return
    if direction == "up":
        for idx in sel:
            if idx == 0:
                continue
            item = lstbox.get(idx)
            lstbox.delete(idx)
            lstbox.insert(idx - 1, item)
            lstbox.selection_set(idx - 1)
            lstbox.selection_clear(idx)
    elif direction == "down":
        for idx in reversed(sel):
            if idx == lstbox.size() - 1:
                continue
            item = lstbox.get(idx)
            lstbox.delete(idx)
            lstbox.insert(idx + 1, item)
            lstbox.selection_set(idx + 1)
            lstbox.selection_clear(idx)

def merge_process():
    files = merge_file_listbox.get(0, tk.END)
    output_file = merge_output_entry.get()
    if len(files) < 2:
        messagebox.showerror("Error", "Select at least two files to merge.")
        return
    if not output_file:
        messagebox.showerror("Error", "Specify an output file.")
        return

    output_dir = os.path.dirname(output_file)
    temp_list_path = os.path.join(output_dir, "__tmp_merge_list.txt")

    try:
        with open(temp_list_path, "w") as f:
            for fname in files:
                f.write(f"file '{fname}'\n")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", temp_list_path,
            "-c", "copy", output_file
        ]
        disable_all_controls()
        status_label.config(text="Merging videos... Please wait.", fg="orange")
        root.update()
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Merged video saved to:\n{output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Merge failed. Check ffmpeg installation and input files.")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error:\n{e}")
    finally:
        if os.path.exists(temp_list_path):
            os.remove(temp_list_path)
        enable_all_controls()

# ---------- GUI Layout ----------

# --- Single Mode Tab ---
single_tab = ttk.Frame(notebook)
notebook.add(single_tab, text="Single Mode")

tk.Label(single_tab, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
single_entry = tk.Entry(single_tab, width=50)
single_entry.grid(row=0, column=1, padx=10, pady=10)
single_browse_btn = tk.Button(single_tab, text="Browse...", command=single_browse_file)
single_browse_btn.grid(row=0, column=2, padx=10, pady=10)

tk.Label(single_tab, text="Noise Profile Trim Start (seconds):").grid(row=1, column=0, padx=10, pady=6, sticky='w')
single_trim_start_entry = tk.Entry(single_tab, width=10)
single_trim_start_entry.insert(0, "0.0")
single_trim_start_entry.grid(row=1, column=1, sticky='w', padx=10, pady=6)

tk.Label(single_tab, text="Noise Profile Trim End (seconds):").grid(row=2, column=0, padx=10, pady=6, sticky='w')
single_trim_end_entry = tk.Entry(single_tab, width=10)
single_trim_end_entry.insert(0, "2.0")
single_trim_end_entry.grid(row=2, column=1, sticky='w', padx=10, pady=6)

tk.Label(single_tab, text="Output Video File:").grid(row=3, column=0, padx=10, pady=6, sticky='w')
single_output_entry = tk.Entry(single_tab, width=50)
single_output_entry.grid(row=3, column=1, padx=10, pady=6)

single_browse_output_btn = tk.Button(single_tab, text="Browse...", command=single_browse_output_file)
single_browse_output_btn.grid(row=3, column=2, padx=10, pady=6)

subtle_output_warning = tk.Label(single_tab, text="", fg="orange")
subtle_output_warning.grid(row=4, column=1, sticky='w', padx=10, pady=(0, 10))

single_overwrite_check = tk.Checkbutton(single_tab, text="Overwrite if output file exists", variable=single_overwrite_var)
single_overwrite_check.grid(row=5, column=1, padx=10, pady=(0, 10), sticky='w')

single_process_btn = tk.Button(single_tab, text="Run Noise Reduction", command=single_start_processing)
single_process_btn.grid(row=6, column=0, columnspan=3, padx=10, pady=15)

# --- Batch Mode Tab ---
batch_tab = ttk.Frame(notebook)
notebook.add(batch_tab, text="Batch Mode")

batch_browse_files_btn = tk.Button(batch_tab, text="Add Video Files...", command=batch_browse_files)
batch_browse_files_btn.grid(row=0, column=0, padx=10, pady=10, sticky='w')

batch_clear_files_btn = tk.Button(batch_tab, text="Clear List", command=batch_clear_files)
batch_clear_files_btn.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# --- Batch listbox with scrollbars ---
batch_file_listbox_frame = tk.Frame(batch_tab)
batch_file_listbox_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

batch_file_listbox_vsb = tk.Scrollbar(batch_file_listbox_frame, orient="vertical")
batch_file_listbox_hsb = tk.Scrollbar(batch_file_listbox_frame, orient="horizontal")
batch_file_listbox = tk.Listbox(batch_file_listbox_frame, selectmode=tk.EXTENDED, width=60, height=8,
                                yscrollcommand=batch_file_listbox_vsb.set,
                                xscrollcommand=batch_file_listbox_hsb.set)
batch_file_listbox.grid(row=0, column=0, sticky='nsew')
batch_file_listbox_vsb.grid(row=0, column=1, sticky='ns')
batch_file_listbox_hsb.grid(row=1, column=0, sticky='ew')
batch_file_listbox_frame.rowconfigure(0, weight=1)
batch_file_listbox_frame.columnconfigure(0, weight=1)
batch_file_listbox_vsb.config(command=batch_file_listbox.yview)
batch_file_listbox_hsb.config(command=batch_file_listbox.xview)

tk.Label(batch_tab, text="Output Folder:").grid(row=2, column=0, padx=10, pady=6, sticky='w')
batch_output_folder_entry = tk.Entry(batch_tab, width=50)
batch_output_folder_entry.grid(row=2, column=1, padx=10, pady=6)

batch_browse_output_folder_btn = tk.Button(batch_tab, text="Browse...", command=batch_browse_output_folder)
batch_browse_output_folder_btn.grid(row=2, column=2, padx=10, pady=6)

batch_create_folder_check = tk.Checkbutton(batch_tab, text="Create output folder if it does not exist", variable=batch_create_folder_var)
batch_create_folder_check.grid(row=3, column=1, sticky='w', padx=10, pady=(0,10))

batch_folder_warning_label = tk.Label(batch_tab, text="", fg="orange")
batch_folder_warning_label.grid(row=4, column=1, sticky='w', padx=10, pady=(0, 10))

tk.Label(batch_tab, text="Output Prefix:").grid(row=5, column=0, padx=10, pady=6, sticky='w')
batch_prefix_entry = tk.Entry(batch_tab, width=20)
batch_prefix_entry.insert(0, "")
batch_prefix_entry.grid(row=5, column=1, sticky='w', padx=10, pady=6)

tk.Label(batch_tab, text="Output Suffix:").grid(row=6, column=0, padx=10, pady=6, sticky='w')
batch_suffix_entry = tk.Entry(batch_tab, width=20)
batch_suffix_entry.insert(0, "_denoised")
batch_suffix_entry.grid(row=6, column=1, sticky='w', padx=10, pady=6)

tk.Label(batch_tab, text="Noise Profile Trim Start (seconds):").grid(row=7, column=0, padx=10, pady=6, sticky='w')
batch_trim_start_entry = tk.Entry(batch_tab, width=10)
batch_trim_start_entry.insert(0, "0.0")
batch_trim_start_entry.grid(row=7, column=1, sticky='w', padx=10, pady=6)

tk.Label(batch_tab, text="Noise Profile Trim End (seconds):").grid(row=8, column=0, padx=10, pady=6, sticky='w')
batch_trim_end_entry = tk.Entry(batch_tab, width=10)
batch_trim_end_entry.insert(0, "2.0")
batch_trim_end_entry.grid(row=8, column=1, sticky='w', padx=10, pady=6)

batch_process_btn = tk.Button(batch_tab, text="Run Batch Noise Reduction", command=batch_start_processing)
batch_process_btn.grid(row=9, column=0, columnspan=3, padx=10, pady=15)

# --- Split Tab ---
split_tab = ttk.Frame(notebook)
notebook.add(split_tab, text="Split")
tk.Label(split_tab, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
split_entry = tk.Entry(split_tab, width=50)
split_entry.grid(row=0, column=1, padx=10, pady=10)
split_browse_btn = tk.Button(split_tab, text="Browse...", command=split_browse_file)
split_browse_btn.grid(row=0, column=2, padx=10, pady=10)
tk.Label(split_tab, text="Start Time (HH:MM:SS):").grid(row=1, column=0, padx=10, pady=6, sticky='w')
split_start_entry = tk.Entry(split_tab, width=10)
split_start_entry.insert(0, "00:00:00")
split_start_entry.grid(row=1, column=1, sticky='w', padx=10, pady=6)
tk.Label(split_tab, text="End Time (HH:MM:SS):").grid(row=2, column=0, padx=10, pady=6, sticky='w')
split_end_entry = tk.Entry(split_tab, width=10)
split_end_entry.insert(0, "00:00:10")
split_end_entry.grid(row=2, column=1, sticky='w', padx=10, pady=6)
tk.Label(split_tab, text="Output File:").grid(row=3, column=0, padx=10, pady=6, sticky='w')
split_output_entry = tk.Entry(split_tab, width=50)
split_output_entry.grid(row=3, column=1, padx=10, pady=6)
split_browse_output_btn = tk.Button(split_tab, text="Browse...", command=split_browse_output_file)
split_browse_output_btn.grid(row=3, column=2, padx=10, pady=6)
split_process_btn = tk.Button(split_tab, text="Split Video", command=split_process)
split_process_btn.grid(row=4, column=0, columnspan=3, padx=10, pady=15)

# --- Merge Tab ---
merge_tab = ttk.Frame(notebook)
notebook.add(merge_tab, text="Merge")

merge_file_listbox_frame = tk.Frame(merge_tab)
merge_file_listbox_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky='nsew')

merge_file_listbox_vsb = tk.Scrollbar(merge_file_listbox_frame, orient="vertical")
merge_file_listbox_hsb = tk.Scrollbar(merge_file_listbox_frame, orient="horizontal")
merge_file_listbox = tk.Listbox(
    merge_file_listbox_frame,
    selectmode=tk.EXTENDED,
    width=60, height=8,
    yscrollcommand=merge_file_listbox_vsb.set,
    xscrollcommand=merge_file_listbox_hsb.set
)
merge_file_listbox.grid(row=0, column=0, sticky='nsew')
merge_file_listbox_vsb.grid(row=0, column=1, sticky='ns')
merge_file_listbox_hsb.grid(row=1, column=0, sticky='ew')

merge_file_listbox_frame.rowconfigure(0, weight=1)
merge_file_listbox_frame.columnconfigure(0, weight=1)

merge_file_listbox_vsb.config(command=merge_file_listbox.yview)
merge_file_listbox_hsb.config(command=merge_file_listbox.xview)

merge_add_btn = tk.Button(merge_tab, text="Add Files...", command=lambda: (
    [merge_file_listbox.insert(tk.END, f) for f in filedialog.askopenfilenames(
        title="Select MP4 Video Files to Merge",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )],
    [merge_file_listbox.itemconfig(i, {'bg': "#e6f2ff" if i % 2 == 0 else "#f9fbfd"}) for i in range(merge_file_listbox.size())]
))
merge_add_btn.grid(row=0, column=0, padx=10, pady=10, sticky='w')

merge_clear_btn = tk.Button(merge_tab, text="Clear List", command=lambda: (
    merge_file_listbox.delete(0, tk.END)
))
merge_clear_btn.grid(row=0, column=1, padx=10, pady=10, sticky='w')

merge_up_btn = tk.Button(merge_tab, text="Move Up", command=lambda: move_selection(merge_file_listbox, "up"))
merge_down_btn = tk.Button(merge_tab, text="Move Down", command=lambda: move_selection(merge_file_listbox, "down"))

merge_up_btn.grid(row=0, column=2, padx=10, pady=10, sticky='w')
merge_down_btn.grid(row=0, column=3, padx=10, pady=10, sticky='w')

tk.Label(merge_tab, text="Output File:").grid(row=2, column=0, padx=10, pady=6, sticky='w')
merge_output_entry = tk.Entry(merge_tab, width=55)
merge_output_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=6, sticky='ew')

merge_browse_output_btn = tk.Button(merge_tab, text="Browse...", command=lambda: (
    (lambda filename: (
        merge_output_entry.delete(0, tk.END),
        merge_output_entry.insert(0, filename)
    ))(filedialog.asksaveasfilename(title="Save Merged Video As",
                                    defaultextension=".mp4",
                                    filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]))
))
merge_browse_output_btn.grid(row=2, column=3, padx=10, pady=6)

merge_process_btn = tk.Button(merge_tab, text="Merge Videos", command=merge_process)
merge_process_btn.grid(row=3, column=0, columnspan=4, padx=10, pady=15)

# Progress bar and estimated time shared across tabs
progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 5))

est_time_label = tk.Label(root, text="", fg="green")
est_time_label.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10))

status_label = tk.Label(root, text="Checking tools installation...", fg="blue")
status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

# Bind output path existence warning in single mode
single_output_entry.bind('<KeyRelease>', single_check_output_file_exists_warning)

# Bind output folder existence check in batch mode
batch_output_folder_entry.bind('<KeyRelease>', batch_check_output_folder_existence)

disable_all_controls()
def on_startup():
    def check():
        check_tools()
    threading.Thread(target=check).start()

on_startup()

for tab in [batch_tab, merge_tab]:
    tab.rowconfigure(1, weight=1)
    tab.columnconfigure(0, weight=1)

root.mainloop()
