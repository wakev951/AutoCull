# filmstrip_viewer.py
import tkinter as tk
from base_viewer import BaseThumbnailViewer

HIGHLIGHT_BORDER = 3

class FilmstripViewer(BaseThumbnailViewer):
    """Horizontal scrolling strip of thumbnails."""

    def __init__(self, parent, photo_viewer, exif_viewer=None, score_viewer=None, duplicates_viewer=None, **kwargs):
        super().__init__(parent, thumb_size=80, padding=5, **kwargs)
        self.photo_viewer = photo_viewer
        self.exif_viewer = exif_viewer
        self.score_viewer = score_viewer
        self.duplicates_viewer = duplicates_viewer

        self.canvas = tk.Canvas(self, height=self.thumb_size + 2*self.padding, bg="#1a1a1a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="top", fill="x", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.refresh_thumbs()

    def refresh_thumbs(self):
        self.clear_thumbnails()
        for lbl in self.photo_viewer.labels:
            img_path = getattr(lbl, "photo_path", None)
            photo_id = getattr(lbl, "photo_id", None)
            if not img_path or not photo_id:
                continue
            tk_img = self.load_thumbnail(img_path)
            if not tk_img:
                continue
            self.thumbs.append(tk_img)
            thumb_lbl = tk.Label(
                self.inner_frame, image=tk_img, bg="#1a1a1a", cursor="hand2", bd=0, relief="solid"
            )
            thumb_lbl.image = tk_img
            thumb_lbl.photo_id = photo_id
            thumb_lbl.bind("<Button-1>", lambda e, pid=photo_id: self.on_thumb_click(pid))
            thumb_lbl.pack(side="left", padx=self.padding, pady=self.padding)
            self.labels.append(thumb_lbl)
        self.update_highlight()

    def update_highlight(self, selected_photo_id=None):
        if selected_photo_id:
            self.selected_id = selected_photo_id
        for lbl in self.labels:
            if lbl.photo_id == self.selected_id:
                lbl.config(bd=HIGHLIGHT_BORDER, relief="solid", highlightbackground="yellow")
                self._scroll_to_label(lbl)
            else:
                lbl.config(bd=0, relief="flat", highlightbackground=lbl["bg"])

    def on_thumb_click(self, photo_id):
        self.select_photo(photo_id)
        if hasattr(self.photo_viewer, "_on_photo_click"):
            self.photo_viewer._on_photo_click(photo_id)

    def _scroll_to_label(self, lbl):
        canvas_width = self.canvas.winfo_width()
        lbl_x = lbl.winfo_x() + lbl.winfo_width() // 2
        scroll_x = max(0, lbl_x - canvas_width // 2)
        total_width = self.canvas.bbox("all")[2]
        self.canvas.xview_moveto(scroll_x / max(1, total_width))
