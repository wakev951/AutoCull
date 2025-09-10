# AutoCull

Prototype for automatic photo culling software. 

# Requirements
See `requirements.txt` for required dependencies. 

Run `pip install -r requirements.txt` to install all

---

duplicates.py broken - missing methods. Add following code for test:
    def process_photo(self, photo_id, file_path):
        """
        Process a single photo for near-duplicate detection.

        :param photo_id: ID of the photo in the database
        :param file_path: Path to the photo file
        """
        self._log(f"[DEBUG] Processing single photo_id={photo_id} for duplicates.")
        self.find_duplicates_batch([{"id": photo_id, "file_path": file_path}])

