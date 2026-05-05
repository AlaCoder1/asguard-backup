# Asguard VMware Watchdog - Windows Host
# Surveille la VM, redemarrage auto si elle ne repond plus.

# ── CONFIG ────────────────────────────────────────────────────────────────────
$VM_IP               = "192.168.229.220"
$VMX_PATH            = "C:\Users\USER\OneDrive\Documents\Virtual Machines\Asguard\Asguard.vmx"
$VMRUN_PATH          = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
$CHECK_EVERY         = 30
$FAIL_BEFORE_RESTART = 3
$STARTUP_WAIT        = 90

$EMAIL_FROM   = "asguard.watchdog.bot@gmail.com"  # compte bot dedie
$EMAIL_TO     = "daasala58@gmail.com"             # destinataire admin
$SMTP_SERVER  = "smtp.gmail.com"
$SMTP_PORT    = 587
$SMTP_USER    = "asguard.watchdog.bot@gmail.com"  # compte bot dedie
$SMTP_PASS    = ""  # App Password du compte bot (16 caracteres)
# ─────────────────────────────────────────────────────────────────────────────

$LogFile   = "$PSScriptRoot\asguard-watchdog.log"
$FailCount = 0

function Write-Log {
    param($msg)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Send-Alert {
    param($subject, $body)
    if (-not $EMAIL_FROM) { return }
    if (-not $SMTP_PASS)  { return }
    try {
        $secPass = ConvertTo-SecureString $SMTP_PASS -AsPlainText -Force
        $cred    = New-Object System.Management.Automation.PSCredential($SMTP_USER, $secPass)
        Send-MailMessage -From $EMAIL_FROM -To $EMAIL_TO -Subject "[Asguard] $subject" -Body $body -SmtpServer $SMTP_SERVER -Port $SMTP_PORT -UseSsl -Credential $cred -Encoding UTF8
        Write-Log "Email envoye : $subject"
    } catch {
        Write-Log "Erreur email : $_"
    }
}

function Get-VMState {
    if (-not (Test-Path $VMRUN_PATH)) {
        Write-Log "vmrun introuvable : $VMRUN_PATH"
        return "unknown"
    }
    $list = & "$VMRUN_PATH" list 2>$null
    foreach ($line in $list) {
        if ($line -like "*Asguard*") { return "running" }
    }
    return "stopped"
}

function Start-AsguardVM {
    Write-Log "Demarrage de la VM via vmrun..."
    & "$VMRUN_PATH" start "$VMX_PATH" nogui 2>$null
    Start-Sleep -Seconds $STARTUP_WAIT
}

function Restart-AsguardVM {
    Write-Log "Redemarrage force de la VM..."
    & "$VMRUN_PATH" stop "$VMX_PATH" hard 2>$null
    Start-Sleep -Seconds 5
    Start-AsguardVM
}

# ── Boucle principale ─────────────────────────────────────────────────────────
Write-Log "=== Asguard VMware Watchdog demarre (VM: $VM_IP) ==="

while ($true) {
    $pingOK = Test-Connection -ComputerName $VM_IP -Count 2 -Quiet -ErrorAction SilentlyContinue

    if ($pingOK) {
        if ($FailCount -gt 0) {
            Write-Log "VM Asguard de nouveau accessible (apres $FailCount echec(s))"
            Send-Alert "VM Asguard retablie" "La VM ($VM_IP) repond de nouveau. Heure : $(Get-Date)"
        }
        $FailCount = 0
    } else {
        $FailCount++
        Write-Log "Ping rate - tentative $FailCount / $FAIL_BEFORE_RESTART"

        if ($FailCount -ge $FAIL_BEFORE_RESTART) {
            Write-Log "PANNE DETECTEE - redemarrage automatique en cours..."
            $vmState = Get-VMState
            Write-Log "Etat VM VMware : $vmState"

            Send-Alert "VM Asguard tombee" "La VM ($VM_IP) ne repond plus. Etat VMware : $vmState. Redemarrage en cours. Heure : $(Get-Date)"

            if ($vmState -eq "running") {
                Restart-AsguardVM
            } else {
                Start-AsguardVM
            }

            $FailCount = 0
            Write-Log "VM redemarre - surveillance reprise"
        }
    }

    Start-Sleep -Seconds $CHECK_EVERY
}
