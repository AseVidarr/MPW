PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS main_genres(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE);
CREATE TABLE IF NOT EXISTS subgenres(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE);
CREATE TABLE IF NOT EXISTS genre_relations(main_genre_id INTEGER NOT NULL REFERENCES main_genres(id),subgenre_id INTEGER NOT NULL REFERENCES subgenres(id),PRIMARY KEY(main_genre_id,subgenre_id));
CREATE TABLE IF NOT EXISTS genre_translations(entity_type TEXT NOT NULL CHECK(entity_type IN ('main','sub')),entity_id INTEGER NOT NULL,language_code TEXT NOT NULL CHECK(language_code IN ('de','en','fr','es','it')),display_name TEXT NOT NULL,PRIMARY KEY(entity_type,entity_id,language_code));
CREATE TABLE IF NOT EXISTS genre_aliases(subgenre_id INTEGER NOT NULL REFERENCES subgenres(id),alias TEXT NOT NULL COLLATE NOCASE,PRIMARY KEY(subgenre_id,alias));
CREATE TABLE IF NOT EXISTS song_genres(song_id INTEGER NOT NULL,subgenre_id INTEGER NOT NULL REFERENCES subgenres(id),role TEXT NOT NULL DEFAULT 'influence' CHECK(role IN ('primary','secondary','influence')),PRIMARY KEY(song_id,subgenre_id));
