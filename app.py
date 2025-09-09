# app.py
import tkinter as tk
from PIL import Image, ImageTk  # (kept for when we wire images)

MIN_COLLAPSED = 30
MAX_WIDTH = 500
DEFAULT_WIDTH = 220
GRIP_WIDTH = 6  # draggable area width


class PhotoCullingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Culling Software")
        self.geometry("1200x800")
        self.configure(bg="#1e1e1e")

        # Setup native menubar
        self.setup_menubar()

        # ---- Center viewer fills the window; sidebars overlay on top (independent) ----
        self.center_frame = tk.Frame(self, bg="#141414")
        self.center_frame.pack(fill="both", expand=True)

        # State
        self.left_width = DEFAULT_WIDTH
        self.right_width = DEFAULT_WIDTH
        self.left_collapsed = False
        self.right_collapsed = False

        # ---- Left Sidebar (overlay) ----
        self.left_sidebar = tk.Frame(self, bg="#2f2f2f")
        self.left_toolbar = tk.Frame(self.left_sidebar, bg="#2f2f2f")
        self.left_toolbar.pack(fill="x")

        self.left_toggle_btn = tk.Button(
            self.left_toolbar, text="⮜", width=2, command=self.toggle_left
        )
        self.left_toggle_btn.pack(side="right", padx=4, pady=4)

        # Left resize grip (on the right edge of left sidebar)
        self.left_grip = tk.Frame(self.left_sidebar, cursor="sb_h_double_arrow", bg="#454545", width=GRIP_WIDTH)
        self.left_grip.pack(side="right", fill="y")
        self.left_grip.bind("<ButtonPress-1>", self._start_left_resize)
        self.left_grip.bind("<B1-Motion>", self._do_left_resize)

        # ---- Right Sidebar (overlay) ----
        self.right_sidebar = tk.Frame(self, bg="#2f2f2f")
        self.right_toolbar = tk.Frame(self.right_sidebar, bg="#2f2f2f")
        self.right_toolbar.pack(fill="x")

        self.right_toggle_btn = tk.Button(
            self.right_toolbar, text="⮞", width=2, command=self.toggle_right
        )
        self.right_toggle_btn.pack(side="left", padx=4, pady=4)

        # Right resize grip (on the left edge of right sidebar)
        self.right_grip = tk.Frame(self.right_sidebar, cursor="sb_h_double_arrow", bg="#454545", width=GRIP_WIDTH)
        self.right_grip.pack(side="left", fill="y")
        self.right_grip.bind("<ButtonPress-1>", self._start_right_resize)
        self.right_grip.bind("<B1-Motion>", self._do_right_resize)

        # ---- Center placeholder ----
        self.photo_label = tk.Label(
            self.center_frame, text="Photo Viewer Area", fg="#f0f0f0", bg="#141414", font=("Arial", 20)
        )
        self.photo_label.pack(expand=True)

        # Keep layout updated on window resize
        self.bind("<Configure>", lambda e: self.update_layout())

        # Initial layout
        self.update_layout()

    # ---------- Native Menubar ----------
    def setup_menubar(self):
        menubar = tk.Menu(self)

        # --- File menu ---
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Collection", command=lambda: print("New Collection"))
        file_menu.add_command(label="Open Collection...", command=lambda: print("Open"))
        file_menu.add_separator()
        file_menu.add_command(label="Import Photos", command=lambda: print("Import"))
        file_menu.add_command(label="Export Selection", command=lambda: print("Export"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # --- Edit menu ---
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: print("Undo"))
        edit_menu.add_command(label="Redo", command=lambda: print("Redo"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: print("Cut"))
        edit_menu.add_command(label="Copy", command=lambda: print("Copy"))
        edit_menu.add_command(label="Paste", command=lambda: print("Paste"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=lambda: print("Preferences"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # --- View menu ---
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=lambda: print("Zoom In"))
        view_menu.add_command(label="Zoom Out", command=lambda: print("Zoom Out"))
        view_menu.add_checkbutton(label="Fullscreen", command=lambda: print("Fullscreen"))
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Left Panel", command=lambda: print("Toggle Left Panel"))
        view_menu.add_checkbutton(label="Show Right Panel", command=lambda: print("Toggle Right Panel"))
        menubar.add_cascade(label="View", menu=view_menu)

        # --- Window menu ---
        window_menu = tk.Menu(menubar, tearoff=0)
        window_menu.add_command(label="Minimize", command=lambda: print("Minimize"))
        window_menu.add_command(label="Close", command=lambda: print("Close"))
        window_menu.add_separator()
        window_menu.add_command(label="Switch Window...", command=lambda: print("Switch Window"))
        menubar.add_cascade(label="Window", menu=window_menu)

        # --- Help menu ---
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=lambda: print("Docs"))
        help_menu.add_command(label="Check for Updates", command=lambda: print("Updates"))
        help_menu.add_separator()
        help_menu.add_command(label="About", command=lambda: print("About"))
        menubar.add_cascade(label="Help", menu=help_menu)

        # Attach menubar to window
        self.config(menu=menubar)

    # ---------- Layout ----------
    def update_layout(self):
        w = self.winfo_width()
        h = self.winfo_height()

        # Left sidebar placement (overlay)
        lw = MIN_COLLAPSED if self.left_collapsed else self.left_width
        self.left_sidebar.place(x=0, y=0, width=lw, height=h)
        self.left_sidebar.lift()

        # Right sidebar placement (overlay)
        rw = MIN_COLLAPSED if self.right_collapsed else self.right_width
        self.right_sidebar.place(x=max(0, w - rw), y=0, width=rw, height=h)
        self.right_sidebar.lift()

        # Update toggle icon directions
        self.left_toggle_btn.config(text="⮞" if self.left_collapsed else "⮜")
        self.right_toggle_btn.config(text="⮜" if self.right_collapsed else "⮞")

    # ---------- Collapse / Expand ----------
    def toggle_left(self):
        self.left_collapsed = not self.left_collapsed
        self.update_layout()

    def toggle_right(self):
        self.right_collapsed = not self.right_collapsed
        self.update_layout()

    # ---------- Resizing (independent) ----------
    def _start_left_resize(self, event):
        # record initial width and mouse x
        self._left_start_x = self.left_grip.winfo_rootx()
        self._left_start_width = self.left_width

    def _do_left_resize(self, event):
        if self.left_collapsed:
            # expand from collapsed when dragged
            self.left_collapsed = False
        # delta is how far mouse moved relative to grip origin
        mouse_x = self.left_grip.winfo_pointerx()
        delta = mouse_x - self._left_start_x
        new_w = max(MIN_COLLAPSED, min(MAX_WIDTH, self._left_start_width + delta))
        self.left_width = new_w
        self.update_layout()

    def _start_right_resize(self, event):
        self._right_start_x = self.right_grip.winfo_rootx()
        self._right_start_width = self.right_width

    def _do_right_resize(self, event):
        if self.right_collapsed:
            self.right_collapsed = False
        mouse_x = self.right_grip.winfo_pointerx()
        delta = self._right_start_x - mouse_x  # moving left increases width
        new_w = max(MIN_COLLAPSED, min(MAX_WIDTH, self._right_start_width + delta))
        self.right_width = new_w
        self.update_layout()


if __name__ == "__main__":
    app = PhotoCullingApp()
    app.mainloop()
