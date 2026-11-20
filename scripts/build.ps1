param([switch]$SkipInstall, [switch]$SkipSelfTest)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
function Assert-LastExit([string]$step) {
  if ($LASTEXITCODE -ne 0) { throw "$step fehlgeschlagen (Exitcode: $LASTEXITCODE)" }
}
function Assert-NonEmptyFile([string]$path, [string]$label) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "$label fehlt: $path" }
  if ((Get-Item -LiteralPath $path).Length -le 0) { throw "$label ist leer: $path" }
}

$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$src=Join-Path $root 'source'
$dist=Join-Path $root 'dist'
$build=Join-Path $root 'build'
New-Item -ItemType Directory -Force $dist,$build | Out-Null
$py=(Get-Command py -ErrorAction SilentlyContinue)
if(-not $py){throw 'Python Launcher py.exe (Python 3.10+) fehlt'}
& py -3 -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ erforderlich"'
Assert-LastExit 'Python-Versionspruefung'

if(-not $SkipInstall){
  & py -3 -m pip install --upgrade 'pyinstaller>=6.10,<7' -r (Join-Path $src 'requirements.txt')
  Assert-LastExit 'pip'
}
& py -3 -c 'import PyInstaller, PySide6, mutagen'
Assert-LastExit 'Build-Abhaengigkeiten'

if(-not $SkipSelfTest){
  & py -3 (Join-Path $src 'workstation.py') --self-test
  Assert-LastExit 'Quellcode-Selbsttest'
}
if(-not $SkipSelfTest){
  & py -3 (Join-Path $src 'mpw_mcp_server.py') --self-test
  Assert-LastExit 'MCP-Quellcode-Selbsttest'
}
if(-not $SkipSelfTest){
  & py -3 (Join-Path $src 'mpw_web.py') --self-test
  Assert-LastExit 'Web-Quellcode-Selbsttest'
}
# One spec builds MPW.exe (window) and MPW-MCP.exe (console MCP server) into dist\MPW.
& py -3 -m PyInstaller --noconfirm --clean --distpath $dist --workpath $build (Join-Path $root 'installer/MPW.spec')
Assert-LastExit 'PyInstaller'
$exe=Join-Path $dist 'MPW/MPW.exe'
Assert-NonEmptyFile $exe 'MPW.exe'
& $exe --self-test
Assert-LastExit 'EXE-Selbsttest'
$mcpExe=Join-Path $dist 'MPW/MPW-MCP.exe'
Assert-NonEmptyFile $mcpExe 'MPW-MCP.exe'
& $mcpExe --self-test
Assert-LastExit 'MCP-Selbsttest'
$webExe=Join-Path $dist 'MPW/MPW-Web.exe'
Assert-NonEmptyFile $webExe 'MPW-Web.exe'
& $webExe --self-test
Assert-LastExit 'Web-Selbsttest'
$portable=Join-Path $dist 'MPW_Portable_v2.2.0_RC2'
if(Test-Path $portable){throw 'Portable-Ziel existiert bereits. Bitte alte Ausgabe manuell sichern/umbenennen; keine automatische Loeschung.'}
New-Item -ItemType Directory $portable | Out-Null
Copy-Item (Join-Path $dist 'MPW') (Join-Path $portable 'App') -Recurse
Assert-NonEmptyFile (Join-Path $portable 'App/MPW.exe') 'Portable MPW.exe'
Assert-NonEmptyFile (Join-Path $portable 'App/MPW-MCP.exe') 'Portable MPW-MCP.exe'
Assert-NonEmptyFile (Join-Path $portable 'App/MPW-Web.exe') 'Portable MPW-Web.exe'
Copy-Item (Join-Path $root 'scripts/Start-MPW-Portable.cmd') $portable
Copy-Item (Join-Path $root 'scripts/Start-MPW-Web-Portable.cmd') $portable
Copy-Item (Join-Path $root 'scripts/Launch-Portable.ps1') $portable
'Standalone MPW portable build v2.2.0 RC2' | Set-Content -LiteralPath (Join-Path $portable '.mpw-portable-v2') -Encoding Ascii
'Portable data is stored in Data. Do not delete this directory during updates.' | Set-Content -Encoding UTF8 (Join-Path $portable 'DATEN_HINWEIS.txt')
$portableZip=Join-Path $dist 'MPW_Portable_v2.2.0_RC2.zip'
if(Test-Path $portableZip){throw 'Portable-ZIP existiert bereits. Bitte alte Ausgabe manuell sichern/umbenennen.'}
Compress-Archive -Path (Join-Path $portable '*') -DestinationPath $portableZip
Assert-NonEmptyFile $portableZip 'Portable-ZIP'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipReader=[System.IO.Compression.ZipFile]::OpenRead($portableZip)
try {
  if (-not ($zipReader.Entries | Where-Object { ($_.FullName -replace '\\', '/') -match '(^|/)App/MPW\.exe$' })) {
    throw 'Portable-ZIP enthaelt keine App/MPW.exe'
  }
  if (-not ($zipReader.Entries | Where-Object { ($_.FullName -replace '\\', '/') -match '(^|/)Start-MPW-Portable\.cmd$' })) {
    throw 'Portable-ZIP enthaelt keinen Start-Launcher'
  }
} finally { $zipReader.Dispose() }
$iss=Join-Path $root 'installer/MPW.iss'
$isccCommand=Get-Command ISCC.exe -ErrorAction SilentlyContinue
$isccPath=$null
if($isccCommand){$isccPath=$isccCommand.Source}
if(-not $isccPath){
  foreach($candidate in @('C:\Program Files\Inno Setup 7\ISCC.exe','C:\Program Files (x86)\Inno Setup 7\ISCC.exe','C:\Program Files (x86)\Inno Setup 6\ISCC.exe','C:\Program Files\Inno Setup 6\ISCC.exe')){
    if(Test-Path -LiteralPath $candidate){$isccPath=$candidate;break}
  }
}
if($isccPath){
  Write-Host "Inno Setup Compiler: $isccPath"
  & $isccPath $iss
  Assert-LastExit 'Inno Setup'
  Assert-NonEmptyFile (Join-Path $dist 'MPW_Setup_v2.2.0_RC2.exe') 'Installer-EXE'
}else{
  Write-Warning 'ISCC.exe fehlt. Portable-Version wurde erstellt, Installer noch nicht kompiliert. Inno Setup 7 oder 6 installieren und Build erneut starten.'
}
$checksumPath=Join-Path $dist 'SHA256SUMS.txt'
$hashLines=@(Get-ChildItem -LiteralPath $dist -File -Recurse |
  Where-Object { $_.FullName -ne $checksumPath } |
  ForEach-Object {
    $hash=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    "$hash  $($_.FullName.Substring($dist.Length+1))"
  })
$hashLines | Set-Content -LiteralPath $checksumPath -Encoding UTF8
Assert-NonEmptyFile $checksumPath 'SHA256SUMS.txt'
Write-Host 'Build abgeschlossen. Verfuegbare Artefakte unter dist. Installer nur bei vorhandenem Inno Setup.'
