
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
