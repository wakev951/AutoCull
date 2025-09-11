# db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()  # loads DB credentials from .env


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "autocull_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "admin"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        self.conn.autocommit = True

    # ----------------- Helper Methods -----------------
    def fetch(self, query, params=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def execute(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params or ())
            return True

    # ----------------- Schema -----------------
    def create_schema(self, schema_file="schema.sql"):
        """Run schema.sql to create tables."""
        with open(schema_file, "r") as f:
            sql = f.read()
        self.execute(sql)
        print("Database schema created.")

    # ----------------- Collections -----------------
    def add_collection(self, name: str):
        query = "INSERT INTO collections (name) VALUES (%s) RETURNING id"
        return self.fetch(query, (name,))[0]["id"]

    def get_collections(self):
        return self.fetch("SELECT * FROM collections ORDER BY created_at DESC")

    # ----------------- Photos -----------------
    def add_photo(self, collection_id: int, file_path: str, file_name: str, status="undecided"):
        query = """
        INSERT INTO photos (collection_id, file_path, file_name, status)
        VALUES (%s,%s,%s,%s) RETURNING id
        """
        return self.fetch(query, (collection_id, file_path, file_name, status))[0]["id"]

    def get_photos(self, collection_id=None):
        query = "SELECT * FROM photos"
        if collection_id:
            query += " WHERE collection_id=%s"
            return self.fetch(query, (collection_id,))
        return self.fetch(query)
    
    def get_all_photos(self):
        return self.fetch("SELECT * FROM photos")

    # ----------------- EXIF -----------------
    def add_exif(self, photo_id, tag_name, tag_value):
        query = """
        INSERT INTO exif_data (photo_id, tag_name, tag_value)
        VALUES (%s, %s, %s)
        """
        self.execute(query, (photo_id, tag_name, str(tag_value)))

    def get_exif(self, photo_id):
        query = "SELECT tag_name, tag_value FROM exif_data WHERE photo_id=%s"
        results = self.fetch(query, (photo_id,))
        return {row["tag_name"]: row["tag_value"] for row in results} if results else {}


    # ----------------- Scores -----------------
    def add_score(self, photo_id, score_type, value):
        query = "INSERT INTO scores (photo_id, type, value) VALUES (%s,%s,%s)"
        self.execute(query, (photo_id, score_type, value))

    def get_scores(self, photo_id):
        return self.fetch("SELECT * FROM scores WHERE photo_id=%s", (photo_id,))

    # ----------------- Styles -----------------
    def add_style(self, name, description=None):
        query = "INSERT INTO styles (name, description) VALUES (%s,%s) ON CONFLICT (name) DO NOTHING RETURNING id"
        result = self.fetch(query, (name, description))
        return result[0]["id"] if result else None

    def assign_style(self, photo_id, style_id):
        query = "INSERT INTO photo_styles (photo_id, style_id) VALUES (%s,%s) ON CONFLICT DO NOTHING"
        self.execute(query, (photo_id, style_id))

    def get_styles_for_photo(self, photo_id):
        return self.fetch("""
            SELECT s.* FROM styles s
            JOIN photo_styles ps ON s.id = ps.style_id
            WHERE ps.photo_id=%s
        """, (photo_id,))

    # ----------------- Near Duplicates -----------------
    def add_near_duplicate_group(self, method=None):
        """
        Create a new near-duplicate group and return its ID.
        :param method: method used to detect duplicates (e.g., 'phash')
        """
        query = "INSERT INTO near_duplicate_groups (method) VALUES (%s) RETURNING id"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, (method,))
            group_id = cursor.fetchone()[0]
            print(f"[DEBUG] Created near-duplicate group_id={group_id}, method={method}")
            return group_id
        except Exception as e:
            print(f"[ERROR] Failed to create near-duplicate group (method={method}): {e}")
            return None
        finally:
            cursor.close()


    def assign_photo_to_near_duplicate_group(self, group_id, photo_id):
        """
        Assign a photo to an existing near-duplicate group.
        :param group_id: ID of the near-duplicate group
        :param photo_id: ID of the photo
        """
        query = """
            INSERT INTO near_duplicate_photos (group_id, photo_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, (group_id, photo_id))
            print(f"[DEBUG] Assigned photo_id={photo_id} to group_id={group_id}")
        except Exception as e:
            print(f"[ERROR] Failed to assign photo_id={photo_id} to group_id={group_id}: {e}")
        finally:
            cursor.close()


    def get_near_duplicate_groups(self):
        """
        Retrieve all near-duplicate groups with their associated photos.
        :return: List of groups with photo IDs
        """
        query = "SELECT * FROM near_duplicate_groups"
        groups = self.fetch(query)
        for group in groups:
            photos = self.fetch("""
                SELECT p.* FROM photos p
                JOIN near_duplicate_photos ndp ON p.id = ndp.photo_id
                WHERE ndp.group_id=%s
            """, (group["id"],))
            group["photos"] = photos
        return groups
    
    def get_photos_in_near_duplicate_group(self, group_id):
        """
        Retrieve all photos in a specific near-duplicate group.
        :param group_id: ID of the near-duplicate group
        :return: List of photos in the group
        """
        query = """
            SELECT p.* FROM photos p
            JOIN near_duplicate_photos ndp ON p.id = ndp.photo_id
            WHERE ndp.group_id=%s
        """
        return self.fetch(query, (group_id,))
    
    def get_near_duplicate_groups_for_photo(self, photo_id):
        """
        Retrieve the near-duplicate group for a specific photo.
        :param photo_id: ID of the photo
        :return: Group details or None if not found
        """
        query = """
            SELECT g.* FROM near_duplicate_groups g
            JOIN near_duplicate_photos ndp ON g.id = ndp.group_id
            WHERE ndp.photo_id=%s
        """
        groups = self.fetch(query, (photo_id,))
        return groups[0] if groups else None
    
    def get_groups_for_photo(self, photo_id):
        """
        Get all group IDs that a given photo belongs to.
        """
        query = "SELECT group_id FROM near_duplicate_photos WHERE photo_id=%s"
        return self.fetch(query, (photo_id,))

    def get_photos_in_group(self, group_id):
        """
        Get all photos (id, file_name) in a near-duplicate group.
        """
        query = """
            SELECT p.id AS photo_id, p.file_name
            FROM photos p
            JOIN near_duplicate_photos ndp ON p.id = ndp.photo_id
            WHERE ndp.group_id=%s
        """
        return self.fetch(query, (group_id,))
