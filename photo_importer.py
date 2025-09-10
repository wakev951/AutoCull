# photo_importer.py
from pathlib import Path
from db import Database
from duplicates import NearDuplicateDetector
from photo_scorer import PhotoScorer
from exif_reader import ExifReader

class PhotoImporter:
    SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".tif", ".tiff")

    def __init__(self, db: Database, near_dup_threshold=5):
        self.db = db
        self.duplicates = NearDuplicateDetector(db, threshold=near_dup_threshold)
        self.scorer = PhotoScorer(db)

    def import_files(self, file_paths: list[str], collection_id: int, default_styles=None):
        imported_count = 0
        for file_path in file_paths:
            try:
                self._import_file(Path(file_path), collection_id, default_styles)
                imported_count += 1
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
        print(f"Imported {imported_count} photos")
        return imported_count

    def import_folder(self, folder_path: str, collection_id: int, default_styles=None):
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Folder {folder_path} does not exist or is not a directory")
        files = [str(f) for f in folder.glob("*") if f.suffix.lower() in self.SUPPORTED_EXTENSIONS]
        return self.import_files(files, collection_id, default_styles)

    def _import_file(self, file: Path, collection_id: int, default_styles=None):
        if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file.suffix}")

        # --- Extract EXIF using the dedicated reader ---
        exif = ExifReader.read_exif(file)

        photo_id = self.db.add_photo(
            collection_id=collection_id,
            file_path=str(file),
            file_name=file.name
        )

        # Store EXIF in DB
        for key, value in exif.items():
            self.db.add_exif(photo_id, key, str(value))

        # Assign default styles
        if default_styles:
            for style_name in default_styles:
                style_id = self.db.add_style(style_name)
                if style_id:
                    self.db.assign_style(photo_id, style_id)

        # Score image
        try:
            scores = self.scorer.score_and_store(photo_id, str(file))
            print(f"Scores for {file.name}: {scores}")
        except Exception as e:
            print(f"Failed to score {file.name}: {e}")

        print(f"Imported {file}")
        return photo_id
