from base_sidebar_viewer import BaseSidebarViewer

class ScoreViewer(BaseSidebarViewer):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, db, title="Photo Scores", default_height=300, **kwargs)

    def setup_columns(self, tree):
        tree["columns"] = ("metric", "value")
        tree.heading("metric", text="Metric")
        tree.heading("value", text="Value")
        tree.column("metric", width=150, anchor="w")
        tree.column("value", width=150, anchor="w")

    def update_content(self, photo_id):
        self.clear_tree()
        if not photo_id:
            return
        scores = self.db.get_scores(photo_id)
        if not scores:
            return
        for score in scores:
            self.tree.insert("", "end", values=(score["type"], str(score["value"])))
