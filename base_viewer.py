# base_viewer.py
import tkinter as tk
from PIL import Image, ImageTk

class BaseThumbnailViewer(tk.Frame):
    """
    Shared base class for displaying photo thumbnails.
    Handles loading images, keeping references, selection,
    and notifying parent/other viewers.
    """

    def __init__(self, parent, db=None, thumb_size=100, padding=5, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.thumb_size = thumb_size
        self.padding = padding
        self.labels = []     # Tk Labels for thumbnails
        self.thumbs = []     # ImageTk.PhotoImage refs
        self.photos = []     # DB rows or metadata dicts
        self.selected_id = None

    def load_thumbnail(self, file_path):
        """Return ImageTk.PhotoImage thumbnail."""
        try:
            img = Image.open(file_path)
            img.thumbnail((self.thumb_size, self.thumb_size))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Failed to load thumbnail for {file_path}: {e}")
            return None

    def clear_thumbnails(self):
        for lbl in self.labels:
            lbl.destroy()
        self.labels = []
        self.thumbs = []

    def select_photo(self, photo_id):
        """Highlight a selected thumbnail and update linked viewers."""
        self.selected_id = photo_id
        for lbl in self.labels:
            if getattr(lbl, "photo_id", None) == photo_id:
                lbl.config(bd=3, relief="solid", highlightbackground="yellow")
            else:
                lbl.config(bd=0, relief="flat", highlightbackground=lbl["bg"])

        # Notify parent container if available
        self._notify(photo_id)

    def _notify(self, photo_id):
        """Call updates on linked viewers if parent has them."""
        master = self.master
        if hasattr(master, "exif_viewer") and master.exif_viewer:
            master.exif_viewer.update_content(photo_id)
        if hasattr(master, "score_viewer") and master.score_viewer:
            master.score_viewer.update_content(photo_id)
        if hasattr(master, "filmstrip") and master.filmstrip:
            master.filmstrip.update_highlight(photo_id)
        if hasattr(master, "duplicate_viewer") and master.duplicate_viewer:
            master.duplicate_viewer.update_content(photo_id)
