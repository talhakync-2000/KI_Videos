# Legt eine Windows-Aufgabe an, die alle 15 Minuten faellige Videos hochlaedt.
# Ausfuehren:  powershell -ExecutionPolicy Bypass -File setup\upload-job.ps1
# Entfernen:   schtasks /Delete /TN "KI_Videos Upload" /F
$cmd = Join-Path $PSScriptRoot 'upload.cmd'
schtasks /Create /TN "KI_Videos Upload" /SC MINUTE /MO 15 /TR "`"$cmd`"" /F
Write-Host ''
Write-Host 'Aufgabe "KI_Videos Upload" angelegt. Sie laeuft alle 15 Minuten, solange du angemeldet bist.'
Write-Host 'Log: output\upload.log'
Write-Host 'Hinweis: Ist der PC zur Posting-Zeit aus, wird das Video beim naechsten Lauf nachgeholt.'
