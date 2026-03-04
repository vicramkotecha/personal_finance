param(
    [int]$ProcessId
)

Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
    }
"@

$gnucashProcess = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue

if (-not $gnucashProcess) {
    Write-Error "No process found with PID $ProcessId"
    exit 1
}

# Bring window to foreground, save, then quit
[Win32]::SetForegroundWindow($gnucashProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500

# Save first (Ctrl+S)
[System.Windows.Forms.SendKeys]::SendWait('^s')
Start-Sleep -Milliseconds 1000

# Quit (Ctrl+Q)
[System.Windows.Forms.SendKeys]::SendWait('^q')
Start-Sleep -Milliseconds 1000

# Wait for GnuCash to exit
$gnucashProcess.WaitForExit(15000) | Out-Null

if (-not $gnucashProcess.HasExited) {
    $gnucashProcess | Stop-Process -Force
    exit 1
}

exit $gnucashProcess.ExitCode
