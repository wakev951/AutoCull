import tkinter as tk
from db import Database
from PIL import Image, ImageTk

class PhotoViewer(tk.Frame):
    """
    Center photo viewing area with responsive grid layout, clickable thumbnails,
    white border highlight, and keyboard navigation.
    """
    def __init__(self, parent, db: Database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.photos = []
        self.photo_labels = []
        self.selected_idx = None  # track index of selected photo

        # Canvas + vertical scrollbar
        self.canvas = tk.Canvas(self, bg="#141414")
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Inner frame inside canvas
        self.inner_frame = tk.Frame(self.canvas, bg="#141414")
        self.window_id = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        # Update scroll region when inner frame changes
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self._reflow_grid())

        # Scroll wheel only on canvas
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        # Keyboard navigation
        self.bind_all("<Left>", lambda e: self._move_selection(-1))
        self.bind_all("<Right>", lambda e: self._move_selection(1))
        self.bind_all("<Up>", lambda e: self._move_selection(-1, vertical=True))
        self.bind_all("<Down>", lambda e: self._move_selection(1, vertical=True))

        self.thumb_size = 120
        self.padding = 10
        self.columns = 1  # updated dynamically

        self.refresh_photos()

    # ---------- Photo Handling ----------
    def refresh_photos(self, collection_id=None):
        # Clear previous labels
        for lbl in self.photo_labels:
            lbl.destroy()
        self.photo_labels = []
        self.selected_idx = None

        self.photos = self.db.get_photos(collection_id)

        # Create labels
        for photo in self.photos:
            try:
                img = Image.open(photo["file_path"])
                img.thumbnail((self.thumb_size, self.thumb_size))
                tk_img = ImageTk.PhotoImage(img)

                lbl = tk.Label(
                    self.inner_frame,
                    image=tk_img,
                    bg="#141414",
                    cursor="hand2",
                    bd=2,
                    relief="flat",
                    highlightthickness=0,
                    highlightbackground="white"
                )
                lbl.image = tk_img  # keep reference
                lbl.photo_id = photo["id"]  # store photo ID
                lbl.bind("<Button-1>", lambda e, idx=len(self.photo_labels), pid=photo["id"]: self._on_photo_click(idx, pid))

                lbl.photo_path = photo["file_path"]  # store path for filmstrip
                self.photo_labels.append(lbl)
            except Exception as e:
                print(f"Failed to load photo {photo['file_path']}: {e}")

        self._reflow_grid()

    def _on_photo_click(self, idx, photo_id):
        self._select_photo(idx)
        if hasattr(self.master, "exif_viewer") and self.master.exif_viewer:
            self.master.exif_viewer.update_exif(photo_id)

        if hasattr(self.master, "score_viewer") and self.master.score_viewer:
            self.master.score_viewer.update_scores(photo_id)

        if hasattr(self.master, "filmstrip") and self.master.filmstrip:
            self.master.filmstrip.update_highlight(photo_id)

        if hasattr(self.master, "duplicate_viewer") and self.master.duplicate_viewer:
            self.master.duplicate_viewer.update_duplicates(photo_id)    

    def _select_photo(self, idx):
        if self.selected_idx is not None:
            prev_lbl = self.photo_labels[self.selected_idx]
            prev_lbl.config(highlightthickness=0)
        self.selected_idx = idx
        selected_lbl = self.photo_labels[idx]
        selected_lbl.config(highlightthickness=3)

        # show selected photo on canvas
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(max(0, selected_lbl.winfo_y() / self.inner_frame.winfo_height()))

    # ---------- Grid Layout ----------
    def _reflow_grid(self):
        if not self.photo_labels:
            return

        width = self.canvas.winfo_width()
        if width < 50:
            self.after(50, self._reflow_grid)
            return

        self.columns = max(1, width // (self.thumb_size + self.padding))
        for lbl in self.photo_labels:
            lbl.grid_forget()

        for idx, lbl in enumerate(self.photo_labels):
            row = idx // self.columns
            col = idx % self.columns
            lbl.grid(row=row, column=col, padx=5, pady=5, sticky="nw")

        self.canvas.itemconfig(self.window_id, width=width)

    # ---------- Scroll Wheel ----------
    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # ---------- Keyboard Navigation ----------
    def _move_selection(self, step, vertical=False):
        if not self.photo_labels:
            return
        if self.selected_idx is None:
            idx = 0
        else:
            idx = self.selected_idx
            if vertical:
                idx += step * self.columns
            else:
                idx += step
        idx = max(0, min(len(self.photo_labels)-1, idx))
        self._select_photo(idx)
        #update EXIF panel
        photo_id = self.photo_labels[idx].photo_id
        if hasattr(self.master, "exif_viewer") and self.master.exif_viewer:
            self.master.exif_viewer.update_exif(photo_id)

