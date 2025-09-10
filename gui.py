# gui.py
import tkinter as tk
from tkinter import messagebox

MIN_COLLAPSED = 30
MAX_WIDTH = 500
DEFAULT_WIDTH = 220
GRIP_WIDTH = 6

class Sidebar(tk.Frame):
    """Reusable sidebar with toggle, resize grip, import button, and find duplicates."""

    def __init__(self, master, side="left", width=DEFAULT_WIDTH, db=None,
                 photo_viewer=None, import_command=None, **kwargs):
        super().__init__(master, width=width, **kwargs)
        self.master = master
        self.side = side
        self.width = width
        self.collapsed = False

        # Toolbar
        self.toolbar = tk.Frame(self, bg="#2f2f2f")
        self.toolbar.pack(fill="x")

        if side == "left":
            self.toggle_btn = tk.Button(self.toolbar, text="⮜", width=2, command=self.toggle)
            self.toggle_btn.pack(side="right", padx=4, pady=4)
            self.grip = tk.Frame(self, cursor="sb_h_double_arrow", bg="#454545", width=GRIP_WIDTH)
            self.grip.pack(side="right", fill="y")
        else:
            self.toggle_btn = tk.Button(self.toolbar, text="⮞", width=2, command=self.toggle)
            self.toggle_btn.pack(side="left", padx=4, pady=4)
            self.grip = tk.Frame(self, cursor="sb_h_double_arrow", bg="#454545", width=GRIP_WIDTH)
            self.grip.pack(side="left", fill="y")

        # Bind resize events
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._do_resize)

        # Store db and photo viewer references
        self.db = db
        self.photo_viewer = photo_viewer

        # --- Import Button ---
        if import_command:
            self.import_btn = tk.Button(self, text="Import Files", command=import_command)
            self.import_btn.pack(padx=10, pady=10, anchor="n")
            self.progress_label = tk.Label(self, text="", fg="white", bg="#2f2f2f")
            self.progress_label.pack(padx=10, pady=5, anchor="n")

        # --- Find Duplicates Button ---
        if self.db and self.photo_viewer:
            self.dup_btn = tk.Button(self, text="Find Duplicates", command=self.find_duplicates)
            self.dup_btn.pack(padx=10, pady=10, anchor="n")

    # ----------------- Toggle -----------------
    def toggle(self):
        self.collapsed = not self.collapsed
        self.master.update_layout()

    # ----------------- Resize -----------------
    def _start_resize(self, event):
        self._start_x = self.grip.winfo_rootx()
        self._start_width = self.width
        if self.collapsed:
            self.collapsed = False

    def _do_resize(self, event):
        mouse_x = self.grip.winfo_pointerx()
        delta = mouse_x - self._start_x if self.side == "left" else self._start_x - mouse_x
        self.width = max(MIN_COLLAPSED, min(MAX_WIDTH, self._start_width + delta))
        self.master.update_layout()

    # ----------------- Find Duplicates -----------------
    def find_duplicates(self):
        try:
            if hasattr(self.master.importer, "duplicates"):
                duplicates_detector = self.master.importer.duplicates

                # --- TODO:  TEMP: process all photos in DB ---
                photo_list = self.db.get_all_photos()  # list of dicts with 'id' and 'file_path'
                duplicates_detector.find_duplicates_batch(photo_list)

                messagebox.showinfo(
                    "Duplicates Found",
                    "Near-duplicate detection complete (TEMP: all photos)."
                )

                # Refresh photo viewer to mark duplicates visually
                self.photo_viewer.refresh_photos(None)  # None -> refresh all

            else:
                messagebox.showwarning("Not Available", "Duplicate detection is not configured.")

        except Exception as e:
            messagebox.showerror("Error", f"Error finding duplicates: {e}")
