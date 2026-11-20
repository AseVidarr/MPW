"""Additive, idempotent MPW genre reference-data migration."""
import json
from pathlib import Path


def install(con, catalog_path=None):
    catalog_path = Path(catalog_path or Path(__file__).with_name('MPW_Genre_Katalog_v1.json'))
    if not catalog_path.is_file():
        return False
    data = json.loads(catalog_path.read_text(encoding='utf-8'))
    if len(data['main_genres']) != 45 or len(data['subgenres']) != 408:
        raise ValueError('Unexpected MPW genre catalog counts')
    relations = [(g['id'], sub) for g in data['main_genres'] for sub in g['subgenre_ids']]
    if len(relations) != 415:
        raise ValueError('Unexpected MPW genre relation count')
    with con:
        con.execute('CREATE TABLE IF NOT EXISTS mpw_main_genres (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE)')
        con.execute('CREATE TABLE IF NOT EXISTS mpw_subgenres (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE)')
        con.execute('CREATE TABLE IF NOT EXISTS mpw_genre_relations (main_id INTEGER NOT NULL REFERENCES mpw_main_genres(id), sub_id INTEGER NOT NULL REFERENCES mpw_subgenres(id), PRIMARY KEY(main_id,sub_id))')
        con.execute("CREATE TABLE IF NOT EXISTS mpw_genre_translations (kind TEXT NOT NULL CHECK(kind IN ('main','sub')), genre_id INTEGER NOT NULL, lang TEXT NOT NULL CHECK(lang IN ('de','en','fr','es','it')), display_name TEXT NOT NULL, PRIMARY KEY(kind,genre_id,lang))")
        con.execute('CREATE TABLE IF NOT EXISTS mpw_genre_aliases (sub_id INTEGER NOT NULL REFERENCES mpw_subgenres(id), alias TEXT NOT NULL COLLATE NOCASE, PRIMARY KEY(sub_id,alias))')
        con.execute("CREATE TABLE IF NOT EXISTS mpw_song_genres (song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE, sub_id INTEGER NOT NULL REFERENCES mpw_subgenres(id), role TEXT NOT NULL DEFAULT 'influence' CHECK(role IN ('primary','secondary','influence')), PRIMARY KEY(song_id,sub_id))")
        con.executemany('INSERT OR IGNORE INTO mpw_main_genres(id,name) VALUES(?,?)', ((g['id'],g['name']) for g in data['main_genres']))
        con.executemany('INSERT OR IGNORE INTO mpw_subgenres(id,name) VALUES(?,?)', ((g['id'],g['name']) for g in data['subgenres']))
        con.executemany('INSERT OR IGNORE INTO mpw_genre_relations(main_id,sub_id) VALUES(?,?)', relations)
        con.executemany('INSERT OR IGNORE INTO mpw_genre_translations(kind,genre_id,lang,display_name) VALUES(?,?,?,?)', (('main',g['id'],'en',g['name']) for g in data['main_genres']))
        con.executemany('INSERT OR IGNORE INTO mpw_genre_translations(kind,genre_id,lang,display_name) VALUES(?,?,?,?)', (('sub',g['id'],'en',g['name']) for g in data['subgenres']))
        # Preserve all legacy entries and assignments; extend the existing flat dropdowns.
        con.executemany('INSERT OR IGNORE INTO genre_catalog(name) VALUES(?)', ((g['name'],) for g in data['main_genres']))
        con.executemany('INSERT OR IGNORE INTO genre_catalog(name) VALUES(?)', ((g['name'],) for g in data['subgenres']))
    return True
