param(
    [string]$GnuCashFile
)

$GNUCASH_HOME = $env:GNUCASH_HOME
$GNUCASH_EXE = Join-Path $GNUCASH_HOME 'gnucash.exe'

# Launch GnuCash with the specified file (quote path for spaces)
Start-Process -FilePath $GNUCASH_EXE -ArgumentList "`"$GnuCashFile`""

# Wait for the fully-loaded main window (title contains " - " e.g. "Unsaved Book - GnuCash")
# The splash screen title won't have that pattern
$timeout = 60
$timer = [Diagnostics.Stopwatch]::StartNew()
$gnucashProcess = $null

do {
    Start-Sleep -Milliseconds 500
    $gnucashProcess = Get-Process -Name gnucash -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowTitle -like '* - *GnuCash' } |
        Select-Object -First 1
} until ($gnucashProcess -or ($timer.Elapsed.TotalSeconds -gt $timeout))
$timer.Stop()

if (-not $gnucashProcess) {
    Write-Error "Timeout waiting for GnuCash main window"
    Get-Process -Name gnucash -ErrorAction SilentlyContinue | Stop-Process -Force
    exit 1
}

# Output the PID for the caller
Write-Output $gnucashProcess.Id

exit 0
