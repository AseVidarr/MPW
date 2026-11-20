#!/usr/bin/env python3
"""Read-only SQLite integrity and media-reference inspection for offline test copies.

Run only with MPW closed; WAL state and schema-specific media references require manual review.
"""
import argparse
import json
from pathlib import Path
import sqlite3
import sys


def inspect_database(db_path, media_roots=(), mpw_root=None):
    path = Path(db_path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("SQLite-Pfad ist keine Datei")
    # mode=ro prohibits writes, immutable=1 would ignore live WAL data.
    uri = path.as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=2)
    try:
        integrity = [row[0] for row in con.execute("PRAGMA integrity_check")]
        foreign_keys = [tuple(row) for row in con.execute("PRAGMA foreign_key_check")]
        tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        counts = {}
        for table in tables:
            escaped = table.replace('"', '""')
            counts[table] = con.execute(f'SELECT count(*) FROM "{escaped}"').fetchone()[0]
        # Only validate columns that unambiguously contain absolute paths.
        # Relative paths and URI-style references require application-specific resolution.
        missing = []
        checked = 0
        roots = [Path(root).resolve() for root in media_roots]
        for table in tables:
            escaped = table.replace('"', '""')
            cols = [r[1] for r in con.execute(f'PRAGMA table_info("{escaped}")')]
            for col in cols:
                if col.lower() not in ('file_path','filepath','media_path','cover_path','audio_path'):
                    continue
                ec = col.replace('"', '""')
                for (value,) in con.execute(f'SELECT "{ec}" FROM "{escaped}" WHERE "{ec}" IS NOT NULL'):
                    if not isinstance(value, str) or not value.strip():
                        continue
                    candidate = Path(value)
                    if not candidate.is_absolute():
                        continue
                    resolved = candidate.resolve()
                    if roots and not any(resolved == root or root in resolved.parents for root in roots):
                        continue
                    checked += 1
                    if not resolved.is_file():
                        missing.append({'table': table, 'column': col, 'path': value})
        # MPW-specific relative paths are rooted at the application's ROOT directory,
        # never at the current working directory or the database's parent by guesswork.
        relative_checked = 0
        relative_missing = []
        relative_unsafe = []
        relative_unresolved = 0
        for table, column in [('media_assets', 'relative_path'), ('albums', 'cover_path')]:
            if table not in tables:
                continue
            escaped = table.replace('"', '""')
            columns = [r[1] for r in con.execute(f'PRAGMA table_info("{escaped}")')]
            if column not in columns:
                continue
            for (value,) in con.execute(f'SELECT "{column}" FROM "{escaped}" WHERE "{column}" IS NOT NULL'):
                if not isinstance(value, str) or not value.strip():
                    continue
                # Absolute references are handled by the generic path check for cover_path.
                if Path(value).is_absolute():
                    continue
                if mpw_root is None:
                    relative_unresolved += 1
                    continue
                root = Path(mpw_root).resolve()
                candidate = (root / value).resolve()
                if candidate != root and root not in candidate.parents:
                    relative_unsafe.append({'table': table, 'column': column, 'path': value})
                    continue
                relative_checked += 1
                if not candidate.is_file():
                    relative_missing.append({'table': table, 'column': column, 'path': value})
        return {'database': str(path), 'integrity_ok': integrity == ['ok'],
                'integrity_messages': integrity, 'foreign_key_violations': len(foreign_keys),
                'foreign_key_details': foreign_keys[:20], 'table_counts': counts,
                'absolute_media_paths_checked': checked, 'missing_media': missing,
                'mpw_relative_paths_checked': relative_checked,
                'mpw_relative_paths_unresolved': relative_unresolved,
                'missing_mpw_media': relative_missing, 'unsafe_mpw_paths': relative_unsafe,
                'ok': integrity == ['ok'] and not foreign_keys and not missing and not relative_missing and not relative_unsafe and relative_unresolved == 0}
    finally:
        con.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', help='SQLite-Datei (nur lesend)')
    parser.add_argument('--mpw-root', help='MPW-Anwendungsverzeichnis ROOT für relative Medienpfade')
    parser.add_argument('--media-root', action='append', default=[], help='Optionale Medienwurzel; mehrfach möglich')
    parser.add_argument('--output', help='Neuer JSON-Bericht außerhalb des Datenbestands')
    args = parser.parse_args(argv)
    try:
        report = inspect_database(args.database, args.media_root, args.mpw_root)
        content = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            dest = Path(args.output).resolve()
            db = Path(args.database).resolve()
            if dest == db or dest.exists() or dest.parent == db.parent:
                raise ValueError('Bericht muss neu sein und außerhalb des Datenbankordners liegen')
            with dest.open('x', encoding='utf-8') as file:
                file.write(content + '\n')
        print(content)
        return 0 if report['ok'] else 2
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f'Prüfung fehlgeschlagen: {exc}', file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())
