-- schema.sql

-- ----------------- Collections -----------------
CREATE TABLE IF NOT EXISTS collections (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ----------------- Photos -----------------
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    collection_id INT REFERENCES collections(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    imported_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'undecided'
);

-- ----------------- EXIF Data -----------------
CREATE TABLE IF NOT EXISTS exif_data (
    id SERIAL PRIMARY KEY,
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE,
    tag_name TEXT NOT NULL,
    tag_value TEXT
);


-- ----------------- Scores -----------------
CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE,
    type TEXT,
    value REAL
);

-- ----------------- Styles -----------------
CREATE TABLE IF NOT EXISTS styles (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

-- Many-to-many: photo_styles
CREATE TABLE IF NOT EXISTS photo_styles (
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE,
    style_id INT REFERENCES styles(id) ON DELETE CASCADE,
    PRIMARY KEY(photo_id, style_id)
);

-- ----------------- Near Duplicate Groups -----------------
CREATE TABLE IF NOT EXISTS near_duplicate_groups (
    id SERIAL PRIMARY KEY,
    method TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Many-to-many: near_duplicate_photos
CREATE TABLE IF NOT EXISTS near_duplicate_photos (
    group_id INT REFERENCES near_duplicate_groups(id) ON DELETE CASCADE,
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE,
    PRIMARY KEY(group_id, photo_id)
);
