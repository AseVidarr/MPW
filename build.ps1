# Einstiegspunkt im Projekt-Hauptordner
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'scripts\build.ps1') @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
