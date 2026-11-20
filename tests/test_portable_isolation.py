import ast, pathlib, tempfile, sys, os
source=pathlib.Path(__file__).resolve().parents[1]/'source'/'mpw_core.py'  # data root logic lives in the Qt-free core
module=ast.parse(source.read_text(encoding='utf-8'))
nodes=[n for n in module.body if (isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('portable_root','resolve_data_root','portable_root_for','TranslocatedError')) or (isinstance(n,ast.Assign) and any(getattr(t,'id','')=='PORTABLE_MARKER' for t in n.targets))]
namespace={'Path':pathlib.Path,'sys':sys,'os':os,'json':__import__('json'),'LEGACY_ROOT':pathlib.Path(tempfile.gettempdir())/'MPW_legacy_dummy'}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
with tempfile.TemporaryDirectory() as temp:
 root=pathlib.Path(temp)/'Portable'; (root/'App').mkdir(parents=True); (root/'.mpw-portable-v2').write_text('test'); exe=root/'App'/'MPW.exe';exe.touch()
 original_exe=sys.executable; original_frozen=getattr(sys,'frozen',None)
 try:
  sys.executable=str(exe);sys.frozen=True
  os.environ['MPW_DATA_ROOT']=str(pathlib.Path(temp)/'PRODUCTION')
  assert namespace['resolve_data_root']()==root/'Data', 'Portable should ignore environment override'
  (root/'.mpw-portable-v2').unlink()
  assert namespace['portable_root']() is None
  (root/'.mpw-portable-v2').write_text('test')
  production=pathlib.Path(temp)/'PRODUCTION'; production.mkdir()
  try:(root/'Data').symlink_to(production,target_is_directory=True)
  except OSError:
   # Windows without admin/developer mode (WinError 1314): use a directory junction,
   # which needs no special right and must be rejected just like a symlink.
   if os.name!='nt':raise
   import _winapi;_winapi.CreateJunction(str(production),str(root/'Data'))
  try:namespace['resolve_data_root']();raise AssertionError('Symlink not rejected')
  except RuntimeError:pass
 finally:
  sys.executable=original_exe
  if original_frozen is None:del sys.frozen
  else:sys.frozen=original_frozen
  os.environ.pop('MPW_DATA_ROOT',None)
print('Portable resolver isolation tests passed')
