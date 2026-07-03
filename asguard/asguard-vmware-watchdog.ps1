# Asguard VMware Watchdog - Windows Host
# Surveille la VM, alerte si elle ne repond plus ou si VMware detecte une panne critique.

# ── CONFIG ────────────────────────────────────────────────────────────────────
$VM_IP               = "192.168.229.220"
$VMX_PATH            = "D:\Virtual Machines\Asguard\Asguard.vmx"
$VMRUN_PATH          = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
$CHECK_EVERY         = 30
$FAIL_BEFORE_RESTART = 10
$STARTUP_WAIT        = 90

$EMAIL_FROM   = "asguard.watchdog.bot@gmail.com"  # compte bot dedie
$EMAIL_TO     = "daasala58@gmail.com"             # destinataire admin
$SMTP_SERVER  = "smtp.gmail.com"
$SMTP_PORT    = 587
$SMTP_USER    = "asguard.watchdog.bot@gmail.com"  # compte bot dedie
$SMTP_PASS    = "ieya vfgg yreb eurh"  # App Password du compte bot (16 caracteres)
$NTFY_TOPIC   = "asguard-ala-firewall-2024"  # optionnel: topic ntfy.sh pour alertes push instantanees
# ─────────────────────────────────────────────────────────────────────────────

$LogFile   = "$PSScriptRoot\asguard-watchdog.log"
$FailCount = 0
# Initialize to current log state so we don't react to old crash entries on startup
$LastFatalHint = (Get-Content -Path (Join-Path (Split-Path -Parent $VMX_PATH) "vmware.log") -Tail 220 -ErrorAction SilentlyContinue | Where-Object {
    $_ -match "CPU has been disabled|vcpu.*disabled|triple fault|kernel panic|Guest.*halted|PowerOff"
} | Select-Object -Last 1)

function Write-Log {
    param($msg)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Send-Alert {
    param($subject, $body)
    if ($NTFY_TOPIC) {
        try {
            Invoke-RestMethod -Method Post -Uri "https://ntfy.sh/$NTFY_TOPIC" -Body $body -Headers @{
                Title = "[Asguard] $subject"
                Priority = "urgent"
                Tags = "warning,rotating_light,computer"
            } | Out-Null
            Write-Log "Notification ntfy envoyee : $subject"
        } catch {
            Write-Log "Erreur ntfy : $_"
        }
    }
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

function Get-VMwareFatalHint {
    $vmDir = Split-Path -Parent $VMX_PATH
    $logPath = Join-Path $vmDir "vmware.log"
    if (-not (Test-Path $logPath)) { return "" }
    try {
        $recent = Get-Content -Path $logPath -Tail 220 -ErrorAction Stop
        $hit = $recent | Where-Object {
            $_ -match "CPU has been disabled" -or
            $_ -match "vcpu.*disabled" -or
            $_ -match "triple fault" -or
            $_ -match "kernel panic" -or
            $_ -match "Guest.*halted" -or
            $_ -match "PowerOff"
        } | Select-Object -Last 1
        return [string]$hit
    } catch {
        return ""
    }
}

function Get-ShutdownType {
    # Returns "user" if clean shutdown, "crash" if unexpected, "unknown" if can't determine
    $vmDir = Split-Path -Parent $VMX_PATH
    $logPath = Join-Path $vmDir "vmware.log"
    if (-not (Test-Path $logPath)) { return "unknown" }
    try {
        $recent = Get-Content -Path $logPath -Tail 300 -ErrorAction Stop
        # Crash indicators
        $isCrash = $recent | Where-Object {
            $_ -match "CPU has been disabled|vcpu.*disabled|triple fault|kernel panic|Guest.*halted"
        } | Select-Object -Last 1
        if ($isCrash) { return "crash" }
        # Clean shutdown indicators (user or guest OS shutdown)
        $isClean = $recent | Where-Object {
            $_ -match "Received power off|ACPI power off|Powering off|vmx.*power off|Tools.*power off|Shutdown.*requested|Guest requested"
        } | Select-Object -Last 1
        if ($isClean) { return "user" }
        return "unknown"
    } catch {
        return "unknown"
    }
}

function Check-VMwareFatalEvent {
    $fatalHint = Get-VMwareFatalHint

    if ($fatalHint -and $fatalHint -ne $script:LastFatalHint) {
        $script:LastFatalHint = $fatalHint
        $vmState = Get-VMState

        Write-Log "Evenement VMware critique detecte : $fatalHint"
        Send-Alert "Evenement critique VMware Asguard" "VMware a detecte un probleme critique sur la VM Asguard.`nEvenement : $fatalHint`nEtat VMware : $vmState`nIP surveillee : $VM_IP`nHeure : $(Get-Date)"

        # CPU disabled by guest OS (OOM/kernel panic) — notify only, no auto-restart
        if ($fatalHint -match "CPU has been disabled|vcpu.*disabled|triple fault|kernel panic") {
            Write-Log "CPU/kernel fatal detecte - notification envoyee (pas de redemarrage auto)."
            Send-Alert "VM Asguard - Crash critique (intervention requise)" "CPU desactive par le guest OS (OOM ou kernel panic).`nIntervention manuelle requise.`nEvenement : $fatalHint`nHeure : $(Get-Date)"
        }
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
    & "$VMRUN_PATH" start "$VMX_PATH" 2>$null
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
    Check-VMwareFatalEvent

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
        if ($FailCount -eq 1) {
            $vmState = Get-VMState
            $fatalHint = Get-VMwareFatalHint
            $riskBody = "RISQUE VM detecte.`nLa VM ($VM_IP) ne repond plus au ping.`nEtat VMware : $vmState.`nImpact probable : perte SSH/VS Code/API, services stoppes, VM suspendue, IP changee ou carte reseau deconnectee.`nIndice VMware : $fatalHint`nHeure : $(Get-Date)"
            Send-Alert "Risque VM Asguard - connectivite perdue" $riskBody
        }

        if ($FailCount -ge $FAIL_BEFORE_RESTART) {
            Write-Log "PANNE DETECTEE - verification avant action..."
            $vmState = Get-VMState
            Write-Log "Etat VM VMware : $vmState"
            $fatalHint = Get-VMwareFatalHint

            if ($vmState -eq "stopped") {
                $shutdownType = Get-ShutdownType
                if ($shutdownType -eq "user") {
                    Send-Alert "VM Asguard arretee par utilisateur" "La VM Asguard ($VM_IP) a ete arretee proprement par l'utilisateur.`nAucune action requise.`nHeure : $(Get-Date)"
                    Write-Log "VM arretee proprement par utilisateur - notification envoyee."
                } elseif ($shutdownType -eq "crash") {
                    Send-Alert "VM Asguard - CRASH detecte !" "La VM Asguard ($VM_IP) s'est arretee de facon inattendue (crash/kernel panic).`nIntervention manuelle requise.`nIndice VMware : $fatalHint`nHeure : $(Get-Date)"
                    Write-Log "VM arretee par CRASH - notification urgente envoyee."
                } else {
                    Send-Alert "VM Asguard arretee (cause inconnue)" "La VM Asguard ($VM_IP) est arretee. Cause indeterminee (arret volontaire ou panne).`nVerifiez VMware.`nHeure : $(Get-Date)"
                    Write-Log "VM arretee - cause inconnue, notification envoyee."
                }
            } elseif ($vmState -eq "running") {
                if ($fatalHint -match "CPU has been disabled|vcpu.*disabled|triple fault|kernel panic") {
                    Send-Alert "VM Asguard - Crash critique (intervention requise)" "La VM ($VM_IP) ne repond plus au ping et VMware signale CPU desactive ou kernel panic.`nIntervention manuelle requise.`nIndice VMware : $fatalHint`nHeure : $(Get-Date)"
                    Write-Log "VM running mais crash critique detecte - notification envoyee, pas de redemarrage auto."
                } else {
                    Send-Alert "VM Asguard non joignable" "La VM ($VM_IP) ne repond pas au ping mais VMware indique running.`nIndice VMware : $fatalHint`nHeure : $(Get-Date)"
                    Write-Log "VM encore running dans VMware - pas de redemarrage automatique."
                }
            } else {
                Send-Alert "Etat VM Asguard inconnu" "La VM ($VM_IP) ne repond pas au ping et l'etat VMware est inconnu.`nIndice VMware : $fatalHint`nHeure : $(Get-Date)"
                Write-Log "Etat VM inconnu - pas de redemarrage automatique."
            }

            $FailCount = 0
        }
    }

    Start-Sleep -Seconds $CHECK_EVERY
}
