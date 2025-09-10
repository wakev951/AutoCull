# filmstrip_viewer.py
import tkinter as tk
from PIL import Image, ImageTk

HIGHLIGHT_BORDER = 3

# TODO: simplify buy using more of photo viewer

class FilmstripViewer(tk.Frame):
    """
    Horizontal filmstrip panel to show thumbnails of all photos currently
    displayed in the PhotoViewer.
    Highlights the selected photo and auto-scrolls.
    """
    def __init__(self, parent, photo_viewer, exif_viewer=None, score_viewer=None, duplicates_viewer=None,
                 thumb_size=80, padding=5, **kwargs):
        frame_kwargs = {k: v for k, v in kwargs.items() if k in ("bg", "height", "width", "relief", "bd")}
    
        super().__init__(parent, **frame_kwargs) 

        self.photo_viewer = photo_viewer
        self.exif_viewer = exif_viewer
        self.score_viewer = score_viewer
        self.duplicates_viewer = duplicates_viewer
        self.thumb_size = thumb_size
        self.padding = padding
        self.thumbs = []
        self.labels = []
        self.selected_id = None

        # Canvas for horizontal scrolling
        self.canvas = tk.Canvas(self, height=self.thumb_size + 2*self.padding, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="top", fill="x", expand=True)

        # Inner frame inside canvas
        self.inner_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        self.window_id = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        # Update scrollregion
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Initialize thumbnails
        self.refresh_thumbs()

    # ---------------- Thumbnails ----------------
    def refresh_thumbs(self):
        # Clear previous
        for lbl in self.labels:
            lbl.destroy()
        self.labels = []
        self.thumbs = []

        for lbl in self.photo_viewer.photo_labels:
            try:
                img_path = getattr(lbl, "photo_path", None)
                photo_id = getattr(lbl, "photo_id", None)
                if not img_path or photo_id is None:
                    continue
                img = Image.open(img_path)
                img.thumbnail((self.thumb_size, self.thumb_size))
                tk_img = ImageTk.PhotoImage(img)
                self.thumbs.append(tk_img)

                thumb_lbl = tk.Label(
                    self.inner_frame, image=tk_img, bg="#1a1a1a", cursor="hand2", bd=0, relief="solid"
                )
                thumb_lbl.image = tk_img
                thumb_lbl.photo_id = photo_id
                thumb_lbl.bind("<Button-1>", lambda e, pid=photo_id: self.on_thumb_click(pid))
                thumb_lbl.pack(side="left", padx=self.padding, pady=self.padding)
                self.labels.append(thumb_lbl)
            except Exception as e:
                print(f"Failed to create filmstrip thumbnail: {e}")


        self.update_highlight()

    # ---------------- Selection ----------------
    def update_highlight(self, selected_photo_id=None):
        """Highlight the selected thumbnail and auto-scroll."""
        if selected_photo_id is not None:
            self.selected_id = selected_photo_id

        for lbl in self.labels:
            if lbl.photo_id == self.selected_id:
                lbl.config(
                    bd=HIGHLIGHT_BORDER,
                    relief="solid",
                    highlightbackground="yellow",
                    highlightcolor="yellow"
                )
                self._scroll_to_label(lbl)
            else:
                lbl.config(
                    bd=0,
                    relief="flat",
                    highlightbackground=lbl["bg"],  # reset background
                    highlightcolor=lbl["bg"]
                )

    def on_thumb_click(self, photo_id):
        """Called when a thumbnail is clicked."""
        self.selected_id = photo_id
        self.update_highlight()

        # Update main PhotoViewer
        if hasattr(self.photo_viewer, "on_photo_click"):
            self.photo_viewer.on_photo_click(photo_id)

        # Update EXIF panel
        if self.exif_viewer:
            self.exif_viewer.update_exif(photo_id)

        # Update Score panel
        if self.score_viewer:
            self.score_viewer.update_scores(photo_id)

        # Update Duplicates panel
        if self.duplicates_viewer:
            self.duplicates_viewer.update_duplicates(photo_id)

    # ---------------- Auto-scroll ----------------
    def _scroll_to_label(self, lbl):
        """Scroll the canvas so that lbl is roughly centered."""
        canvas_width = self.canvas.winfo_width()
        lbl_x = lbl.winfo_x() + lbl.winfo_width() // 2
        scroll_x = max(0, lbl_x - canvas_width // 2)
        self.canvas.xview_moveto(scroll_x / max(1, self.canvas.bbox("all")[2]))
