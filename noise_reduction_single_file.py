
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
# ---------- End of Single Mode Functions ----------