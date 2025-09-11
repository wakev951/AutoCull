from base_sidebar_viewer import BaseSidebarViewer

class DuplicateViewer(BaseSidebarViewer):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, db, title="Duplicates", default_height=400, **kwargs)
        self.selected_photo_id = None

    def setup_columns(self, tree):
        tree["columns"] = ("group_id", "photo_id", "file_name")
        tree.heading("group_id", text="Group ID")
        tree.heading("photo_id", text="Photo ID")
        tree.heading("file_name", text="File Name")
        tree.column("group_id", width=80, anchor="center")
        tree.column("photo_id", width=80, anchor="center")
        tree.column("file_name", width=250, anchor="w")

    def update_content(self, photo_id):
        self.clear_tree()
        self.selected_photo_id = photo_id
        if not photo_id:
            return
        groups = self.db.get_groups_for_photo(photo_id)
        if not groups:
            return
        for g in groups:
            group_id = g["group_id"]
            for p in self.db.get_photos_in_group(group_id):
                self.tree.insert("", "end", values=(group_id, p["photo_id"], p["file_name"]))
