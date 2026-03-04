param(
    [int]$ProcessId,
    [string]$Date,
    [string]$Description,
    [string]$Transfer,
    [string]$Deposit,
    [string]$Withdrawal
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

# Bring GnuCash to foreground
[Win32]::SetForegroundWindow($gnucashProcess.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500

# Sanitize strings for SendKeys special characters: +^%~{}[]()
function Escape-SendKeys([string]$text) {
    $text = $text -replace '([+^%~{}()\[\]])', '{$1}'
    return $text
}

$delay = 300

# Date
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Date))")
Start-Sleep -Milliseconds $delay
# TAB past Date
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay
# TAB past Num (left blank)
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Description — clear any autocomplete first
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Description))")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Transfer — clear field then type full path
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Transfer))")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# TAB past R (reconciled, leave default n)
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Deposit or Withdrawal
if ($Deposit -ne '') {
    [System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Deposit))")
    Start-Sleep -Milliseconds $delay
    # TAB past Withdrawal (leave blank) then ENTER to save
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds $delay
}

if ($Withdrawal -ne '') {
    # TAB past Deposit (leave blank)
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds $delay
    [System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Withdrawal))")
    Start-Sleep -Milliseconds $delay
}

# ENTER to save transaction and move to next blank row
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds $delay

exit 0
