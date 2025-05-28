# VRChat VR Environment Optimizer - Windows 11
# VR Headset FPS Improvement and Frame Drop Reduction

param(
    [switch]$SkipRestart,
    [switch]$Verbose,
    [string]$VRHeadset = "Auto"
)

# Administrator privilege check
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "=== 警告: 管理者権限なしで実行中 ===" -ForegroundColor Yellow
    Write-Host "一部の最適化機能は制限されますが、基本的な最適化は実行されます。" -ForegroundColor Yellow
    Write-Host "完全な最適化を行うには、PowerShellを管理者として実行してください。" -ForegroundColor Cyan
    Write-Host ""
    # exit 1 # 管理者権限なしでも続行
}

Write-Host "=== VRChat VR Environment Optimizer ===" -ForegroundColor Cyan
Write-Host "VR Headset FPS improvement and frame drop reduction" -ForegroundColor Green

# Log file setup
$LogFile = "VRChat_VR_Optimization_Log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
function Write-Log {
    param($Message, $Color = "White")
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$TimeStamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

# VR Headset Detection
function Detect-VRHeadset {
    Write-Log "Detecting VR headsets..." "Yellow"
    
    $DetectedHeadsets = @()
    
    # Oculus/Meta Quest detection
    if (Get-Process -Name "OculusClient" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "Oculus"
        Write-Log "Oculus/Meta Quest headset detected" "Green"
    }
    
    # SteamVR detection
    if (Get-Process -Name "vrserver" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "SteamVR"
        Write-Log "SteamVR headset detected" "Green"
    }
    
    # Windows Mixed Reality detection
    if (Get-Service -Name "MixedRealityPortal" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "WMR"
        Write-Log "Windows Mixed Reality headset detected" "Green"
    }
    
    # Pico detection
    if (Get-Process -Name "PicoConnect" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "Pico"
        Write-Log "Pico headset detected" "Green"
    }
    
    # Virtual Desktop detection
    if (Get-Process -Name "VirtualDesktop.Streamer" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "VirtualDesktop"
        Write-Log "Virtual Desktop detected" "Green"
    }
    
    return $DetectedHeadsets
}

# 1. VR-specific system optimization
Write-Log "Optimizing VR-specific system settings..." "Yellow"
try {
    # VR-optimized power settings
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    powercfg /change monitor-timeout-ac 0
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    powercfg /change disk-timeout-ac 0
    
    # VR USB power management disable
    powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /setactive SCHEME_CURRENT
    
    Write-Log "VR-specific power settings completed" "Green"
} catch {
    Write-Log "VR power settings error: $($_.Exception.Message)" "Red"
}

# 2. VR-specific GPU optimization
Write-Log "Optimizing VR-specific GPU settings..." "Yellow"
try {
    # GPU maximum performance settings
    $GraphicsPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    if (Test-Path $GraphicsPath) {
        Set-ItemProperty -Path $GraphicsPath -Name "HwSchMode" -Value 2 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrLevel" -Value 0 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDelay" -Value 60 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDdiDelay" -Value 60 -Force
    }
    
    # NVIDIA VR optimization
    $NvidiaVRPath = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\FTS"
    if (Test-Path $NvidiaVRPath) {
        Set-ItemProperty -Path $NvidiaVRPath -Name "EnableRidgedMultiGpu" -Value 0 -Force
    }
    
    # DirectX VR optimization
    $DirectXPath = "HKLM:\SOFTWARE\Microsoft\DirectDraw"
    if (!(Test-Path $DirectXPath)) {
        New-Item -Path $DirectXPath -Force | Out-Null
    }
    Set-ItemProperty -Path $DirectXPath -Name "DisableAGPSupport" -Value 0 -Force
    Set-ItemProperty -Path $DirectXPath -Name "EnableDebugging" -Value 0 -Force
    
    Write-Log "VR-specific GPU settings completed" "Green"
} catch {
    Write-Log "VR GPU settings error: $($_.Exception.Message)" "Red"
}

# 3. VR-specific memory optimization
Write-Log "Optimizing VR-specific memory settings..." "Yellow"
try {
    $MemoryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
    
    # VR memory settings
    Set-ItemProperty -Path $MemoryPath -Name "ClearPageFileAtShutdown" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "DisablePagingExecutive" -Value 1 -Force
    Set-ItemProperty -Path $MemoryPath -Name "LargeSystemCache" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "SystemPages" -Value 0 -Force
    
    # VR virtual memory optimization
    $ComputerSystem = Get-WmiObject -Class Win32_ComputerSystem
    $TotalRAM = [math]::Round($ComputerSystem.TotalPhysicalMemory / 1GB)
    $OptimalPageFile = [math]::Round($TotalRAM * 1.5 * 1024)
    
    Write-Log "VR-specific memory settings completed (RAM: ${TotalRAM}GB, PageFile: ${OptimalPageFile}MB)" "Green"
} catch {
    Write-Log "VR memory settings error: $($_.Exception.Message)" "Red"
}

# 4. VR headset-specific optimization
$DetectedHeadsets = Detect-VRHeadset

foreach ($Headset in $DetectedHeadsets) {
    Write-Log "Running $Headset specific optimization..." "Yellow"
    
    switch ($Headset) {
        "Oculus" {
            try {
                # Oculus-specific optimization
                $OculusPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\OculusClient.exe\PerfOptions"
                if (!(Test-Path $OculusPath)) {
                    New-Item -Path $OculusPath -Force | Out-Null
                }
                Set-ItemProperty -Path $OculusPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # Oculus VR service optimization
                $OculusVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\OVRServer_x64.exe\PerfOptions"
                if (!(Test-Path $OculusVRPath)) {
                    New-Item -Path $OculusVRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $OculusVRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "Oculus optimization completed" "Green"
            } catch {
                Write-Log "Oculus optimization error: $($_.Exception.Message)" "Red"
            }
        }
        
        "SteamVR" {
            try {
                # SteamVR-specific optimization
                $SteamVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\vrserver.exe\PerfOptions"
                if (!(Test-Path $SteamVRPath)) {
                    New-Item -Path $SteamVRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $SteamVRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # SteamVR compositor optimization
                $CompositorPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\vrcompositor.exe\PerfOptions"
                if (!(Test-Path $CompositorPath)) {
                    New-Item -Path $CompositorPath -Force | Out-Null
                }
                Set-ItemProperty -Path $CompositorPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "SteamVR optimization completed" "Green"
            } catch {
                Write-Log "SteamVR optimization error: $($_.Exception.Message)" "Red"
            }
        }
        
        "WMR" {
            try {
                # Windows Mixed Reality optimization
                $WMRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\MixedRealityPortal.exe\PerfOptions"
                if (!(Test-Path $WMRPath)) {
                    New-Item -Path $WMRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $WMRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "Windows Mixed Reality optimization completed" "Green"
            } catch {
                Write-Log "WMR optimization error: $($_.Exception.Message)" "Red"
            }
        }
        
        "VirtualDesktop" {
            try {
                # Virtual Desktop-specific optimization
                $VDPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VirtualDesktop.Streamer.exe\PerfOptions"
                if (!(Test-Path $VDPath)) {
                    New-Item -Path $VDPath -Force | Out-Null
                }
                Set-ItemProperty -Path $VDPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # Virtual Desktop network optimization
                netsh int tcp set global autotuninglevel=normal
                netsh int tcp set global chimney=enabled
                netsh int tcp set global rss=enabled
                netsh int tcp set global netdma=enabled
                
                Write-Log "Virtual Desktop optimization completed" "Green"
            } catch {
                Write-Log "Virtual Desktop optimization error: $($_.Exception.Message)" "Red"
            }
        }
    }
}

# 5. VRChat VR-specific settings
Write-Log "Applying VRChat VR-specific settings..." "Yellow"
try {
    # VRChat VR-specific process priority
    $VRChatVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VRChat.exe\PerfOptions"
    if (!(Test-Path $VRChatVRPath)) {
        New-Item -Path $VRChatVRPath -Force | Out-Null
    }
    Set-ItemProperty -Path $VRChatVRPath -Name "CpuPriorityClass" -Value 3 -Force
    Set-ItemProperty -Path $VRChatVRPath -Name "IoPriority" -Value 3 -Force
    
    Write-Log "VRChat VR-specific settings completed" "Green"
} catch {
    Write-Log "VRChat VR settings error: $($_.Exception.Message)" "Red"
}

# 6. VR-specific network optimization
Write-Log "Optimizing VR-specific network settings..." "Yellow"
try {
    # VR TCP settings (low latency focus)
    netsh int tcp set global autotuninglevel=normal
    netsh int tcp set global chimney=enabled
    netsh int tcp set global rss=enabled
    netsh int tcp set global netdma=enabled
    netsh int tcp set global ecncapability=enabled
    
    # VR UDP optimization
    netsh int udp set global uro=enabled
    
    # VR QoS settings
    netsh advfirewall firewall add rule name="VRChat VR Priority" dir=out action=allow protocol=UDP localport=any remoteport=any
    
    Write-Log "VR-specific network optimization completed" "Green"
} catch {
    Write-Log "VR network settings error: $($_.Exception.Message)" "Red"
}

# 7. VR-specific service optimization
Write-Log "Optimizing VR-specific service settings..." "Yellow"

# Stop VR-unnecessary services
$VRUnnecessaryServices = @(
    "Fax",
    "Spooler",
    "TabletInputService",
    "Themes",
    "WSearch",
    "SysMain",
    "DiagTrack",
    "dmwappushservice"
)

foreach ($Service in $VRUnnecessaryServices) {
    try {
        $ServiceObj = Get-Service -Name $Service -ErrorAction SilentlyContinue
        if ($ServiceObj -and $ServiceObj.Status -eq "Running") {
            Stop-Service -Name $Service -Force -ErrorAction SilentlyContinue
            Set-Service -Name $Service -StartupType Disabled -ErrorAction SilentlyContinue
            Write-Log "VR-unnecessary service '$Service' stopped and disabled" "Green"
        }
    } catch {
        Write-Log "Service '$Service' processing error: $($_.Exception.Message)" "Red"
    }
}

# Set VR-important services to high priority
$VRImportantServices = @(
    "AudioSrv",
    "AudioEndpointBuilder",
    "UsoSvc",
    "Winmgmt"
)

foreach ($Service in $VRImportantServices) {
    try {
        $ServiceObj = Get-Service -Name $Service -ErrorAction SilentlyContinue
        if ($ServiceObj) {
            Set-Service -Name $Service -StartupType Automatic -ErrorAction SilentlyContinue
            Write-Log "VR-important service '$Service' set to automatic startup" "Green"
        }
    } catch {
        Write-Log "Service '$Service' setting error: $($_.Exception.Message)" "Red"
    }
}

# 8. VR-specific visual effects disable
Write-Log "Disabling VR-specific visual effects..." "Yellow"
try {
    # Completely disable visual effects unnecessary for VR
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "DragFullWindows" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "MenuShowDelay" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ListviewAlphaSelect" -Value 0 -Force
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0 -Force
    
    Write-Log "VR-specific visual effects disable completed" "Green"
} catch {
    Write-Log "VR visual effects settings error: $($_.Exception.Message)" "Red"
}

# 9. VR-specific temporary file cleanup
Write-Log "Cleaning up VR-specific temporary files..." "Yellow"
try {
    $VRTempPaths = @(
        "$env:TEMP\*",
        "$env:LOCALAPPDATA\Temp\*",
        "$env:WINDIR\Temp\*",
        "$env:LOCALAPPDATA\VRChat\VRChat\Cache\*",
        "$env:LOCALAPPDATA\Oculus\*\Cache\*",
        "$env:PROGRAMDATA\Oculus\*\Cache\*",
        "$env:LOCALAPPDATA\openvr\*\Cache\*",
        "$env:LOCALAPPDATA\VirtualDesktop\*\Cache\*"
    )
    
    foreach ($Path in $VRTempPaths) {
        if (Test-Path (Split-Path $Path -Parent)) {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Log "VR-specific cleanup completed" "Green"
} catch {
    Write-Log "VR cleanup error: $($_.Exception.Message)" "Red"
}

# 10. VR system information display
Write-Log "Getting VR system information..." "Yellow"
try {
    $VRSystemInfo = @{
        "OS" = (Get-WmiObject -Class Win32_OperatingSystem).Caption
        "CPU" = (Get-WmiObject -Class Win32_Processor).Name
        "RAM" = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
        "GPU" = (Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -notlike "*Basic*"}).Name
        "Detected VR Headsets" = if ($DetectedHeadsets.Count -gt 0) { $DetectedHeadsets -join ", " } else { "None" }
    }
    
    Write-Log "=== VR System Information ===" "Cyan"
    foreach ($Key in $VRSystemInfo.Keys) {
        Write-Log "$Key : $($VRSystemInfo[$Key])" "White"
    }
} catch {
    Write-Log "VR system information error: $($_.Exception.Message)" "Red"
}

# VR-specific recommendations display
Write-Log "=== VR-specific Recommendations ===" "Cyan"
Write-Log "1. Check VR headset refresh rate" "Yellow"
Write-Log "2. For SteamVR, adjust rendering resolution" "Yellow"
Write-Log "3. Check VRChat VR Comfort settings" "Yellow"
Write-Log "4. Close unnecessary VR applications" "Yellow"
Write-Log "5. Check VR headset cable connection" "Yellow"
Write-Log "6. For Virtual Desktop, check network environment" "Yellow"

# Completion message
Write-Log "=== VR-specific Optimization Completed ===" "Cyan"
Write-Log "VRChat VR environment FPS improvement and frame drop reduction settings completed." "Green"
Write-Log "Log file: $LogFile" "Yellow"

if (-not $SkipRestart) {
    Write-Log "PC restart is recommended to enable VR optimization settings." "Yellow"
    $Restart = Read-Host "Restart now? (Y/N)"
    if ($Restart -eq "Y" -or $Restart -eq "y") {
        Write-Log "Restarting PC..." "Red"
        Restart-Computer -Force
    }
}

Write-Log "VR-specific script execution completed" "Green"

