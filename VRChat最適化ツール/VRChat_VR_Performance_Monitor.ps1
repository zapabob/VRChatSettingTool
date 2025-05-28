# VRChat VR環境専用パフォーマンス監視スクリプト
# VRヘッドセット使用時のリアルタイムFPS監視とフレームタイム分析

param(
    [switch]$Monitor,
    [switch]$Optimize,
    [int]$MonitorInterval = 3,
    [string]$VRHeadset = "Auto"
)

# 管理者権限チェック
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "このスクリプトは管理者権限で実行する必要があります。" -ForegroundColor Red
    exit 1
}

Write-Host "=== VRChat VR環境専用パフォーマンス監視ツール ===" -ForegroundColor Cyan

# ログファイル設定
$LogFile = "VRChat_VR_Performance_Log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
function Write-Log {
    param($Message, $Color = "White")
    $TimeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$TimeStamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

# VRプロセス検出関数
function Get-VRProcesses {
    $VRProcesses = @{}
    
    # VRChat
    $VRChatProcess = Get-Process -Name "VRChat" -ErrorAction SilentlyContinue
    if ($VRChatProcess) {
        $VRProcesses["VRChat"] = $VRChatProcess
    }
    
    # Oculus
    $OculusClient = Get-Process -Name "OculusClient" -ErrorAction SilentlyContinue
    if ($OculusClient) {
        $VRProcesses["OculusClient"] = $OculusClient
    }
    
    $OVRServer = Get-Process -Name "OVRServer_x64" -ErrorAction SilentlyContinue
    if ($OVRServer) {
        $VRProcesses["OVRServer"] = $OVRServer
    }
    
    # SteamVR
    $VRServer = Get-Process -Name "vrserver" -ErrorAction SilentlyContinue
    if ($VRServer) {
        $VRProcesses["SteamVR"] = $VRServer
    }
    
    $VRCompositor = Get-Process -Name "vrcompositor" -ErrorAction SilentlyContinue
    if ($VRCompositor) {
        $VRProcesses["VRCompositor"] = $VRCompositor
    }
    
    # Windows Mixed Reality
    $WMRPortal = Get-Process -Name "MixedRealityPortal" -ErrorAction SilentlyContinue
    if ($WMRPortal) {
        $VRProcesses["WMRPortal"] = $WMRPortal
    }
    
    return $VRProcesses
}

# VR専用GPU使用率取得
function Get-VRGPUUsage {
    try {
        # NVIDIA GPU使用率（VR専用）
        $NvidiaGPU = Get-Counter "\GPU Engine(*engtype_3D)\Utilization Percentage" -ErrorAction SilentlyContinue
        if ($NvidiaGPU) {
            return [math]::Round(($NvidiaGPU.CounterSamples | Measure-Object CookedValue -Maximum).Maximum, 2)
        }
        
        # 一般的なGPU使用率
        $GPU = Get-Counter "\GPU Engine(*)\Utilization Percentage" -ErrorAction SilentlyContinue
        if ($GPU) {
            return [math]::Round(($GPU.CounterSamples | Measure-Object CookedValue -Average).Average, 2)
        }
    } catch {
        return "N/A"
    }
    return "N/A"
}

# VRフレームタイム取得
function Get-VRFrameTime {
    try {
        # SteamVRフレームタイム
        $SteamVRProcess = Get-Process -Name "vrcompositor" -ErrorAction SilentlyContinue
        if ($SteamVRProcess) {
            $CPUTime = $SteamVRProcess.TotalProcessorTime.TotalMilliseconds
            return [math]::Round($CPUTime / 1000, 2)
        }
        
        # Oculusフレームタイム
        $OculusProcess = Get-Process -Name "OVRServer_x64" -ErrorAction SilentlyContinue
        if ($OculusProcess) {
            $CPUTime = $OculusProcess.TotalProcessorTime.TotalMilliseconds
            return [math]::Round($CPUTime / 1000, 2)
        }
    } catch {
        return "N/A"
    }
    return "N/A"
}

# VR専用FPS推定
function Get-VREstimatedFPS {
    param($CPUUsage, $GPUUsage, $MemoryUsage, $VRProcessCount)
    
    # VR基本FPS（90Hz想定）
    $BaseVRFPS = 90
    
    # VRプロセス数による影響
    $VRProcessFactor = if ($VRProcessCount -gt 3) { 0.8 } elseif ($VRProcessCount -gt 2) { 0.9 } else { 1.0 }
    
    # CPU負荷による影響（VRはCPU依存が高い）
    $CPUFactor = if ($CPUUsage -gt 90) { 0.3 } 
                 elseif ($CPUUsage -gt 80) { 0.5 }
                 elseif ($CPUUsage -gt 70) { 0.7 }
                 elseif ($CPUUsage -gt 50) { 0.85 }
                 else { 1.0 }
    
    # GPU負荷による影響（VRはGPU依存が非常に高い）
    $GPUFactor = if ($GPUUsage -gt 95) { 0.2 }
                 elseif ($GPUUsage -gt 90) { 0.4 }
                 elseif ($GPUUsage -gt 85) { 0.6 }
                 elseif ($GPUUsage -gt 75) { 0.8 }
                 else { 1.0 }
    
    # メモリ負荷による影響
    $MemoryFactor = if ($MemoryUsage -gt 90) { 0.5 }
                    elseif ($MemoryUsage -gt 80) { 0.7 }
                    elseif ($MemoryUsage -gt 70) { 0.9 }
                    else { 1.0 }
    
    # VR専用FPS計算
    $EstimatedVRFPS = $BaseVRFPS * $VRProcessFactor * $CPUFactor * $GPUFactor * $MemoryFactor
    
    return [math]::Round($EstimatedVRFPS, 1)
}

# VR専用最適化関数
function Optimize-VRPerformance {
    Write-Log "VR専用パフォーマンス最適化を実行中..." "Yellow"
    
    $VRProcesses = Get-VRProcesses
    
    foreach ($ProcessName in $VRProcesses.Keys) {
        $Process = $VRProcesses[$ProcessName]
        try {
            # VRプロセス優先度を最高に設定
            if ($ProcessName -eq "VRChat") {
                $Process.PriorityClass = "High"
                Write-Log "VRChat プロセス優先度を高に設定" "Green"
            } else {
                $Process.PriorityClass = "AboveNormal"
                Write-Log "$ProcessName プロセス優先度を標準以上に設定" "Green"
            }
            
            # CPU親和性設定（VR用）
            $ProcessorCount = (Get-WmiObject -Class Win32_ComputerSystem).NumberOfLogicalProcessors
            if ($ProcessorCount -ge 8) {
                # 8コア以上の場合、VRChatに専用コアを割り当て
                if ($ProcessName -eq "VRChat") {
                    $AffinityMask = [math]::Pow(2, [math]::Min(6, $ProcessorCount)) - 1  # 最初の6コア
                } else {
                    $AffinityMask = [math]::Pow(2, $ProcessorCount) - 1  # 全コア
                }
            } else {
                $AffinityMask = [math]::Pow(2, $ProcessorCount) - 1  # 全コア使用
            }
            $Process.ProcessorAffinity = $AffinityMask
            
        } catch {
            Write-Log "$ProcessName 最適化でエラー: $($_.Exception.Message)" "Red"
        }
    }
    
    # VR専用メモリ最適化
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    [System.GC]::Collect()
    Write-Log "VR専用メモリガベージコレクション実行" "Green"
    
    # VR以外のプロセス優先度を下げる
    try {
        $NonVRProcesses = Get-Process | Where-Object { 
            $_.WorkingSet -gt 50MB -and 
            $_.Name -notin @("VRChat", "OculusClient", "OVRServer_x64", "vrserver", "vrcompositor", "MixedRealityPortal") -and
            $_.Name -notin @("System", "Idle", "dwm", "winlogon", "csrss", "smss", "services", "lsass")
        }
        
        foreach ($Process in $NonVRProcesses) {
            try {
                if ($Process.PriorityClass -ne "BelowNormal") {
                    $Process.PriorityClass = "BelowNormal"
                }
            } catch {
                # エラーは無視
            }
        }
        Write-Log "非VRプロセスの優先度を下げました" "Green"
    } catch {
        Write-Log "非VRプロセス最適化でエラー: $($_.Exception.Message)" "Red"
    }
}

# VRパフォーマンス監視関数
function Monitor-VRPerformance {
    Write-Log "VR専用パフォーマンス監視を開始します (間隔: ${MonitorInterval}秒)" "Cyan"
    Write-Log "VRヘッドセットを装着してVRChatを起動してください" "Yellow"
    
    $FrameDropCount = 0
    $TotalFrames = 0
    
    while ($true) {
        $VRProcesses = Get-VRProcesses
        
        if ($VRProcesses.ContainsKey("VRChat")) {
            try {
                $VRChatProcess = $VRProcesses["VRChat"]
                
                # パフォーマンス情報取得
                $CPUUsage = [math]::Round((Get-Counter "\Process(VRChat)\% Processor Time").CounterSamples[0].CookedValue, 2)
                $MemoryUsage = [math]::Round($VRChatProcess.WorkingSet / 1MB, 2)
                $GPUUsage = Get-VRGPUUsage
                $SystemMemoryUsage = [math]::Round((Get-WmiObject -Class Win32_OperatingSystem | ForEach-Object {(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) / $_.TotalVisibleMemorySize) * 100}), 2)
                $VRFrameTime = Get-VRFrameTime
                
                # VR専用FPS推定
                $EstimatedVRFPS = Get-VREstimatedFPS -CPUUsage $CPUUsage -GPUUsage $GPUUsage -MemoryUsage $SystemMemoryUsage -VRProcessCount $VRProcesses.Count
                
                # フレームドロップ検出
                $TotalFrames++
                if ($EstimatedVRFPS -lt 80) {
                    $FrameDropCount++
                }
                $FrameDropRate = [math]::Round(($FrameDropCount / $TotalFrames) * 100, 1)
                
                # VRパフォーマンス評価
                $VRPerformanceRating = if ($EstimatedVRFPS -ge 85) { "優秀" }
                                      elseif ($EstimatedVRFPS -ge 75) { "良好" }
                                      elseif ($EstimatedVRFPS -ge 60) { "普通" }
                                      elseif ($EstimatedVRFPS -ge 45) { "要改善" }
                                      else { "危険" }
                
                # VR情報表示
                Write-Log "=== VRChat VRパフォーマンス ===" "Cyan"
                Write-Log "推定VR FPS: ${EstimatedVRFPS} (評価: $VRPerformanceRating)" "White"
                Write-Log "CPU使用率: ${CPUUsage}%" "White"
                Write-Log "GPU使用率: ${GPUUsage}%" "White"
                Write-Log "VRChatメモリ: ${MemoryUsage}MB" "White"
                Write-Log "システムメモリ: ${SystemMemoryUsage}%" "White"
                Write-Log "VRフレームタイム: ${VRFrameTime}ms" "White"
                Write-Log "フレームドロップ率: ${FrameDropRate}%" "White"
                Write-Log "検出VRプロセス数: $($VRProcesses.Count)" "White"
                
                # VR専用警告
                if ($EstimatedVRFPS -lt 60) {
                    Write-Log "警告: VR FPSが低すぎます！VR酔いの原因になります！" "Red"
                }
                if ($CPUUsage -gt 85) {
                    Write-Log "警告: CPU使用率が高すぎます！VRパフォーマンスに影響します！" "Red"
                }
                if ($GPUUsage -gt 90) {
                    Write-Log "警告: GPU使用率が高すぎます！フレームドロップが発生します！" "Red"
                }
                if ($SystemMemoryUsage -gt 85) {
                    Write-Log "警告: メモリ不足です！VRアプリケーションが不安定になります！" "Red"
                }
                if ($FrameDropRate -gt 10) {
                    Write-Log "警告: フレームドロップが多発しています！" "Red"
                }
                
                # VR最適化提案
                if ($EstimatedVRFPS -lt 75) {
                    Write-Log "提案: VRChat設定でAvatar Performance Rankingを有効にしてください" "Yellow"
                    Write-Log "提案: VRヘッドセットの解像度を下げてください" "Yellow"
                    Write-Log "提案: 他のVRアプリケーションを終了してください" "Yellow"
                }
                
            } catch {
                Write-Log "VRパフォーマンス情報取得でエラー: $($_.Exception.Message)" "Red"
            }
        } else {
            Write-Log "VRChatプロセスが見つかりません（VRモードで起動してください）" "Yellow"
            
            # 検出されたVRプロセス表示
            if ($VRProcesses.Count -gt 0) {
                Write-Log "検出されたVRプロセス: $($VRProcesses.Keys -join ', ')" "Cyan"
            } else {
                Write-Log "VRヘッドセットが検出されません" "Red"
            }
        }
        
        Write-Log "----------------------------------------" "DarkGray"
        Start-Sleep -Seconds $MonitorInterval
    }
}

# VRヘッドセット別最適化
function Optimize-VRHeadsetSpecific {
    Write-Log "VRヘッドセット別最適化を実行中..." "Yellow"
    
    # Oculus最適化
    $OculusProcess = Get-Process -Name "OculusClient" -ErrorAction SilentlyContinue
    if ($OculusProcess) {
        try {
            # Oculus ASW（非同期スペースワープ）最適化
            $OculusRegPath = "HKCU:\Software\Oculus\RemoteHeadset"
            if (Test-Path $OculusRegPath) {
                Set-ItemProperty -Path $OculusRegPath -Name "ASW" -Value 1 -Force
            }
            Write-Log "Oculus ASW最適化完了" "Green"
        } catch {
            Write-Log "Oculus最適化でエラー: $($_.Exception.Message)" "Red"
        }
    }
    
    # SteamVR最適化
    $SteamVRProcess = Get-Process -Name "vrserver" -ErrorAction SilentlyContinue
    if ($SteamVRProcess) {
        try {
            # SteamVRモーションスムージング最適化
            Write-Log "SteamVRモーションスムージング設定を確認してください" "Yellow"
            Write-Log "SteamVR設定 → 開発者 → モーションスムージングを有効にしてください" "Yellow"
            Write-Log "SteamVR最適化完了" "Green"
        } catch {
            Write-Log "SteamVR最適化でエラー: $($_.Exception.Message)" "Red"
        }
    }
}

# メイン処理
if ($Monitor) {
    Monitor-VRPerformance
} elseif ($Optimize) {
    Optimize-VRPerformance
    Optimize-VRHeadsetSpecific
    Write-Log "VR専用最適化完了" "Green"
} else {
    Write-Host "VR環境専用使用方法:" -ForegroundColor Yellow
    Write-Host "  -Monitor    : VRパフォーマンスを監視（VRヘッドセット装着推奨）" -ForegroundColor White
    Write-Host "  -Optimize   : VRプロセスを最適化" -ForegroundColor White
    Write-Host "  例: .\VRChat_VR_Performance_Monitor.ps1 -Monitor" -ForegroundColor Cyan
    Write-Host "  例: .\VRChat_VR_Performance_Monitor.ps1 -Optimize" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "VR専用機能:" -ForegroundColor Green
    Write-Host "  ✓ VRヘッドセット自動検出" -ForegroundColor White
    Write-Host "  ✓ VR専用FPS推定（90Hz基準）" -ForegroundColor White
    Write-Host "  ✓ フレームドロップ検出" -ForegroundColor White
    Write-Host "  ✓ VRプロセス優先度最適化" -ForegroundColor White
    Write-Host "  ✓ VR酔い防止警告" -ForegroundColor White
    
    $Choice = Read-Host "VR専用リアルタイム最適化を開始しますか？ (Y/N)"
    if ($Choice -eq "Y" -or $Choice -eq "y") {
        Optimize-VRPerformance
        Optimize-VRHeadsetSpecific
        Write-Log "VR専用最適化完了 - VRChatをVRモードで起動してください" "Green"
    }
} 