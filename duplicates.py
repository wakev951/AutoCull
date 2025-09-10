# duplicates.py
DEBUG = False  # Set False to suppress debug output

from PIL import Image
import imagehash
import numpy as np
from sklearn.cluster import DBSCAN
from db import Database

class NearDuplicateDetector:
    """
    Detects near-duplicate photos using perceptual hashing and DBSCAN clustering.
    Works efficiently for large photo collections.
    """

    def __init__(self, db: Database, threshold=5):
        """
        :param db: Database instance
        :param threshold: maximum Hamming distance to consider photos as duplicates
        """
        self.db = db
        self.threshold = threshold

    def _log(self, msg):
        if DEBUG:
            print(msg)

    def find_duplicates_batch(self, photo_list):
        """
        Run near-duplicate detection on a batch of photos.

        :param photo_list: list of dicts, each with 'id' and 'file_path'
        """
        self._log(f"[DEBUG] Starting batch duplicate detection for {len(photo_list)} photos.")
        if not photo_list:
            return

        hashes = []
        photo_ids = []

        for photo in photo_list:
            photo_id = photo["id"]
            path = photo["file_path"]
            try:
                img = Image.open(path)
                phash = imagehash.phash(img)
                hashes.append(phash.hash.flatten().astype(int))
                photo_ids.append(photo_id)
                self._log(f"[DEBUG] photo_id={photo_id}, hash={phash}")
            except Exception as e:
                self._log(f"[ERROR] Failed to hash {path}: {e}")

        if not hashes:
            self._log("[DEBUG] No valid hashes to process.")
            return

        hashes_np = np.array(hashes)

        clustering = DBSCAN(
            eps=self.threshold / 64,
            min_samples=2,
            metric="hamming"
        )
        labels = clustering.fit_predict(hashes_np)
        self._log(f"[DEBUG] Clustering labels: {labels}")

        cluster_map = {}

        for photo_id, label in zip(photo_ids, labels):
            try:
                if label == -1:
                    # Noise: create single-photo group
                    group_id = self.db.add_near_duplicate_group(method="phash")
                    self.db.assign_photo_to_near_duplicate_group(group_id, photo_id)
                    self._log(f"[DEBUG] photo_id={photo_id} -> new group_id={group_id} (noise)")
                else:
                    # Clustered: reuse group_id per cluster
                    if label not in cluster_map:
                        group_id = self.db.add_near_duplicate_group(method="phash")
                        cluster_map[label] = group_id
                        self._log(f"[DEBUG] Created cluster group_id={group_id} for label={label}")
                    else:
                        group_id = cluster_map[label]

                    self.db.assign_photo_to_near_duplicate_group(group_id, photo_id)
                    self._log(f"[DEBUG] photo_id={photo_id} -> group_id={group_id}")
            except Exception as e:
                self._log(f"[ERROR] Failed to assign photo_id={photo_id} to group: {e}")
