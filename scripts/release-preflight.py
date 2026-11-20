#!/usr/bin/env python3
"""Read-only source release preflight; does not build or run Windows GUI."""
from pathlib import Path
import ast, json, re, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
VERSION="2.2.0 RC2"
checks={}
app=ROOT/'source/workstation.py'
core=ROOT/'source/mpw_core.py'  # Qt-free core: APP_VERSION, data root, schema
try:
    for source in (app, core, ROOT/'source/mpw_web.py', ROOT/'source/mpw_mcp_server.py'):
        ast.parse(source.read_text(encoding="utf-8"))
    checks["python_syntax"]="passed"
except (SyntaxError, OSError) as exc:
    checks["python_syntax"]=f"failed: {exc}"
apptext=app.read_text(encoding="utf-8")+core.read_text(encoding="utf-8")
checks["app_version"]="passed" if f"APP_VERSION = '{VERSION}'" in apptext else "failed"
build=(ROOT/'scripts/build.ps1').read_text(encoding="utf-8")
iss=(ROOT/'installer/MPW.iss').read_text(encoding="utf-8")
checks["portable_name"]="passed" if "MPW_Portable_v2.2.0_RC2" in build and "Preview47" not in build else "failed"
checks["installer_name"]="passed" if "MPW_Setup_v2.2.0_RC2" in iss and "MPW_Setup_v2.2.0_RC2.exe" in build else "failed"
checks["installer_no_data_delete"]="passed" if "[UninstallDelete]" not in iss and "[InstallDelete]" not in iss else "failed"
checks["portable_data_note"]="passed" if "Do not delete this directory during updates." in build else "failed"
checks["windows_gui_test"]="not_run (requires Windows)"
checks["windows_installer_build"]="not_run (requires Windows and Inno Setup)"
print(json.dumps(checks,indent=2,ensure_ascii=False))
sys.exit(1 if any(v.startswith("failed") for v in checks.values()) else 0)
