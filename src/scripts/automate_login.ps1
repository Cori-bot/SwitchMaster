# Script de login Riot Client : frappe via presse-papier (indépendant du clavier
# AZERTY/IME) avec focus de fenêtre robuste (Win32), en un seul appel.
param (
    [string]$Username = "",
    [string]$Password = ""
)

Add-Type -AssemblyName System.Windows.Forms

# Win32 pour un focus fiable : SetForegroundWindow + restauration + vérification.
# Plus robuste que WScript.Shell.AppActivate seul (qui dépend de l'ordre des fenêtres).
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class SmWin32 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
}
"@

# Constantes de timing
$FOCUS_MAX_ATTEMPTS = 30
$FOCUS_POLL_INTERVAL_MS = 1000
$SHORT_DELAY_MS = 120
$MEDIUM_DELAY_MS = 180
$LONG_DELAY_MS = 500
$SW_RESTORE = 9

# Presse-papier sécurisé (exclut de l'historique Windows et du cloud)
function Set-SecureClipboard {
    param([string]$Content)

    if ([string]::IsNullOrWhiteSpace($Content)) { return }

    try {
        $dataObject = New-Object System.Windows.Forms.DataObject
        $dataObject.SetText($Content, [System.Windows.Forms.TextDataFormat]::UnicodeText)

        # CanIncludeInClipboardHistory = 0, ExcludeFromCloudClipboard = 1
        $zero = [byte[]]@(0,0,0,0)
        $one = [byte[]]@(1,0,0,0)

        $msHistory = New-Object System.IO.MemoryStream
        $msHistory.Write($zero, 0, 4)
        $dataObject.SetData("CanIncludeInClipboardHistory", $msHistory)

        $msCloud = New-Object System.IO.MemoryStream
        $msCloud.Write($one, 0, 4)
        $dataObject.SetData("ExcludeFromCloudClipboard", $msCloud)

        [System.Windows.Forms.Clipboard]::SetDataObject($dataObject, $true)
    }
    catch {
        # Fallback simple
        [System.Windows.Forms.Clipboard]::SetText($Content)
    }
}

# Trouve la fenêtre du Riot Client
function Get-RiotWindow {
    $processes = Get-Process | Where-Object {
        $_.MainWindowTitle -like "*Riot Client*" -or $_.Name -like "RiotClientServices"
    }
    foreach ($proc in $processes) {
        if ($proc.MainWindowHandle -ne 0) {
            return $proc
        }
    }
    return $null
}

# Focus robuste : restaure si minimisé, met au premier plan, et VÉRIFIE que la
# fenêtre est bien au premier plan (plusieurs tentatives). Renvoie $true si OK.
function Focus-RiotWindow {
    param([System.Diagnostics.Process]$Process)

    if (-not $Process) { return $false }
    $h = $Process.MainWindowHandle
    if ($h -eq 0) { return $false }

    for ($i = 0; $i -lt 8; $i++) {
        if ([SmWin32]::IsIconic($h)) {
            [SmWin32]::ShowWindow($h, $SW_RESTORE) | Out-Null
        }
        [SmWin32]::SetForegroundWindow($h) | Out-Null
        try { (New-Object -ComObject WScript.Shell).AppActivate($Process.Id) | Out-Null } catch {}
        Start-Sleep -Milliseconds $SHORT_DELAY_MS
        if ([SmWin32]::GetForegroundWindow() -eq $h) { return $true }
    }
    return $false
}

# Attend que la fenêtre Riot Client soit disponible
function Wait-ForRiotWindow {
    for ($attempt = 0; $attempt -lt $FOCUS_MAX_ATTEMPTS; $attempt++) {
        $proc = Get-RiotWindow
        if ($proc) {
            return $proc
        }
        Start-Sleep -Milliseconds $FOCUS_POLL_INTERVAL_MS
    }
    return $null
}

# ========== MAIN EXECUTION ==========

# 1. Attendre et trouver la fenêtre
$proc = Wait-ForRiotWindow
if (-not $proc) {
    Write-Host "ERROR: Window not found"
    exit 1
}

# 2. Focus initial robuste + petit settle pour laisser le formulaire prendre le focus
Focus-RiotWindow -Process $proc | Out-Null
Start-Sleep -Milliseconds $MEDIUM_DELAY_MS

# 3. Username (re-focus juste avant pour garantir la cible) + Tab
Focus-RiotWindow -Process $proc | Out-Null
Set-SecureClipboard -Content $Username
Start-Sleep -Milliseconds $SHORT_DELAY_MS
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds $MEDIUM_DELAY_MS
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
[System.Windows.Forms.Clipboard]::Clear()

# 4. Petit délai entre les champs
Start-Sleep -Milliseconds $LONG_DELAY_MS

# 5. Password (re-focus au cas où le premier plan a bougé) + Enter
Focus-RiotWindow -Process $proc | Out-Null
Set-SecureClipboard -Content $Password
Start-Sleep -Milliseconds $SHORT_DELAY_MS
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds $MEDIUM_DELAY_MS
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

# 6. Nettoyage final sécurisé
Start-Sleep -Milliseconds $MEDIUM_DELAY_MS
[System.Windows.Forms.Clipboard]::Clear()

Write-Host "SUCCESS"
exit 0
