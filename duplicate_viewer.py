# duplicate_viewer.py
import tkinter as tk
from tkinter import ttk
from db import Database

MIN_COLLAPSED_HEIGHT = 30
DEFAULT_HEIGHT = 400
GRIP_HEIGHT = 6

class DuplicateViewer(tk.Frame):
    """
    Right-hand panel to display near-duplicate groups of a selected photo.
    Shows the selected photo ID at the top.
    Supports vertical collapse/expand and manual resizing via a grip.
    """
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.collapsed = False
        self.expanded_height = DEFAULT_HEIGHT
        self.selected_photo_id = None

        self.pack_propagate(False)
        self.configure(height=self.expanded_height)

        # Top bar with toggle and selected photo label
        self.top_bar = tk.Frame(self, bg="#2f2f2f")
        self.top_bar.pack(fill="x")

        self.toggle_btn = tk.Button(
            self.top_bar,
            text="⯆ Duplicates",
            bg="#2f2f2f",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            command=self.toggle
        )
        self.toggle_btn.pack(side="left", padx=5, pady=2)

        self.selected_label = tk.Label(
            self.top_bar,
            text="Selected Photo ID: None",
            bg="#2f2f2f",
            fg="white",
            font=("Arial", 10, "italic")
        )
        self.selected_label.pack(side="left", padx=10)

        # Treeview
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree_scroll = tk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("group_id", "photo_id", "file_name"),
            show="headings",
            yscrollcommand=self.tree_scroll.set
        )
        self.tree.heading("group_id", text="Group ID")
        self.tree.heading("photo_id", text="Photo ID")
        self.tree.heading("file_name", text="File Name")
        self.tree.column("group_id", width=80, anchor="center")
        self.tree.column("photo_id", width=80, anchor="center")
        self.tree.column("file_name", width=250, anchor="w")
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
            self.configure(height=self.expanded_height)
            self.tree_frame.pack(fill="both", expand=True)
            self.grip.pack(fill="x", side="bottom")
            self.toggle_btn.config(text="⯆ Duplicates")
            self.collapsed = False
        else:
            self.expanded_height = self.winfo_height()
            self.tree_frame.pack_forget()
            self.grip.pack_forget()
            self.configure(height=MIN_COLLAPSED_HEIGHT)
            self.toggle_btn.config(text="⯈ Duplicates")
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

    # ----------------- Update duplicates -----------------
    def update_duplicates(self, photo_id):
        """
        Populate treeview with all photos in the same near-duplicate groups as photo_id.
        Shows the selected photo ID at the top.
        """
        self.selected_photo_id = photo_id
        self.selected_label.config(text=f"Selected Photo ID: {photo_id}")

        # Clear previous
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not photo_id:
            return

        # Fetch all groups the photo belongs to
        query_groups = """
            SELECT group_id FROM near_duplicate_photos
            WHERE photo_id = %s
        """
        groups = self.db.fetch(query_groups, (photo_id,))
        if not groups:
            return

        for g in groups:
            group_id = g["group_id"]
            # Fetch all photos in this group
            photos_in_group = self.db.fetch("""
                SELECT p.id AS photo_id, p.file_name
                FROM photos p
                JOIN near_duplicate_photos ndp ON p.id = ndp.photo_id
                WHERE ndp.group_id = %s
            """, (group_id,))
            for p in photos_in_group:
                self.tree.insert("", "end", values=(group_id, p["photo_id"], p["file_name"]))
