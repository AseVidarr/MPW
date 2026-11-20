param(
  [string]$DistDirectory = '',
  [switch]$RunPortableSelfTest
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $DistDirectory) { $DistDirectory = Join-Path $root 'dist' }
if (-not (Test-Path -LiteralPath $DistDirectory -PathType Container)) { throw "dist-Verzeichnis fehlt: $DistDirectory" }
$dist = (Resolve-Path -LiteralPath $DistDirectory).Path
$version = 'v2.2.0_RC2'
$zip = Join-Path $dist "MPW_Portable_$version.zip"
$installer = Join-Path $dist "MPW_Setup_$version.exe"
$exe = Join-Path $dist 'MPW/MPW.exe'
function Assert-NonEmpty([string]$path) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Datei fehlt: $path" }
  if ((Get-Item -LiteralPath $path).Length -le 0) { throw "Datei leer: $path" }
}
Assert-NonEmpty $exe
Assert-NonEmpty $zip
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($zip)
try {
  $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace('c','/') })
  foreach ($required in @('App/MPW.exe','Start-MPW-Portable.cmd','Launch-Portable.ps1')) {
    if (-not ($names | Where-Object { $_ -eq $required -or $_.EndsWith('/' + $required) })) {
      throw "Portable-ZIP unvollstaendig: $required"
    }
  }
} finally { $archive.Dispose() }
$report = [ordered]@{
  Release = $version
  PortableZip = $zip
  PortableSHA256 = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
  PortableContent = 'passed'
  Installer = if (Test-Path -LiteralPath $installer -PathType Leaf) { 'present' } else { 'missing' }
  InstallerSHA256 = if (Test-Path -LiteralPath $installer -PathType Leaf) { (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash } else { $null }
  PortableSelfTest = 'not_run'
  GuiAndDataMigration = 'manual_check_required'
}
if ($RunPortableSelfTest) {
  & $exe --self-test
  if ($LASTEXITCODE -ne 0) { throw "EXE-Selbsttest fehlgeschlagen: $LASTEXITCODE" }
  $report.PortableSelfTest = 'passed'
}
$report | ConvertTo-Json -Depth 3
if ($report.Installer -eq 'missing') { throw "Installer fehlt: $installer" }
