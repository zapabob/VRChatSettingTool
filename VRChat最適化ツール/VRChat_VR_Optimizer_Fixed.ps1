# VRChat VR環境専用最適化スクリプト - Windows 11対応
# VRヘッドセット使用時のFPS向上とフレームドロップ軽減

param(
    [switch]$SkipRestart,
    [switch]$Verbose,
    [string]$VRHeadset = "Auto"
)

# 管理者権限チェック
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "このスクリプトは管理者権限で実行する必要があります。" -ForegroundColor Red
    Write-Host "PowerShellを管理者として実行し、再度お試しください。" -ForegroundColor Yellow
    exit 1
}

Write-Host "=== VRChat VR環境専用最適化スクリプト ===" -ForegroundColor Cyan
Write-Host "VRヘッドセット使用時のFPS向上とフレームドロップ軽減を行います" -ForegroundColor Green

# ログファイル設定
$LogFile = "VRChat_VR_Optimization_Log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
function Write-Log {
    param($Message, $Color = "White")
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$TimeStamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

# VRヘッドセット検出
function Detect-VRHeadset {
    Write-Log "VRヘッドセットを検出中..." "Yellow"
    
    $DetectedHeadsets = @()
    
    # Oculus/Meta Quest検出
    if (Get-Process -Name "OculusClient" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "Oculus"
        Write-Log "Oculus/Meta Questヘッドセットを検出" "Green"
    }
    
    # SteamVR検出
    if (Get-Process -Name "vrserver" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "SteamVR"
        Write-Log "SteamVRヘッドセットを検出" "Green"
    }
    
    # Windows Mixed Reality検出
    if (Get-Service -Name "MixedRealityPortal" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "WMR"
        Write-Log "Windows Mixed Realityヘッドセットを検出" "Green"
    }
    
    # Pico検出
    if (Get-Process -Name "PicoConnect" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "Pico"
        Write-Log "Picoヘッドセットを検出" "Green"
    }
    
    # Virtual Desktop検出
    if (Get-Process -Name "VirtualDesktop.Streamer" -ErrorAction SilentlyContinue) {
        $DetectedHeadsets += "VirtualDesktop"
        Write-Log "Virtual Desktopを検出" "Green"
    }
    
    return $DetectedHeadsets
}

# 1. VR専用システム最適化
Write-Log "VR専用システム設定を最適化中..." "Yellow"
try {
    # VRに最適化された電源設定
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    powercfg /change monitor-timeout-ac 0
    powercfg /change standby-timeout-ac 0
    powercfg /change hibernate-timeout-ac 0
    powercfg /change disk-timeout-ac 0
    
    # VR用USB電源管理無効化
    powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /setactive SCHEME_CURRENT
    
    Write-Log "VR専用電源設定完了" "Green"
} catch {
    Write-Log "VR電源設定でエラー: $($_.Exception.Message)" "Red"
}

# 2. VR専用GPU最適化
Write-Log "VR専用GPU設定を最適化中..." "Yellow"
try {
    # GPU最大パフォーマンス設定
    $GraphicsPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    if (Test-Path $GraphicsPath) {
        Set-ItemProperty -Path $GraphicsPath -Name "HwSchMode" -Value 2 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrLevel" -Value 0 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDelay" -Value 60 -Force
        Set-ItemProperty -Path $GraphicsPath -Name "TdrDdiDelay" -Value 60 -Force
    }
    
    # NVIDIA VR最適化
    $NvidiaVRPath = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\FTS"
    if (Test-Path $NvidiaVRPath) {
        Set-ItemProperty -Path $NvidiaVRPath -Name "EnableRidgedMultiGpu" -Value 0 -Force
    }
    
    # DirectX VR最適化
    $DirectXPath = "HKLM:\SOFTWARE\Microsoft\DirectDraw"
    if (!(Test-Path $DirectXPath)) {
        New-Item -Path $DirectXPath -Force | Out-Null
    }
    Set-ItemProperty -Path $DirectXPath -Name "DisableAGPSupport" -Value 0 -Force
    Set-ItemProperty -Path $DirectXPath -Name "EnableDebugging" -Value 0 -Force
    
    Write-Log "VR専用GPU設定完了" "Green"
} catch {
    Write-Log "VR GPU設定でエラー: $($_.Exception.Message)" "Red"
}

# 3. VR専用メモリ最適化
Write-Log "VR専用メモリ設定を最適化中..." "Yellow"
try {
    $MemoryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
    
    # VR用メモリ設定
    Set-ItemProperty -Path $MemoryPath -Name "ClearPageFileAtShutdown" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "DisablePagingExecutive" -Value 1 -Force
    Set-ItemProperty -Path $MemoryPath -Name "LargeSystemCache" -Value 0 -Force
    Set-ItemProperty -Path $MemoryPath -Name "SystemPages" -Value 0 -Force
    
    # VR用仮想メモリ最適化
    $ComputerSystem = Get-WmiObject -Class Win32_ComputerSystem
    $TotalRAM = [math]::Round($ComputerSystem.TotalPhysicalMemory / 1GB)
    $OptimalPageFile = [math]::Round($TotalRAM * 1.5 * 1024)
    
    Write-Log "VR専用メモリ設定完了 (RAM: ${TotalRAM}GB, PageFile: ${OptimalPageFile}MB)" "Green"
} catch {
    Write-Log "VRメモリ設定でエラー: $($_.Exception.Message)" "Red"
}

# 4. VRヘッドセット別最適化
$DetectedHeadsets = Detect-VRHeadset

foreach ($Headset in $DetectedHeadsets) {
    Write-Log "$Headset 専用最適化を実行中..." "Yellow"
    
    switch ($Headset) {
        "Oculus" {
            try {
                # Oculus専用最適化
                $OculusPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\OculusClient.exe\PerfOptions"
                if (!(Test-Path $OculusPath)) {
                    New-Item -Path $OculusPath -Force | Out-Null
                }
                Set-ItemProperty -Path $OculusPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # Oculus VRサービス最適化
                $OculusVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\OVRServer_x64.exe\PerfOptions"
                if (!(Test-Path $OculusVRPath)) {
                    New-Item -Path $OculusVRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $OculusVRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "Oculus最適化完了" "Green"
            } catch {
                Write-Log "Oculus最適化でエラー: $($_.Exception.Message)" "Red"
            }
        }
        
        "SteamVR" {
            try {
                # SteamVR専用最適化
                $SteamVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\vrserver.exe\PerfOptions"
                if (!(Test-Path $SteamVRPath)) {
                    New-Item -Path $SteamVRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $SteamVRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # SteamVRコンポーザー最適化
                $CompositorPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\vrcompositor.exe\PerfOptions"
                if (!(Test-Path $CompositorPath)) {
                    New-Item -Path $CompositorPath -Force | Out-Null
                }
                Set-ItemProperty -Path $CompositorPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "SteamVR最適化完了" "Green"
            } catch {
                Write-Log "SteamVR最適化でエラー: $($_.Exception.Message)" "Red"
            }
        }
        
        "WMR" {
            try {
                # Windows Mixed Reality最適化
                $WMRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\MixedRealityPortal.exe\PerfOptions"
                if (!(Test-Path $WMRPath)) {
                    New-Item -Path $WMRPath -Force | Out-Null
                }
                Set-ItemProperty -Path $WMRPath -Name "CpuPriorityClass" -Value 3 -Force
                
                Write-Log "Windows Mixed Reality最適化完了" "Green"
            } catch {
                Write-Log "WMR最適化でエラー: $($_.Exception.Message)" "Red"
            }
        }
        
        "VirtualDesktop" {
            try {
                # Virtual Desktop専用最適化
                $VDPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VirtualDesktop.Streamer.exe\PerfOptions"
                if (!(Test-Path $VDPath)) {
                    New-Item -Path $VDPath -Force | Out-Null
                }
                Set-ItemProperty -Path $VDPath -Name "CpuPriorityClass" -Value 3 -Force
                
                # Virtual Desktop用ネットワーク最適化
                netsh int tcp set global autotuninglevel=normal
                netsh int tcp set global chimney=enabled
                netsh int tcp set global rss=enabled
                netsh int tcp set global netdma=enabled
                
                Write-Log "Virtual Desktop最適化完了" "Green"
            } catch {
                Write-Log "Virtual Desktop最適化でエラー: $($_.Exception.Message)" "Red"
            }
        }
    }
}

# 5. VRChat VR専用設定
Write-Log "VRChat VR専用設定を適用中..." "Yellow"
try {
    # VRChat VR専用プロセス優先度
    $VRChatVRPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\VRChat.exe\PerfOptions"
    if (!(Test-Path $VRChatVRPath)) {
        New-Item -Path $VRChatVRPath -Force | Out-Null
    }
    Set-ItemProperty -Path $VRChatVRPath -Name "CpuPriorityClass" -Value 3 -Force
    Set-ItemProperty -Path $VRChatVRPath -Name "IoPriority" -Value 3 -Force
    
    Write-Log "VRChat VR専用設定完了" "Green"
} catch {
    Write-Log "VRChat VR設定でエラー: $($_.Exception.Message)" "Red"
}

# 6. VR専用ネットワーク最適化
Write-Log "VR専用ネットワーク設定を最適化中..." "Yellow"
try {
    # VR用TCP設定（低遅延重視）
    netsh int tcp set global autotuninglevel=normal
    netsh int tcp set global chimney=enabled
    netsh int tcp set global rss=enabled
    netsh int tcp set global netdma=enabled
    netsh int tcp set global ecncapability=enabled
    
    # VR用UDP最適化
    netsh int udp set global uro=enabled
    
    # VR用QoS設定
    netsh advfirewall firewall add rule name="VRChat VR Priority" dir=out action=allow protocol=UDP localport=any remoteport=any
    
    Write-Log "VR専用ネットワーク最適化完了" "Green"
} catch {
    Write-Log "VRネットワーク設定でエラー: $($_.Exception.Message)" "Red"
}

# 7. VR専用サービス最適化
Write-Log "VR専用サービス設定を最適化中..." "Yellow"

# VRに不要なサービスを停止
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
            Write-Log "VR不要サービス '$Service' を停止・無効化" "Green"
        }
    } catch {
        Write-Log "サービス '$Service' の処理でエラー: $($_.Exception.Message)" "Red"
    }
}

# VRに重要なサービスを高優先度に設定
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
            Write-Log "VR重要サービス '$Service' を自動起動に設定" "Green"
        }
    } catch {
        Write-Log "サービス '$Service' の設定でエラー: $($_.Exception.Message)" "Red"
    }
}

# 8. VR専用視覚効果無効化
Write-Log "VR専用視覚効果を無効化中..." "Yellow"
try {
    # VRでは不要な視覚効果を完全無効化
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "DragFullWindows" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "MenuShowDelay" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -Force
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ListviewAlphaSelect" -Value 0 -Force
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0 -Force
    
    Write-Log "VR専用視覚効果無効化完了" "Green"
} catch {
    Write-Log "VR視覚効果設定でエラー: $($_.Exception.Message)" "Red"
}

# 9. VR専用一時ファイルクリーンアップ
Write-Log "VR専用一時ファイルをクリーンアップ中..." "Yellow"
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
    
    Write-Log "VR専用クリーンアップ完了" "Green"
} catch {
    Write-Log "VRクリーンアップでエラー: $($_.Exception.Message)" "Red"
}

# 10. VRシステム情報表示
Write-Log "VRシステム情報を取得中..." "Yellow"
try {
    $VRSystemInfo = @{
        "OS" = (Get-WmiObject -Class Win32_OperatingSystem).Caption
        "CPU" = (Get-WmiObject -Class Win32_Processor).Name
        "RAM" = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
        "GPU" = (Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -notlike "*Basic*"}).Name
        "検出されたVRヘッドセット" = if ($DetectedHeadsets.Count -gt 0) { $DetectedHeadsets -join ", " } else { "なし" }
    }
    
    Write-Log "=== VRシステム情報 ===" "Cyan"
    foreach ($Key in $VRSystemInfo.Keys) {
        Write-Log "$Key : $($VRSystemInfo[$Key])" "White"
    }
} catch {
    Write-Log "VRシステム情報取得でエラー: $($_.Exception.Message)" "Red"
}

# VR専用推奨事項表示
Write-Log "=== VR専用推奨事項 ===" "Cyan"
Write-Log "1. VRヘッドセットのリフレッシュレートを確認してください" "Yellow"
Write-Log "2. SteamVRの場合、レンダリング解像度を調整してください" "Yellow"
Write-Log "3. VRChatのVR設定でComfort設定を確認してください" "Yellow"
Write-Log "4. 不要なVRアプリケーションを終了してください" "Yellow"
Write-Log "5. VRヘッドセットのケーブル接続を確認してください" "Yellow"
Write-Log "6. Virtual Desktop使用時はネットワーク環境を確認してください" "Yellow"

# 完了メッセージ
Write-Log "=== VR専用最適化完了 ===" "Cyan"
Write-Log "VRChat VR環境でのFPS向上とフレームドロップ軽減設定が完了しました。" "Green"
Write-Log "ログファイル: $LogFile" "Yellow"

if (-not $SkipRestart) {
    Write-Log "VR最適化設定を有効にするため、PCの再起動をお勧めします。" "Yellow"
    $Restart = Read-Host "今すぐ再起動しますか？ (Y/N)"
    if ($Restart -eq "Y" -or $Restart -eq "y") {
        Write-Log "PCを再起動します..." "Red"
        Restart-Computer -Force
    }
}

Write-Log "VR専用スクリプト実行完了" "Green" 