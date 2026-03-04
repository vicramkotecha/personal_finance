param(
    [int]$ProcessId,
    [string]$AccountName
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

# Navigate via Accounts tree: focus the tree, type first letter to jump,
# then use arrow keys. But this is fragile with tree structure.
# Instead, use the GnuCash URL bar / location bar approach:
# Ctrl+L opens the location bar where you can type an account path.

# First ensure we are on the Accounts tab (not a register) by pressing
# Ctrl+F4 to close any open register tabs, then we navigate fresh.
# Skip this if already on the Accounts page.

# Use Edit > Find Account (Ctrl+I) to search
[System.Windows.Forms.SendKeys]::SendWait("^i")
Start-Sleep -Milliseconds 1000

# Type the account name in the search field and Enter to search
[System.Windows.Forms.SendKeys]::SendWait("($AccountName)")
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1000

# Shift+Tab to highlight the result in the tree
[System.Windows.Forms.SendKeys]::SendWait("+{TAB}")
Start-Sleep -Milliseconds 500

# First Enter selects the account in the tree and closes the dialog
# (Close on Jump is ticked). The account should now be highlighted
# in the main accounts tree.
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1500

# Enter on the tree triggers the OLD selection, not the newly highlighted one.
# Use Edit > Open Account from the menu instead.
[System.Windows.Forms.SendKeys]::SendWait("%e")
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("a")
Start-Sleep -Milliseconds 1500

# Verify the window title now contains the account name
$gnucashProcess = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($gnucashProcess.MainWindowTitle -notlike "*$AccountName*") {
    # If still in dialog, try Escape and report
    [System.Windows.Forms.SendKeys]::SendWait("{ESCAPE}")
    Start-Sleep -Milliseconds 500
    Write-Error "Failed to open register for account: $AccountName. Window title: $($gnucashProcess.MainWindowTitle)"
    exit 1
}

# Jump to the blank transaction row at the bottom (Date field)
[System.Windows.Forms.SendKeys]::SendWait("^{END}")
Start-Sleep -Milliseconds 500

exit 0
