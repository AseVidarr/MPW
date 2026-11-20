# -*- mode: python ; coding: utf-8 -*-
# PyInstaller build for MPW: MPW.exe (window), MPW-MCP.exe (console MCP server, stdio) and
# MPW-Web.exe (console, local browser GUI on 127.0.0.1) share one folder, so the portable App\
# detection and the data root are identical for all three.
import os

SRC = os.path.abspath(os.path.join(SPECPATH, '..', 'source'))
DATAS = [(os.path.join(SRC, 'MPW_Genre_Katalog_v1.json'), '.')]
WEB_DATAS = DATAS + [(os.path.join(SRC, 'web'), 'web')]

app = Analysis([os.path.join(SRC, 'workstation.py')], pathex=[SRC], datas=DATAS)
mcp = Analysis([os.path.join(SRC, 'mpw_mcp_server.py')], pathex=[SRC], datas=DATAS)
web = Analysis([os.path.join(SRC, 'mpw_web.py')], pathex=[SRC], datas=WEB_DATAS)

app_exe = EXE(PYZ(app.pure), app.scripts, [], exclude_binaries=True,
              name='MPW', console=False, upx=False)
mcp_exe = EXE(PYZ(mcp.pure), mcp.scripts, [], exclude_binaries=True,
              name='MPW-MCP', console=True, upx=False)
web_exe = EXE(PYZ(web.pure), web.scripts, [], exclude_binaries=True,
              name='MPW-Web', console=True, upx=False)

COLLECT(app_exe, app.binaries, app.datas,
        mcp_exe, mcp.binaries, mcp.datas,
        web_exe, web.binaries, web.datas,
        upx=False, name='MPW')
