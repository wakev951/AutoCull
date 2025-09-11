# photo_viewer.py
import tkinter as tk
from PIL import Image, ImageTk
from base_viewer import BaseThumbnailViewer

class PhotoViewer(BaseThumbnailViewer):
    """Main center grid of photos with scrolling + keyboard navigation."""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, db=db, thumb_size=120, padding=10, **kwargs)
        self.selected_idx = None
        self.canvas = tk.Canvas(self, bg="#141414")
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="#141414")
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Update scroll region
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self._reflow_grid())

        self.thumb_size = 120
        self.padding = 10
        self.columns = 1
        self.refresh_photos()

    def refresh_photos(self, collection_id=None):
        self.clear_thumbnails()
        self.photos = self.db.get_photos(collection_id)

        for photo in self.photos:
            tk_img = self.load_thumbnail(photo["file_path"])
            if not tk_img:
                continue
            self.thumbs.append(tk_img)
            lbl = tk.Label(
                self.inner_frame, image=tk_img, bg="#141414", cursor="hand2",
                bd=2, relief="flat", highlightthickness=0
            )
            lbl.image = tk_img
            lbl.photo_id = photo["id"]
            lbl.photo_path = photo["file_path"]
            lbl.bind("<Button-1>", lambda e, pid=photo["id"]: self._on_photo_click(pid))
            self.labels.append(lbl)

        self._reflow_grid()

    def _on_photo_click(self, photo_id):
        idx = next((i for i, lbl in enumerate(self.labels) if lbl.photo_id == photo_id), None)
        if idx is not None:
            self._select_idx(idx)
        self.select_photo(photo_id)

    def _select_idx(self, idx):
        if self.selected_idx is not None and 0 <= self.selected_idx < len(self.labels):
            self.labels[self.selected_idx].config(highlightthickness=0)
        self.selected_idx = idx
        self.labels[idx].config(highlightthickness=3)

    def _reflow_grid(self):
        if not self.labels:
            return
        width = self.canvas.winfo_width()
        if width < 50:
            self.after(50, self._reflow_grid)
            return
        self.columns = max(1, width // (self.thumb_size + self.padding))
        for lbl in self.labels:
            lbl.grid_forget()
        for idx, lbl in enumerate(self.labels):
            row, col = divmod(idx, self.columns)
            lbl.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
        self.canvas.itemconfig(self.window_id, width=width)
