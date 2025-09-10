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
from functools import partial
from constants import FFMPEG_BIN_PATH, FFMPEG_INSTALL_PATH, SOX_DOWNLOAD_URL, light_themes, dark_themes
from check_setup import check_tools, is_tool_installed, download_and_install_ffmpeg
from gui_helper import cycle_theme, toggle_dark_mode, update_theme_label, disable_all_controls, enable_all_controls
from noise_reduction_single_file import single_browse_file, single_browse_output_file, single_start_processing, single_check_output_file_exists_warning
from noise_reduction_batch_mode import batch_browse_files, batch_browse_output_folder, batch_start_processing, batch_clear_files, batch_check_output_folder_existence
from split_video import split_browse_file, split_browse_output_file, split_process
from merge_video import merge_process, move_selection

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

theme_btn = ttk.Button(top_frame, text="Theme: plastik (Light)")
theme_btn.config(command=cycle_theme(root, theme_btn))
theme_btn.grid(row=0, column=0, sticky='ew', padx=5)

dark_mode_toggle = ttk.Checkbutton(top_frame, text="Dark Mode")
dark_mode_toggle.config(command=cycle_theme(root, dark_mode_toggle))
dark_mode_toggle.grid(row=0, column=1, sticky='ew', padx=5)

update_theme_label(theme_btn)

# Create notebook below toolbar
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)


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

disable_all_controls(widgets, status_label, progress_bar, est_time_label, subtle_output_warning, batch_folder_warning_label)
def on_startup():
    def check():
        if check_tools(status_label, root, messagebox):
            enable_all_controls(widgets, status_label, progress_bar, est_time_label, subtle_output_warning, batch_folder_warning_label)
        else:
            disable_all_controls(widgets, status_label, progress_bar, est_time_label, subtle_output_warning, batch_folder_warning_label)
    threading.Thread(target=check).start()

on_startup()

for tab in [batch_tab, merge_tab]:
    tab.rowconfigure(1, weight=1)
    tab.columnconfigure(0, weight=1)

root.mainloop()
