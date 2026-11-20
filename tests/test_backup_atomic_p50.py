import ast, importlib.util, sqlite3, tempfile, zipfile, unittest
from pathlib import Path
from contextlib import closing
from datetime import datetime
import os, shutil
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'source/mpw_core.py').read_text(encoding='utf-8')  # backup functions live in the Qt-free core
NAMES=['check_database_integrity','validate_backup','_write_backup_archive','restore_backup']
TREE=ast.parse(SOURCE)
MODULE=ast.Module(body=[n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name in NAMES],type_ignores=[])
NS=dict(Path=Path,sqlite3=sqlite3,zipfile=zipfile,closing=closing,tempfile=tempfile,shutil=shutil,datetime=datetime,os=os)
exec(compile(ast.fix_missing_locations(MODULE),'mpw_core.py','exec'),NS)
class BackupAtomicTests(unittest.TestCase):
 def db(self,path):
  con=sqlite3.connect(path)
  con.execute('CREATE TABLE bands(id INTEGER PRIMARY KEY)')
  for t in ('projects','songs','releases','media_assets'): con.execute(f'CREATE TABLE {t}(id INTEGER PRIMARY KEY)')
  con.execute('INSERT INTO bands VALUES (1)');con.commit();return con
 def test_archive_contains_only_database_and_info(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); con=self.db(root/'workstation.db')
   try:
    out=NS['_write_backup_archive'](con,root,root/'backup.zip')
    self.assertTrue(NS['validate_backup'](out))
    with zipfile.ZipFile(out) as z:self.assertEqual(set(z.namelist()),{'workstation.db','backup_info.txt'})
   finally:con.close()
 def test_existing_archive_preserved_if_backup_fails(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); dest=root/'backup.zip';dest.write_bytes(b'original')
   con=sqlite3.connect(':memory:')
   try:
    with self.assertRaises(ValueError):NS['_write_backup_archive'](con,root,dest)
    self.assertEqual(dest.read_bytes(),b'original')
    self.assertFalse(list(root.glob('.mpw_backup_*')))
   finally:con.close()
 def test_corrupt_archive_cannot_replace_live_database(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); live=root/'workstation.db'; con=self.db(live);con.close()
   before=live.read_bytes();bad=root/'bad.zip';bad.write_bytes(b'bad')
   with self.assertRaises(zipfile.BadZipFile):NS['restore_backup'](bad,root)
   self.assertEqual(live.read_bytes(),before)
 def test_wal_sidecar_blocks_restore(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); live=root/'workstation.db';con=self.db(live)
   try:NS['_write_backup_archive'](con,root,root/'good.zip')
   finally:con.close()
   (root/'workstation.db-wal').write_bytes(b'guard')
   before=live.read_bytes()
   with self.assertRaises(RuntimeError):NS['restore_backup'](root/'good.zip',root)
   self.assertEqual(live.read_bytes(),before)
 def test_restore_preserves_media(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);live=root/'workstation.db';con=self.db(live)
   try:NS['_write_backup_archive'](con,root,root/'good.zip')
   finally:con.close()
   media=root/'media';media.mkdir();(media/'song.wav').write_bytes(b'unchanged')
   with closing(sqlite3.connect(live)) as c, c:c.execute('INSERT INTO bands VALUES (2)')
   NS['restore_backup'](root/'good.zip',root)
   with closing(sqlite3.connect(live)) as c, c:self.assertEqual(c.execute('SELECT count(*) FROM bands').fetchone()[0],1)
   self.assertEqual((media/'song.wav').read_bytes(),b'unchanged')

if __name__ == '__main__':
    unittest.main()
