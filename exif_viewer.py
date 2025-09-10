import tkinter as tk
from tkinter import ttk
from db import Database

MIN_COLLAPSED_HEIGHT = 30  # height when collapsed
DEFAULT_HEIGHT = 400       # default expanded height
GRIP_HEIGHT = 6            # height of resize grip

class ExifViewer(tk.Frame):
    """
    Right-hand panel to display EXIF data of a selected photo.
    Supports vertical collapse/expand and manual resizing via a grip.
    """
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.collapsed = False
        self.expanded_height = DEFAULT_HEIGHT

        self.pack_propagate(False)  # prevent auto-resize
        self.configure(height=self.expanded_height)

        # Top bar with toggle button
        self.top_bar = tk.Frame(self, bg="#2f2f2f")
        self.top_bar.pack(fill="x")

        self.toggle_btn = tk.Button(
            self.top_bar,
            text="⯆ EXIF Data",
            bg="#2f2f2f",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            command=self.toggle
        )
        self.toggle_btn.pack(pady=2)

        # Scrollable Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree_scroll = tk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("tag", "value"),
            show="headings",
            yscrollcommand=self.tree_scroll.set
        )
        self.tree.heading("tag", text="Tag")
        self.tree.heading("value", text="Value")
        self.tree.column("tag", width=150, anchor="w")
        self.tree.column("value", width=250, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree_scroll.config(command=self.tree.yview)

        # Style
        style = ttk.Style()
        style.configure("Treeview", background="#141414", foreground="white", fieldbackground="#141414")
        style.configure("Treeview.Heading", background="#2f2f2f", foreground="white", font=("Arial", 10, "bold"))

        # Bottom resize grip
        self.grip = tk.Frame(self, cursor="sb_v_double_arrow", bg="#454545", height=GRIP_HEIGHT)
        self.grip.pack(fill="x", side="bottom")
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._do_resize)

    # ----------------- Toggle -----------------
    def toggle(self):
        if self.collapsed:
            # Expand
            self.configure(height=self.expanded_height)
            self.tree_frame.pack(fill="both", expand=True)
            self.grip.pack(fill="x", side="bottom")
            self.toggle_btn.config(text="⯆ EXIF Data")
            self.collapsed = False
        else:
            # Collapse
            self.expanded_height = self.winfo_height()
            self.tree_frame.pack_forget()
            self.grip.pack_forget()
            self.configure(height=MIN_COLLAPSED_HEIGHT)
            self.toggle_btn.config(text="⯈ EXIF Data")
            self.collapsed = True

    # ----------------- Resize -----------------
    def _start_resize(self, event):
        self._start_y = self.grip.winfo_rooty()
        self._start_height = self.winfo_height()
        if self.collapsed:
            self.toggle() 

    def _do_resize(self, event):
        mouse_y = self.grip.winfo_pointery()
        delta = mouse_y - self._start_y
        new_height = max(MIN_COLLAPSED_HEIGHT, self._start_height + delta)
        self.expanded_height = new_height
        self.configure(height=new_height)

    # ----------------- Update EXIF -----------------
    def update_exif(self, photo_id):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not photo_id:
            return

        exif = self.db.get_exif(photo_id)
        if not exif:
            return

        for key, value in exif.items():
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(v) for v in value)
            self.tree.insert("", "end", values=(key, str(value)))
