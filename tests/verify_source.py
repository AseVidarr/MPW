import ast,hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'source/workstation.py'
core=root/'source/mpw_core.py'  # data root logic (incl. MPW_DATA_ROOT) lives in the Qt-free core
for source in (p, core, root/'source/mpw_web.py', root/'source/mpw_mcp_server.py'):
    ast.parse(source.read_text(encoding='utf8'))
assert 'MPW_DATA_ROOT' in core.read_text(encoding='utf8')
assert 'MPW_DATA_ROOT' not in (root/'source/README_START.md').read_text(encoding='utf8')
print('Source syntax OK; portable override present; no user data inspected')
