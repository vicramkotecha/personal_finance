param(
    [int]$ProcessId,
    [string]$Date,
    [string]$Description,
    [string]$Transfer,
    [string]$Deposit,
    [string]$Withdrawal,
    [string]$FxRate = ''
)

Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int count);
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

# Date — select all and overwrite (may have pre-populated date)
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Date))")
Start-Sleep -Milliseconds $delay
# TAB past Date
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay
# TAB past Num (left blank)
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Description — type it with trailing 'a' to defeat autocomplete
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Description))")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("a")
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Transfer — clear field then type full path
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Transfer))")
Start-Sleep -Milliseconds $delay

# Shift-Tab back to Description, press End then Backspace to remove trailing 'a'
[System.Windows.Forms.SendKeys]::SendWait("+{TAB}")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("{END}")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
Start-Sleep -Milliseconds $delay

# Tab forward to Transfer (still has our text), then Tab to amount
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Milliseconds $delay

# Deposit or Withdrawal (R field is skipped automatically)
if ($Deposit -ne '') {
    [System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Deposit))")
    Start-Sleep -Milliseconds $delay
}

if ($Withdrawal -ne '') {
    # TAB past Deposit (leave blank), then type withdrawal
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    Start-Sleep -Milliseconds $delay
    [System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $Withdrawal))")
    Start-Sleep -Milliseconds $delay
}

# ENTER to save transaction and move to next blank row
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1000

# Handle "Transfer Funds" currency dialog if it appears
# Check the foreground window title (modal dialogs have their own window)
$fgWnd = [Win32]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 256
[Win32]::GetWindowText($fgWnd, $sb, 256) | Out-Null
$fgTitle = $sb.ToString()

if ($fgTitle -like '*Transfer Funds*') {
    # TAB to the Exchange Rate field
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    [System.Windows.Forms.SendKeys]::SendWait("{TAB}")
    # Exchange Rate field should have focus — clear and type the rate
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds $delay
    [System.Windows.Forms.SendKeys]::SendWait("($(Escape-SendKeys $FxRate))")
    Start-Sleep -Milliseconds $delay
    # Press Enter to confirm (OK is the default button)
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 1000
}

exit 0
