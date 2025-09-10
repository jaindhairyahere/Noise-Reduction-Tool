import tkinter as tk
from global_variables import current_light_index, current_dark_index, dark_mode
from constants import light_themes, dark_themes

current_light_index = 0
current_dark_index = 0
dark_mode = False

def update_theme_label(theme_btn):
    global current_light_index, current_dark_index, dark_mode
    theme_list = dark_themes if dark_mode else light_themes
    idx = current_dark_index if dark_mode else current_light_index
    theme_btn.config(text=f"Theme: {theme_list[idx]} {'(Dark)' if dark_mode else '(Light)'}")

def cycle_theme(root, theme_btn):
    def wrapped():
        global current_light_index, current_dark_index, dark_mode
        if dark_mode:
            current_dark_index = (current_dark_index + 1) % len(dark_themes)
            root.set_theme(dark_themes[current_dark_index])
        else:
            current_light_index = (current_light_index + 1) % len(light_themes)
            root.set_theme(light_themes[current_light_index])
        update_theme_label(theme_btn)
    return wrapped

def toggle_dark_mode(root, theme_btn):
    def wrapped():
        global dark_mode
        dark_mode = not dark_mode
        if dark_mode:
            root.set_theme(dark_themes[current_dark_index])
        else:
            root.set_theme(light_themes[current_light_index])
        update_theme_label(theme_btn)
    return wrapped

def disable_all_controls(widgets, status_label, progress_bar, est_time_label, subtle_output_warning, batch_folder_warning_label):
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

def enable_all_controls(widgets, status_label, progress_bar, est_time_label, subtle_output_warning, batch_folder_warning_label):
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
