from base_sidebar_viewer import BaseSidebarViewer

class ExifViewer(BaseSidebarViewer):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, db, title="EXIF Data", default_height=400, **kwargs)

    def setup_columns(self, tree):
        tree["columns"] = ("tag", "value")
        tree.heading("tag", text="Tag")
        tree.heading("value", text="Value")
        tree.column("tag", width=150, anchor="w")
        tree.column("value", width=250, anchor="w")

    def update_content(self, photo_id):
        self.clear_tree()
        if not photo_id:
            return
        exif = self.db.get_exif(photo_id)
        if not exif:
            return
        for key, value in exif.items():
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(v) for v in value)
            self.tree.insert("", "end", values=(key, str(value)))
