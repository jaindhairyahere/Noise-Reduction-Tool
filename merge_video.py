
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
