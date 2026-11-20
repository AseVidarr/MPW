#!/usr/bin/env python3
"""MPW workflow acceptance using disposable SQLite; never imports GUI or opens production DB."""
import argparse
import ast
import importlib.util
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / 'source'


def ensure_genre_module(source_dir=SOURCE_DIR):
    """init_database imports mpw_genre_upgrade, which lives next to workstation.py, not in scripts/."""
    if 'mpw_genre_upgrade' in sys.modules:
        return
    spec = importlib.util.spec_from_file_location('mpw_genre_upgrade', Path(source_dir) / 'mpw_genre_upgrade.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules['mpw_genre_upgrade'] = module


def load_schema_initializer(source):
    ensure_genre_module()
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'init_database')
    # Remove default ROOT binding so the isolated test must explicitly supply a temp root.
    node.args.defaults = []
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    scope = {'sqlite3': sqlite3, 'Path': Path}
    exec(compile(module, '<MPW schema initializer>', 'exec'), scope)
    return scope['init_database']


def run(source):
    init = load_schema_initializer(source)
    results = {}
    with tempfile.TemporaryDirectory(prefix='mpw_preview49_') as tmp:
        root = Path(tmp) / 'Data'
        con = init(root)
        try:
            results['schema_and_foreign_keys'] = con.execute('PRAGMA foreign_keys').fetchone()[0] == 1
            with con:
                band = con.execute('INSERT INTO bands(name,genre) VALUES(?,?)', ('Test Band','Blues')).lastrowid
                project = con.execute('INSERT INTO projects(band_id,name) VALUES(?,?)',(band,'Test Project')).lastrowid
                song = con.execute('INSERT INTO songs(project_id,title) VALUES(?,?)',(project,'Test Song')).lastrowid
            results['band_project_song'] = (con.execute('SELECT COUNT(*) FROM songs WHERE project_id=?',(project,)).fetchone()[0] == 1)
            old_style, old_lyrics = 'Blues groove', '[Verse] Test'
            with con:
                con.execute('UPDATE songs SET style=?,lyrics=? WHERE id=?',(old_style,old_lyrics,song))
            new_style = 'Industrial Blues'
            with con:
                previous = con.execute('SELECT style,lyrics FROM songs WHERE id=?',(song,)).fetchone()
                con.execute('INSERT INTO prompt_versions(song_id,provider,model,style,lyrics,brief) VALUES(?,?,?,?,?,?)',
                            (song,'MPW Sicherung','vor Song-Speicherung',*previous,'Automatic history test'))
                con.execute('UPDATE songs SET style=? WHERE id=?',(new_style,song))
            results['prompt_version_preserved'] = (con.execute('SELECT style,lyrics FROM prompt_versions WHERE song_id=?',(song,)).fetchone() == (old_style,old_lyrics)
                                                    and con.execute('SELECT style FROM songs WHERE id=?',(song,)).fetchone()[0] == new_style)
            con.execute('SAVEPOINT reject_orphan')
            try:
                con.execute('INSERT INTO songs(project_id,title) VALUES(?,?)',(999999,'Orphan'))
                results['foreign_key_rejects_orphan'] = False
            except sqlite3.IntegrityError:
                results['foreign_key_rejects_orphan'] = True
            finally:
                con.execute('ROLLBACK TO reject_orphan');con.execute('RELEASE reject_orphan')
            count_before = con.execute('SELECT COUNT(*) FROM songs').fetchone()[0]
            try:
                with con:
                    con.execute('INSERT INTO songs(project_id,title) VALUES(?,?)',(project,'Rolled back'))
                    raise RuntimeError('Simulated write failure')
            except RuntimeError:
                pass
            results['transaction_rollback'] = con.execute('SELECT COUNT(*) FROM songs').fetchone()[0] == count_before
            with con:
                con.execute('DELETE FROM songs WHERE id=?',(song,))
            results['prompt_history_cascade'] = con.execute('SELECT COUNT(*) FROM prompt_versions WHERE song_id=?',(song,)).fetchone()[0] == 0
            results['integrity'] = con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        finally:
            con.close()
    results['temporary_database_only'] = not (root/'workstation.db').exists()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1]/'source/mpw_core.py')
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    result=run(args.source.read_text(encoding='utf-8'))
    print(json.dumps(result,ensure_ascii=False,indent=2) if args.json else f'Workflow acceptance: {sum(result.values())}/{len(result)} checks passed')
    return 0 if all(result.values()) else 1

if __name__ == '__main__':
    raise SystemExit(main())
