import json
import pandas as pd
from pathlib import Path
from deepdiff import DeepDiff
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

def flatten_path(path_obj):
    return (
        path_obj.replace("root", "")
        .replace("['", "")
        .replace("']", "")
        .replace("']['", ".")
        .replace("'][", ".")
        .strip(".")
    )

def compare_folders(before_folder, after_folder, output_file, progress_var, percent_label, progress_bar, progress_win):
    before_files = [f.name for f in Path(before_folder).iterdir() if f.is_file()]
    after_files = [f.name for f in Path(after_folder).iterdir() if f.is_file()]
    common_files = list(set(before_files).intersection(after_files))

    total_files = len(common_files)
    records = []

    for idx, fname in enumerate(common_files, start=1):
        with open(f"{before_folder}/{fname}") as f1, open(f"{after_folder}/{fname}") as f2:
            old_data = json.load(f1)
            new_data = json.load(f2)

        diff = DeepDiff(old_data, new_data, ignore_order=True, view='tree')

        if diff:
            for change_type, changes in diff.items():
                for change in changes:
                    records.append([
                        Path(before_folder).name,
                        fname,
                        change_type,
                        flatten_path(change.path()),
                        getattr(change, 't1', None),
                        getattr(change, 't2', None)
                    ])
        else:
            records.append([Path(before_folder).name, fname, 'no_change', None, None, None])

        # Update progress bar and label
        progress = int((idx / total_files) * 100)
        progress_var.set(progress)
        percent_label.config(text=f"{progress}% complete")
        progress_bar.update()

    df = pd.DataFrame(records, columns=['date','file','change_type','parameter','old','new'])
    df.to_csv(output_file, index=False)
    messagebox.showinfo("Done", f"✅ Comparison complete.\nResults saved to:\n{output_file}")
    progress_win.destroy()

def run_app():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Select Folders", "Please select the BEFORE folder")
    before_folder = filedialog.askdirectory(title="Select BEFORE folder")

    messagebox.showinfo("Select Folders", "Please select the AFTER folder")
    after_folder = filedialog.askdirectory(title="Select AFTER folder")

    if not before_folder or not after_folder:
        messagebox.showwarning("Cancelled", "❌ Folders not selected. Exiting.")
        return

    if before_folder == after_folder:
        messagebox.showerror("Invalid Selection", "⚠️ BEFORE and AFTER folders must be different.\nPlease try again.")
        return

    messagebox.showinfo("Destination", "Now select the destination folder and filename for the CSV output")
    default_name = f"changes_{datetime.now().strftime('%Y-%m-%d')}.csv"
    output_file = filedialog.asksaveasfilename(
        title="Save results as...",
        initialfile=default_name,
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if not output_file:
        messagebox.showwarning("Cancelled", "❌ No destination selected. Exiting.")
        return

    # Create progress window
    progress_win = tk.Toplevel()
    progress_win.title("Processing Files")
    tk.Label(progress_win, text="Comparing JSON files...").pack(pady=10)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(progress_win, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10)

    percent_label = tk.Label(progress_win, text="0% complete")
    percent_label.pack(pady=5)

    # Run comparison in a separate thread so GUI stays responsive
    threading.Thread(target=compare_folders, args=(before_folder, after_folder, output_file, progress_var, percent_label, progress_bar, progress_win)).start()

    progress_win.mainloop()

if __name__ == "__main__":
    run_app()
