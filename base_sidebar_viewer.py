import tkinter as tk
from tkinter import ttk
from db import Database

MIN_COLLAPSED_HEIGHT = 30
DEFAULT_HEIGHT = 300
GRIP_HEIGHT = 6

class BaseSidebarViewer(tk.Frame):
    """
    Base class for right-hand sidebar viewers.
    Provides:
      - Collapsible header bar
      - Scrollable Treeview
      - Resize grip
    Subclasses should:
      - Define self.title
      - Override setup_columns(tree)
      - Override update_content(photo_id)
    """

    def __init__(self, parent, db: Database, title="Viewer", default_height=DEFAULT_HEIGHT, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.title = title
        self.collapsed = False
        self.expanded_height = default_height

        self.pack_propagate(False)
        self.configure(height=self.expanded_height)

        # ---------- Header ----------
        self.top_bar = tk.Frame(self, bg="#2f2f2f")
        self.top_bar.pack(fill="x")

        self.toggle_btn = tk.Button(
            self.top_bar,
            text=f"⯆ {self.title}",
            bg="#2f2f2f",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            command=self.toggle
        )
        self.toggle_btn.pack(pady=2, padx=5, anchor="w")

        # ---------- Treeview ----------
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree_scroll = tk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.tree_frame,
            show="headings",
            yscrollcommand=self.tree_scroll.set
        )
        self.setup_columns(self.tree)
        self.tree.pack(fill="both", expand=True)
        self.tree_scroll.config(command=self.tree.yview)

        # ---------- Style ----------
        style = ttk.Style()
        style.configure("Treeview", background="#141414", foreground="white", fieldbackground="#141414")
        style.configure("Treeview.Heading", background="#2f2f2f", foreground="white", font=("Arial", 10, "bold"))

        # ---------- Resize Grip ----------
        self.grip = tk.Frame(self, cursor="sb_v_double_arrow", bg="#454545", height=GRIP_HEIGHT)
        self.grip.pack(fill="x", side="bottom")
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._do_resize)

    # ----------------- Must Override -----------------
    def setup_columns(self, tree: ttk.Treeview):
        """Define columns in subclass."""
        raise NotImplementedError

    def update_content(self, photo_id):
        """Populate tree in subclass."""
        raise NotImplementedError

    # ----------------- Toggle -----------------
    def toggle(self):
        if self.collapsed:
            self.configure(height=self.expanded_height)
            self.tree_frame.pack(fill="both", expand=True)
            self.grip.pack(fill="x", side="bottom")
            self.toggle_btn.config(text=f"⯆ {self.title}")
            self.collapsed = False
        else:
            self.expanded_height = self.winfo_height()
            self.tree_frame.pack_forget()
            self.grip.pack_forget()
            self.configure(height=MIN_COLLAPSED_HEIGHT)
            self.toggle_btn.config(text=f"⯈ {self.title}")
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

    # ----------------- Helpers -----------------
    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
