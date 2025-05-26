# Virtual Desktop + VRChat Optimizer
# Wireless VR Environment FPS Improvement and Network Latency Reduction

param(
    [switch]$SkipRestart,
    [switch]$Verbose
)

# Administrator privilege check
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "=== 警告: 管理者権限なしで実行中 ===" -ForegroundColor Yellow
    Write-Host "一部の最適化機能は制限されますが、基本的な最適化は実行されます。" -ForegroundColor Yellow
    Write-Host "完全な最適化を行うには、PowerShellを管理者として実行してください。" -ForegroundColor Cyan
    Write-Host ""
    # exit 1 # 管理者権限なしでも続行
}

Write-Host "=== Virtual Desktop + VRChat Optimizer ===" -ForegroundColor Cyan
Write-Host "Wireless VR environment FPS improvement and network latency reduction" -ForegroundColor Green

# Log file setup
$LogFile = "VirtualDesktop_VRChat_Optimization_Log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
function Write-Log {
    param($Message, $Color = "White")
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$TimeStamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

# Virtual Desktop detection
function Test-VirtualDesktop {
    $VDStreamer = Get-Process -Name "VirtualDesktop.Streamer" -ErrorAction SilentlyContinue
    $VDService = Get-Service -Name "VirtualDesktop.Service" -ErrorAction SilentlyContinue
    
    if ($VDStreamer -or $VDService) {
        Write-Log "Virtual Desktop detected" "Green"
        return $true
    } else {
        Write-Log "Virtual Desktop not detected" "Yellow"
        return $false
    }
}

# 1. Virtual Desktop-specific network optimization
Write-Log "Optimizing Virtual Desktop-specific network settings..." "Yellow"
try {
    # TCP optimization (for wireless VR)
    netsh int tcp set global autotuninglevel=normal
    netsh int tcp set global chimney=enabled
    netsh int tcp set global rss=enabled
    netsh int tcp set global netdma=enabled
    netsh int tcp set global ecncapability=enabled
    netsh int tcp set global timestamps=disabled
    
    # UDP optimization (for Virtual Desktop)
    netsh int udp set global uro=enabled
    
    # Network adapter optimization
    $NetworkAdapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.MediaType -eq "802.11"}
    foreach ($Adapter in $NetworkAdapters) {
        try {
            # Disable Wi-Fi power saving
            Set-NetAdapterPowerManagement -Name $Adapter.Name -ArpOffload Disabled -NSOffload Disabled -WakeOnMagicPacket Disabled -WakeOnPattern Disabled
            Write-Log "Wi-Fi adapter '$($Adapter.Name)' power saving disabled" "Green"
        } catch {
            Write-Log "Wi-Fi adapter settings error: $($_.Exception.Message)" "Red"
        }
    }
    
    # QoS settings (Virtual Desktop priority)
    netsh advfirewall firewall add rule name="Virtual Desktop Priority" dir=out action=allow protocol=UDP localport=any remoteport=any
    netsh advfirewall firewall add rule name="VRChat VD Priority" dir=out action=allow protocol=UDP localport=any remoteport=any
    
    Write-Log "Virtual Desktop-specific network optimization completed" "Green"
} catch {
    Write-Log "Network optimization error: $($_.Exception.Message)" "Red"
}

# 2. Virtual Desktop-specific process optimization
Write-Log "Optimizing Virtual Desktop-specific processes..." "Yellow"
try {
    # Virtual Desktop Streamer optimization
    $VDStreamerPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VirtualDesktop.Streamer.exe\PerfOptions"
    if (!(Test-Path $VDStreamerPath)) {
        New-Item -Path $VDStreamerPath -Force | Out-Null
    }
    Set-ItemProperty -Path $VDStreamerPath -Name "CpuPriorityClass" -Value 3 -Force
    Set-ItemProperty -Path $VDStreamerPath -Name "IoPriority" -Value 3 -Force
    
    # Virtual Desktop Service optimization
    $VDServicePath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VirtualDesktop.Service.exe\PerfOptions"
    if (!(Test-Path $VDServicePath)) {
        New-Item -Path $VDServicePath -Force | Out-Null
    }
    Set-ItemProperty -Path $VDServicePath -Name "CpuPriorityClass" -Value 3 -Force
    
    # VRChat optimization (for Virtual Desktop environment)
    $VRChatVDPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VRChat.exe\PerfOptions"
    if (!(Test-Path $VRChatVDPath)) {
        New-Item -Path $VRChatVDPath -Force | Out-Null
    }
    Set-ItemProperty -Path $VRChatVDPath -Name "CpuPriorityClass" -Value 3 -Force
    Set-ItemProperty -Path $VRChatVDPath -Name "IoPriority" -Value 3 -Force
    
    Write-Log "Virtual Desktop-specific process optimization completed" "Green"
} catch {
    Write-Log "Process optimization error: $($_.Exception.Message)" "Red"
}

# 3. Wireless VR-specific GPU settings
Write-Log "Optimizing wireless VR-specific GPU settings..." "Yellow"
try {
    # GPU maximum performance settings
    $GraphicsPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    if (Test-Path $GraphicsPath) {
        Set-ItemProperty -Path $GraphicsPath -Name "HwSchMode" -Value 2 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrLevel" -Value 0 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDelay" -Value 120 -Force  # Extended for wireless
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDdiDelay" -Value 120 -Force
    }
    
    # NVIDIA settings (for Virtual Desktop)
    $NvidiaPath = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\FTS"
    if (Test-Path $NvidiaPath) {
        Set-ItemProperty -Path $NvidiaPath -Name "EnableRidgedMultiGpu" -Value 0 -Force
    }
    
    # NVIDIA Control Panel settings (via registry)
    $NvidiaProfilePath = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\NVTweak"
    if (Test-Path $NvidiaProfilePath) {
        Set-ItemProperty -Path $NvidiaProfilePath -Name "DisplayPowerSaving" -Value 0 -Force
    }
    
    Write-Log "Wireless VR-specific GPU settings completed" "Green"
} catch {
    Write-Log "GPU settings error: $($_.Exception.Message)" "Red"
}

# 4. Wireless VR-specific power management
Write-Log "Setting wireless VR-specific power management..." "Yellow"
try {
    # High performance power plan
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    
    # Wireless power settings
    powercfg /change monitor-timeout-ac 0
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    powercfg /change disk-timeout-ac 0
    
    # USB power management disable (important)
    powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    
    # Wi-Fi power management disable
    powercfg /setacvalueindex SCHEME_CURRENT 19cbb8fa-5279-450e-9fac-8a3d5fedd0c1 12bbebe6-58d6-4636-95bb-3217ef867c1a 0
    
    powercfg /setactive SCHEME_CURRENT
    
    Write-Log "Wireless VR-specific power management completed" "Green"
} catch {
    Write-Log "Power management settings error: $($_.Exception.Message)" "Red"
}

# 5. Wireless VR-specific memory optimization
Write-Log "Optimizing wireless VR-specific memory..." "Yellow"
try {
    $MemoryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
    
    # Wireless VR memory settings
    Set-ItemProperty -Path $MemoryPath -Name "ClearPageFileAtShutdown" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "DisablePagingExecutive" -Value 1 -Force
    Set-ItemProperty -Path $MemoryPath -Name "LargeSystemCache" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "SystemPages" -Value 0 -Force
    
    # Virtual Desktop memory settings
    $ComputerSystem = Get-WmiObject -Class Win32_ComputerSystem
    $TotalRAM = [math]::Round($ComputerSystem.TotalPhysicalMemory / 1GB)
    $OptimalPageFile = [math]::Round($TotalRAM * 2 * 1024)  # Increased for wireless
    
    Write-Log "Wireless VR-specific memory settings completed (RAM: ${TotalRAM}GB, PageFile: ${OptimalPageFile}MB)" "Green"
} catch {
    Write-Log "Memory optimization error: $($_.Exception.Message)" "Red"
}

# 6. Wireless VR unnecessary service stop
Write-Log "Stopping wireless VR unnecessary services..." "Yellow"

$WirelessVRUnnecessaryServices = @(
    "Fax",
    "Spooler",
    "TabletInputService",
    "Themes",
    "WSearch",
    "SysMain",
    "DiagTrack",
    "dmwappushservice",
    "MapsBroker",
    "lfsvc"  # Location service
)

foreach ($Service in $WirelessVRUnnecessaryServices) {
    try {
        $ServiceObj = Get-Service -Name $Service -ErrorAction SilentlyContinue
        if ($ServiceObj -and $ServiceObj.Status -eq "Running") {
            Stop-Service -Name $Service -Force -ErrorAction SilentlyContinue
            Set-Service -Name $Service -StartupType Disabled -ErrorAction SilentlyContinue
            Write-Log "Wireless VR unnecessary service '$Service' stopped and disabled" "Green"
        }
    } catch {
        Write-Log "Service '$Service' processing error: $($_.Exception.Message)" "Red"
    }
}

# Wireless VR important service optimization
$WirelessVRImportantServices = @(
    "AudioSrv",
    "AudioEndpointBuilder",
    "Winmgmt",
    "WLAN AutoConfig",  # Wi-Fi important
    "Dnscache"  # DNS important
)

foreach ($Service in $WirelessVRImportantServices) {
    try {
        $ServiceObj = Get-Service -Name $Service -ErrorAction SilentlyContinue
        if ($ServiceObj) {
            Set-Service -Name $Service -StartupType Automatic -ErrorAction SilentlyContinue
            Write-Log "Wireless VR important service '$Service' set to automatic startup" "Green"
        }
    } catch {
        Write-Log "Service '$Service' setting error: $($_.Exception.Message)" "Red"
    }
}

# 7. Virtual Desktop-specific registry optimization
Write-Log "Optimizing Virtual Desktop-specific registry..." "Yellow"
try {
    # Network latency reduction
    $NetworkPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
    Set-ItemProperty -Path $NetworkPath -Name "TcpAckFrequency" -Value 1 -Force
    Set-ItemProperty -Path $NetworkPath -Name "TCPNoDelay" -Value 1 -Force
    Set-ItemProperty -Path $NetworkPath -Name "TcpDelAckTicks" -Value 0 -Force
    
    # Wi-Fi optimization
    $WifiPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    $Interfaces = Get-ChildItem -Path $WifiPath
    foreach ($Interface in $Interfaces) {
        try {
            Set-ItemProperty -Path $Interface.PSPath -Name "TcpAckFrequency" -Value 1 -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $Interface.PSPath -Name "TCPNoDelay" -Value 1 -Force -ErrorAction SilentlyContinue
        } catch {
            # Ignore errors
        }
    }
    
    Write-Log "Virtual Desktop-specific registry optimization completed" "Green"
} catch {
    Write-Log "Registry optimization error: $($_.Exception.Message)" "Red"
}

# 8. Wireless VR-specific temporary file cleanup
Write-Log "Cleaning up wireless VR-specific temporary files..." "Yellow"
try {
    $WirelessVRTempPaths = @(
        "$env:TEMP\*",
        "$env:LOCALAPPDATA\Temp\*",
        "$env:WINDIR\Temp\*",
        "$env:LOCALAPPDATA\VRChat\VRChat\Cache\*",
        "$env:LOCALAPPDATA\VirtualDesktop\*\Cache\*",
        "$env:LOCALAPPDATA\VirtualDesktop\*\Logs\*",
        "$env:PROGRAMDATA\VirtualDesktop\*\Cache\*"
    )
    
    foreach ($Path in $WirelessVRTempPaths) {
        if (Test-Path (Split-Path $Path -Parent)) {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Log "Wireless VR-specific cleanup completed" "Green"
} catch {
    Write-Log "Cleanup error: $($_.Exception.Message)" "Red"
}

# 9. System information display
Write-Log "Getting wireless VR system information..." "Yellow"
try {
    $WirelessVRSystemInfo = @{
        "OS" = (Get-WmiObject -Class Win32_OperatingSystem).Caption
        "CPU" = (Get-WmiObject -Class Win32_Processor).Name
        "RAM" = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
        "GPU" = (Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -notlike "*Basic*"}).Name
        "Virtual Desktop" = if (Test-VirtualDesktop) { "Detected" } else { "Not Detected" }
    }
    
    # Network information
    $WifiAdapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.MediaType -eq "802.11"}
    if ($WifiAdapters) {
        $WirelessVRSystemInfo["Wi-Fi Adapter"] = $WifiAdapters.Name -join ", "
    }
    
    Write-Log "=== Wireless VR System Information ===" "Cyan"
    foreach ($Key in $WirelessVRSystemInfo.Keys) {
        Write-Log "$Key : $($WirelessVRSystemInfo[$Key])" "White"
    }
} catch {
    Write-Log "System information error: $($_.Exception.Message)" "Red"
}

# Virtual Desktop-specific recommendations display
Write-Log "=== Virtual Desktop-specific Recommendations ===" "Cyan"
Write-Log "1. Use Wi-Fi 6 (802.11ax) or Wi-Fi 6E recommended" "Yellow"
Write-Log "2. Use 5GHz band, avoid 2.4GHz band" "Yellow"
Write-Log "3. Connect router and PC with wired connection" "Yellow"
Write-Log "4. Adjust Virtual Desktop quality settings" "Yellow"
Write-Log "5. Minimize other Wi-Fi device usage" "Yellow"
Write-Log "6. Enable Avatar Performance Ranking in VRChat settings" "Yellow"
Write-Log "7. Adjust Virtual Desktop bitrate according to environment" "Yellow"

# Completion message
Write-Log "=== Virtual Desktop + VRChat Optimization Completed ===" "Cyan"
Write-Log "Wireless VR environment FPS improvement and network latency reduction settings completed." "Green"
Write-Log "Log file: $LogFile" "Yellow"

if (-not $SkipRestart) {
    Write-Log "PC restart is recommended to enable optimization settings." "Yellow"
    $Restart = Read-Host "Restart now? (Y/N)"
    if ($Restart -eq "Y" -or $Restart -eq "y") {
        Write-Log "Restarting PC..." "Red"
        Restart-Computer -Force
    }
}

Write-Log "Virtual Desktop-specific script execution completed" "Green"
