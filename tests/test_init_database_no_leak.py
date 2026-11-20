"""init_database must close its connection when schema setup fails (Windows file lock)."""
import ast
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'source' / 'mpw_core.py'  # init_database lives in the Qt-free core


def load_init():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'init_database')
    node.args.defaults = []
    ns = {'sqlite3': sqlite3, 'Path': Path}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(SOURCE), 'exec'), ns)
    return ns['init_database']


class InitDatabaseNoLeak(unittest.TestCase):
    def test_failed_setup_closes_connection(self):
        init = load_init()
        saved = sys.modules.get('mpw_genre_upgrade', ...)
        sys.modules['mpw_genre_upgrade'] = None  # makes the import inside init_database fail
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'Data'
                with self.assertRaises(ImportError):
                    init(root)
                # Fails with WinError 32 on Windows if the handle was leaked.
                os.remove(root / 'workstation.db')
        finally:
            if saved is ...:
                del sys.modules['mpw_genre_upgrade']
            else:
                sys.modules['mpw_genre_upgrade'] = saved


if __name__ == '__main__':
    unittest.main()
