param(
    [string]$GnuCashFile
)

$GNUCASH_HOME = $env:GNUCASH_HOME
$GNUCASH_EXE = Join-Path $GNUCASH_HOME 'gnucash.exe'

Add-Type -AssemblyName System.Windows.Forms

# Launch GnuCash with the specified file
Start-Process -FilePath $GNUCASH_EXE -ArgumentList $GnuCashFile

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

# Bring window to foreground and send Ctrl+Q for a clean quit
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
    }
"@

# Output the window title for verification
Write-Output $gnucashProcess.MainWindowTitle

[Win32]::SetForegroundWindow($gnucashProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait('^q')

# Wait for GnuCash to exit
$gnucashProcess.WaitForExit(15000) | Out-Null

if (-not $gnucashProcess.HasExited) {
    $gnucashProcess | Stop-Process -Force
    exit 1
}

exit $gnucashProcess.ExitCode
