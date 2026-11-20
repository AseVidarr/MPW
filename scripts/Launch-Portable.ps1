$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
if(-not (Test-Path -LiteralPath (Join-Path $root '.mpw-portable-v2'))){throw 'Portable-Marker fehlt. Start abgebrochen.'}
$data=Join-Path $root 'Data'
if(Test-Path -LiteralPath $data -PathType Leaf){throw 'Data-Pfad ist eine Datei.'}
New-Item -ItemType Directory -Force -Path $data | Out-Null
& (Join-Path $root 'App/MPW.exe')
exit $LASTEXITCODE
