# Richtet die KI-Video-Pipeline unter Windows ein.
# Ausfuehren im Ordner KI_Videos:  powershell -ExecutionPolicy Bypass -File setup\install.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$pakete = @(
    @{ Id = 'Python.Python.3.12'; Befehl = 'python' },
    @{ Id = 'Gyan.FFmpeg';        Befehl = 'ffmpeg' }
)
$neuInstalliert = $false
foreach ($p in $pakete) {
    $vorhanden = Get-Command $p.Befehl -ErrorAction SilentlyContinue
    # Der Microsoft-Store-Platzhalter fuer python zaehlt nicht als installiert
    if ($vorhanden -and $vorhanden.Source -notlike '*WindowsApps*') {
        Write-Host "OK      $($p.Befehl) ist schon installiert"
        continue
    }
    Write-Host "INSTALL $($p.Id)"
    winget install --id $p.Id -e --accept-source-agreements --accept-package-agreements
    $neuInstalliert = $true
}

if ($neuInstalliert) {
    Write-Host ''
    Write-Host 'Programme wurden neu installiert. Terminal schliessen, neu oeffnen und dieses Skript nochmal starten.'
    exit 0
}

if (-not (Test-Path '.venv')) {
    Write-Host 'Erstelle virtuelle Python-Umgebung (.venv) ...'
    python -m venv .venv
}
Write-Host 'Installiere Python-Pakete ...'
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Datei .env angelegt: bitte jetzt die API-Keys eintragen (notepad .env).'
}

Write-Host ''
& .\.venv\Scripts\python.exe -m ki_videos nischen
Write-Host ''
Write-Host 'Fertig. Naechste Schritte:'
Write-Host '  1. notepad .env                      (API-Keys eintragen)'
Write-Host '  2. .venv\Scripts\python -m ki_videos erstellen --nische slicelab --skript content\slicelab\01.json'
Write-Host '  3. powershell -ExecutionPolicy Bypass -File setup\upload-job.ps1   (automatische Uploads)'
