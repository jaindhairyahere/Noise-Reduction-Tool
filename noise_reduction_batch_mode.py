
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
# ---------- End of Batch Mode Functions ----------