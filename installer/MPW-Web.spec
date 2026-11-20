# -*- mode: python ; coding: utf-8 -*-
# PyInstaller build for the web-only portable packages (macOS, Linux):
#   App/MPW-Web  – local browser GUI (127.0.0.1)
#   App/MPW-MCP  – MCP server (stdio)
# Both use the Qt-free core (mpw_core.py); PySide6 is excluded on purpose.
# Windows keeps using MPW.spec (desktop app + web + MCP).
import os

SRC = os.path.abspath(os.path.join(SPECPATH, '..', 'source'))
CATALOG = (os.path.join(SRC, 'MPW_Genre_Katalog_v1.json'), '.')
NO_QT = ['PySide6', 'shiboken6']

web = Analysis([os.path.join(SRC, 'mpw_web.py')], pathex=[SRC],
               datas=[CATALOG, (os.path.join(SRC, 'web'), 'web')], excludes=NO_QT)
mcp = Analysis([os.path.join(SRC, 'mpw_mcp_server.py')], pathex=[SRC], datas=[CATALOG], excludes=NO_QT)

web_exe = EXE(PYZ(web.pure), web.scripts, [], exclude_binaries=True,
              name='MPW-Web', console=True, upx=False)
mcp_exe = EXE(PYZ(mcp.pure), mcp.scripts, [], exclude_binaries=True,
              name='MPW-MCP', console=True, upx=False)

COLLECT(web_exe, web.binaries, web.datas,
        mcp_exe, mcp.binaries, mcp.datas,
        upx=False, name='App')
