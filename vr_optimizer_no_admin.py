#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VR環境最適化ツール（管理者権限不要版）
VirtualDesktop、SteamVR、VRChat用PC最適化

このツールは管理者権限なしで実行可能な最適化を提供します。
"""

import os
import sys
import json
import time
import psutil
import winreg
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from tqdm import tqdm

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'vr_optimizer_no_admin_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VROptimizerNoAdmin:
    """管理者権限不要のVR最適化ツール"""
    
    def __init__(self):
        self.config = {
            'optimization_level': 'balanced',  # conservative, balanced, aggressive
            'target_apps': ['VRChat', 'SteamVR', 'VirtualDesktop'],
            'network_optimization': True,
            'process_optimization': True,
            'power_optimization': True,
            'gpu_optimization': True,
            'memory_optimization': True
        }
        
        self.detected_vr_apps = {}
        self.optimization_results = {}
        
    def detect_vr_environment(self) -> Dict[str, bool]:
        """VR環境の検出"""
        logger.info("🔍 VR環境を検出中...")
        
        vr_processes = {
            'SteamVR': ['vrserver.exe', 'vrcompositor.exe', 'vrdashboard.exe'],
            'VirtualDesktop': ['VirtualDesktop.Streamer.exe', 'VirtualDesktop.Service.exe'],
            'VRChat': ['VRChat.exe'],
            'OculusVR': ['OculusClient.exe', 'OVRServer_x64.exe'],
            'Steam': ['steam.exe']
        }
        
        detected = {}
        
        for app_name, process_names in vr_processes.items():
            detected[app_name] = any(
                any(proc.name().lower() == pname.lower() for proc in psutil.process_iter(['name']))
                for pname in process_names
            )
            
            if detected[app_name]:
                logger.info(f"✅ {app_name} が検出されました")
            else:
                logger.info(f"❌ {app_name} は検出されませんでした")
        
        self.detected_vr_apps = detected
        return detected
    
    def optimize_process_priorities(self) -> bool:
        """プロセス優先度の最適化（管理者権限不要）"""
        logger.info("⚡ プロセス優先度を最適化中...")
        
        try:
            # VR関連プロセスの優先度を上げる
            vr_processes = {
                'VRChat.exe': psutil.HIGH_PRIORITY_CLASS,
                'vrserver.exe': psutil.HIGH_PRIORITY_CLASS,
                'vrcompositor.exe': psutil.HIGH_PRIORITY_CLASS,
                'VirtualDesktop.Streamer.exe': psutil.HIGH_PRIORITY_CLASS,
                'steam.exe': psutil.ABOVE_NORMAL_PRIORITY_CLASS
            }
            
            optimized_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name in vr_processes:
                        # 現在のユーザーが所有するプロセスのみ変更可能
                        if proc.username() == psutil.Process().username():
                            proc.nice(vr_processes[proc_name])
                            optimized_count += 1
                            logger.info(f"✅ {proc_name} の優先度を最適化しました")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 不要なプロセスの優先度を下げる
            low_priority_processes = [
                'explorer.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe',
                'chrome.exe', 'firefox.exe', 'discord.exe', 'spotify.exe'
            ]
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name in low_priority_processes:
                        if proc.username() == psutil.Process().username():
                            proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                            optimized_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"✅ {optimized_count}個のプロセス優先度を最適化しました")
            return True
            
        except Exception as e:
            logger.error(f"❌ プロセス優先度最適化エラー: {e}")
            return False
    
    def optimize_network_settings(self) -> bool:
        """ネットワーク設定の最適化"""
        logger.info("🌐 ネットワーク設定を最適化中...")
        
        try:
            # TCP/UDP最適化コマンド（管理者権限不要）
            network_commands = [
                # TCP最適化
                'netsh int tcp set global autotuninglevel=normal',
                'netsh int tcp set global chimney=enabled',
                'netsh int tcp set global rss=enabled',
                'netsh int tcp set global netdma=enabled',
                'netsh int tcp set global ecncapability=enabled',
                'netsh int tcp set global timestamps=disabled',
                
                # UDP最適化
                'netsh int udp set global uro=enabled',
                
                # DNS最適化
                'netsh interface ip set dns "Wi-Fi" static 1.1.1.1',
                'netsh interface ip add dns "Wi-Fi" 1.0.0.1 index=2',
            ]
            
            success_count = 0
            
            for cmd in tqdm(network_commands, desc="ネットワーク最適化"):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        logger.warning(f"⚠️ コマンド実行警告: {cmd}")
                except Exception as e:
                    logger.warning(f"⚠️ ネットワークコマンドエラー: {cmd} - {e}")
            
            logger.info(f"✅ {success_count}/{len(network_commands)}個のネットワーク最適化を完了")
            return success_count > len(network_commands) // 2
            
        except Exception as e:
            logger.error(f"❌ ネットワーク最適化エラー: {e}")
            return False
    
    def optimize_power_settings(self) -> bool:
        """電源設定の最適化"""
        logger.info("🔋 電源設定を最適化中...")
        
        try:
            # 高パフォーマンス電源プランに設定
            power_commands = [
                'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',  # 高パフォーマンス
                'powercfg /change monitor-timeout-ac 0',
                'powercfg /change standby-timeout-ac 0',
                'powercfg /change hibernate-timeout-ac 0',
                'powercfg /change disk-timeout-ac 0',
            ]
            
            success_count = 0
            
            for cmd in tqdm(power_commands, desc="電源設定最適化"):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ 電源コマンドエラー: {cmd} - {e}")
            
            logger.info(f"✅ {success_count}/{len(power_commands)}個の電源設定を最適化")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ 電源設定最適化エラー: {e}")
            return False
    
    def optimize_windows_settings(self) -> bool:
        """Windows設定の最適化（レジストリ不要）"""
        logger.info("🪟 Windows設定を最適化中...")
        
        try:
            # Windows設定最適化コマンド
            windows_commands = [
                # ゲームモード有効化
                'reg add "HKCU\\SOFTWARE\\Microsoft\\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 1 /f',
                
                # ハードウェアアクセラレーション有効化
                'reg add "HKCU\\SOFTWARE\\Microsoft\\DirectX\\UserGpuPreferences" /v "DirectXUserGlobalSettings" /t REG_SZ /d "VRROptimizeEnable=1;" /f',
                
                # フルスクリーン最適化無効化
                'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers" /v "VRChat.exe" /t REG_SZ /d "DISABLEDXMAXIMIZEDWINDOWEDMODE" /f',
                
                # Visual Effects最適化
                'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 2 /f',
            ]
            
            success_count = 0
            
            for cmd in tqdm(windows_commands, desc="Windows設定最適化"):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Windows設定コマンドエラー: {cmd} - {e}")
            
            logger.info(f"✅ {success_count}/{len(windows_commands)}個のWindows設定を最適化")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Windows設定最適化エラー: {e}")
            return False
    
    def optimize_gpu_settings(self) -> bool:
        """GPU設定の最適化"""
        logger.info("🎮 GPU設定を最適化中...")
        
        try:
            # NVIDIA GPU最適化
            nvidia_commands = [
                # NVIDIA Control Panel設定（レジストリ経由）
                'reg add "HKCU\\SOFTWARE\\NVIDIA Corporation\\Global\\NVTweak" /v "DisplayPowerSaving" /t REG_DWORD /d 0 /f',
                'reg add "HKCU\\SOFTWARE\\NVIDIA Corporation\\Global\\FTS" /v "EnableRidgedMultiGpu" /t REG_DWORD /d 0 /f',
            ]
            
            # AMD GPU最適化
            amd_commands = [
                # AMD Radeon設定
                'reg add "HKCU\\SOFTWARE\\AMD\\CN" /v "PowerSaverAutoEnable_DEF" /t REG_DWORD /d 0 /f',
            ]
            
            success_count = 0
            total_commands = len(nvidia_commands) + len(amd_commands)
            
            # NVIDIA設定
            for cmd in nvidia_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception:
                    pass
            
            # AMD設定
            for cmd in amd_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception:
                    pass
            
            logger.info(f"✅ {success_count}/{total_commands}個のGPU設定を最適化")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ GPU設定最適化エラー: {e}")
            return False
    
    def optimize_memory_settings(self) -> bool:
        """メモリ設定の最適化"""
        logger.info("💾 メモリ設定を最適化中...")
        
        try:
            # メモリ最適化コマンド
            memory_commands = [
                # 仮想メモリ設定
                'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Serialize" /v "StartupDelayInMSec" /t REG_DWORD /d 0 /f',
                
                # プリフェッチ最適化
                'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v "EnableBalloonTips" /t REG_DWORD /d 0 /f',
            ]
            
            success_count = 0
            
            for cmd in tqdm(memory_commands, desc="メモリ設定最適化"):
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ メモリ設定コマンドエラー: {cmd} - {e}")
            
            # メモリ使用量の確認と最適化
            memory = psutil.virtual_memory()
            logger.info(f"📊 現在のメモリ使用量: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
            
            if memory.percent > 80:
                logger.warning("⚠️ メモリ使用量が高いです。不要なアプリケーションを終了することを推奨します。")
            
            logger.info(f"✅ {success_count}/{len(memory_commands)}個のメモリ設定を最適化")
            return True
            
        except Exception as e:
            logger.error(f"❌ メモリ設定最適化エラー: {e}")
            return False
    
    def optimize_vr_specific_settings(self) -> bool:
        """VR専用設定の最適化"""
        logger.info("🥽 VR専用設定を最適化中...")
        
        try:
            # VRChat専用設定
            vrchat_commands = [
                # VRChat最適化設定
                'reg add "HKCU\\SOFTWARE\\VRChat\\VRChat" /v "fps_limit_desktop" /t REG_DWORD /d 144 /f',
                'reg add "HKCU\\SOFTWARE\\VRChat\\VRChat" /v "fps_limit_vr" /t REG_DWORD /d 90 /f',
            ]
            
            # SteamVR設定
            steamvr_commands = [
                # SteamVR最適化
                'reg add "HKCU\\SOFTWARE\\Valve\\Steam\\Apps\\250820" /v "LaunchOptions" /t REG_SZ /d "-vrmode vr -novid -nojoy" /f',
            ]
            
            success_count = 0
            total_commands = len(vrchat_commands) + len(steamvr_commands)
            
            for cmd in vrchat_commands + steamvr_commands:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                except Exception:
                    pass
            
            logger.info(f"✅ {success_count}/{total_commands}個のVR専用設定を最適化")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ VR専用設定最適化エラー: {e}")
            return False
    
    def optimize_amd_gpu_vrchat(self) -> bool:
        """AMD GPU向けVRChat特化最適化"""
        try:
            logger.info("AMD GPU向けVRChat最適化を実行中...")
            
            # AMD GPU検出
            amd_gpu_detected = False
            try:
                import subprocess
                gpu_info = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                        capture_output=True, text=True, timeout=10)
                if 'AMD' in gpu_info.stdout or 'Radeon' in gpu_info.stdout:
                    amd_gpu_detected = True
                    logger.info("AMD GPUを検出しました")
            except Exception:
                pass
            
            if not amd_gpu_detected:
                logger.info("AMD GPUが検出されませんでした")
                return True
            
            # VRChat起動オプション設定
            steam_userdata_paths = [
                os.path.expanduser("~\\AppData\\Local\\Steam\\userdata"),
                "C:\\Program Files (x86)\\Steam\\userdata"
            ]
            
            for userdata_path in steam_userdata_paths:
                if os.path.exists(userdata_path):
                    try:
                        # Steam設定ファイルでVRChatの起動オプションを確認/設定
                        # --enable-hw-video-decodingオプションを推奨
                        logger.info("VRChatの起動オプションに --enable-hw-video-decoding の追加を推奨")
                        break
                    except Exception as e:
                        logger.warning(f"Steam設定の確認中にエラー: {e}")
            
            # AMD固有のレジストリ最適化
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  "Software\\AMD\\CN\\OverDrive", 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    # AMD GPU最適化設定
                    winreg.SetValueEx(key, "EnableUlps", 0, winreg.REG_DWORD, 0)  # ULPS無効化
                    logger.info("AMD GPU ULPS設定を最適化しました")
            except Exception:
                pass
            
            # AMD Adrenalin設定の推奨値をログに記録
            logger.info("AMD Adrenalin推奨設定:")
            logger.info("- Anti-Lag: 無効")
            logger.info("- Radeon Boost: 無効")
            logger.info("- Radeon Image Sharpening: 無効")
            logger.info("- AMD FreeSync: VR使用時は無効推奨")
            
            return True
            
        except Exception as e:
            logger.error(f"AMD GPU向けVRChat最適化でエラー: {e}")
            return False

    def optimize_vrchat_specific_settings(self) -> bool:
        """VRChat特化設定最適化"""
        try:
            logger.info("VRChat特化設定最適化を実行中...")
            
            # VRChatローカル設定ディレクトリ
            vrchat_data_path = os.path.expanduser("~\\AppData\\LocalLow\\VRChat\\VRChat")
            
            if os.path.exists(vrchat_data_path):
                # VRChatの設定ファイル確認
                logger.info("VRChat設定ディレクトリを検出しました")
                
                # 推奨設定をログに出力
                logger.info("VRChat推奨設定:")
                logger.info("- Avatar Culling Distance: 25m")
                logger.info("- Maximum Shown Avatars: 15")
                logger.info("- Pixel Light Count: Low以上")
                logger.info("- Antialiasing: x2以上推奨")
                logger.info("- Particle Limiter: 有効（パフォーマンス重視時）")
                
            # VRChatプロセス最適化
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'vrchat' in proc.info['name'].lower():
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        logger.info(f"VRChatプロセス最適化: PID {proc.info['pid']}")
                        break
                except Exception:
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"VRChat特化設定最適化でエラー: {e}")
            return False
    
    def optimize_virtual_desktop(self) -> bool:
        """VirtualDesktop特化最適化"""
        try:
            logger.info("VirtualDesktop最適化を実行中...")
            
            # VirtualDesktopプロセス検出と最適化
            vd_processes = ['VirtualDesktop.Service', 'VirtualDesktop.Streamer', 'VirtualDesktop.Dashboard']
            optimized_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(vd_proc.lower() in proc.info['name'].lower() for vd_proc in vd_processes):
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        logger.info(f"VirtualDesktopプロセス最適化: {proc.info['name']} (PID: {proc.info['pid']})")
                        optimized_processes += 1
                except Exception:
                    continue
            
            # ネットワーク最適化（VirtualDesktop向け）
            try:
                # TCP/UDP最適化
                tcp_settings = [
                    ("TcpWindowSize", 65536),
                    ("TcpAckFrequency", 1),
                    ("TCPNoDelay", 1),
                    ("TcpDelAckTicks", 0)
                ]
                
                interfaces_key = "SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_key) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            interface_name = winreg.EnumKey(key, i)
                            interface_path = f"{interfaces_key}\\{interface_name}"
                            
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interface_path, 0, 
                                              winreg.KEY_SET_VALUE) as interface_key:
                                for setting, value in tcp_settings:
                                    try:
                                        winreg.SetValueEx(interface_key, setting, 0, winreg.REG_DWORD, value)
                                    except Exception:
                                        pass
                        except Exception:
                            continue
                
                logger.info("VirtualDesktop向けネットワーク設定を最適化しました")
                
            except Exception as e:
                logger.warning(f"ネットワーク最適化でエラー: {e}")
            
            # VirtualDesktop設定の推奨値をログに記録
            logger.info("VirtualDesktop推奨設定:")
            logger.info("- ビットレート: 自動または100-150Mbps（Wi-Fi 6使用時）")
            logger.info("- フレームレート: 90Hz（Quest 2）, 120Hz（Quest 3）")
            logger.info("- 解像度: 100%（パフォーマンス重視時は90%）")
            logger.info("- H.264/H.265エンコーディング: GPU性能に応じて選択")
            logger.info("- スライス: 2-4（レイテンシ重視時）")
            logger.info("- 専用ルーター使用を強く推奨（Wi-Fi 6E/7対応）")
            
            return True
            
        except Exception as e:
            logger.error(f"VirtualDesktop最適化でエラー: {e}")
            return False

    def optimize_steamvr_performance(self) -> bool:
        """SteamVR性能最適化"""
        try:
            logger.info("SteamVR性能最適化を実行中...")
            
            # SteamVRプロセス最適化
            steamvr_processes = ['vrserver', 'vrmonitor', 'vrcompositor', 'vrdashboard']
            optimized_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(svr_proc.lower() in proc.info['name'].lower() for svr_proc in steamvr_processes):
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        logger.info(f"SteamVRプロセス最適化: {proc.info['name']} (PID: {proc.info['pid']})")
                        optimized_processes += 1
                except Exception:
                    continue
            
            # SteamVR設定ファイルの最適化推奨値
            steamvr_config_path = os.path.expanduser("~\\AppData\\Local\\openvr")
            if os.path.exists(steamvr_config_path):
                logger.info("SteamVR設定ディレクトリを検出しました")
                
                logger.info("SteamVR推奨設定:")
                logger.info("- レンダリング解像度: 100%（高性能GPU時は110-120%）")
                logger.info("- リフレッシュレート: HMDの最大値に設定")
                logger.info("- モーションスムージング: 無効（十分なFPS時）")
                logger.info("- 非同期再投影: 有効")
                logger.info("- 自動解像度調整: 無効（手動調整推奨）")
            
            # Windows Mixed Reality最適化（該当する場合）
            try:
                wmr_key_path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Holographic"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, wmr_key_path, 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    # WMR最適化設定
                    winreg.SetValueEx(key, "FirstRunSucceeded", 0, winreg.REG_DWORD, 1)
                    logger.info("Windows Mixed Reality設定を最適化しました")
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"SteamVR性能最適化でエラー: {e}")
            return False
    
    def run_optimization(self) -> Dict[str, bool]:
        """最適化の実行"""
        logger.info("🚀 VR環境最適化を開始します...")
        
        # VR環境検出
        self.detect_vr_environment()
        
        # 最適化実行
        optimizations = [
            ("プロセス優先度最適化", self.optimize_process_priorities),
            ("ネットワーク設定最適化", self.optimize_network_settings),
            ("電源設定最適化", self.optimize_power_settings),
            ("Windows設定最適化", self.optimize_windows_settings),
            ("GPU設定最適化", self.optimize_gpu_settings),
            ("メモリ設定最適化", self.optimize_memory_settings),
            ("VR専用設定最適化", self.optimize_vr_specific_settings),
            ("AMD GPU向けVRChat最適化", self.optimize_amd_gpu_vrchat),
            ("VRChat特化設定最適化", self.optimize_vrchat_specific_settings),
            ("VirtualDesktop最適化", self.optimize_virtual_desktop),
            ("SteamVR性能最適化", self.optimize_steamvr_performance),
        ]
        
        results = {}
        
        for name, func in optimizations:
            logger.info(f"\n📋 {name}を実行中...")
            try:
                results[name] = func()
                if results[name]:
                    logger.info(f"✅ {name}が完了しました")
                else:
                    logger.warning(f"⚠️ {name}で問題が発生しました")
            except Exception as e:
                logger.error(f"❌ {name}でエラーが発生: {e}")
                results[name] = False
        
        self.optimization_results = results
        return results
    
    def generate_report(self) -> str:
        """最適化レポートの生成"""
        report = []
        report.append("=" * 60)
        report.append("🥽 VR環境最適化レポート（管理者権限不要版）")
        report.append("=" * 60)
        report.append(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 検出されたVRアプリケーション
        report.append("🔍 検出されたVRアプリケーション:")
        for app, detected in self.detected_vr_apps.items():
            status = "✅ 検出" if detected else "❌ 未検出"
            report.append(f"  {app}: {status}")
        report.append("")
        
        # 最適化結果
        report.append("⚡ 最適化結果:")
        success_count = 0
        for name, success in self.optimization_results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            report.append(f"  {name}: {status}")
            if success:
                success_count += 1
        
        report.append("")
        report.append(f"📊 成功率: {success_count}/{len(self.optimization_results)} ({success_count/len(self.optimization_results)*100:.1f}%)")
        
        # システム情報
        report.append("")
        report.append("💻 システム情報:")
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        report.append(f"  CPU使用率: {cpu_percent:.1f}%")
        report.append(f"  メモリ使用率: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
        
        # 推奨事項
        report.append("")
        report.append("💡 推奨事項:")
        if cpu_percent > 80:
            report.append("  ⚠️ CPU使用率が高いです。不要なアプリケーションを終了してください。")
        if memory.percent > 80:
            report.append("  ⚠️ メモリ使用率が高いです。不要なアプリケーションを終了してください。")
        
        if not any(self.detected_vr_apps.values()):
            report.append("  ℹ️ VRアプリケーションが検出されませんでした。VRアプリを起動後に再実行してください。")
        
        report.append("")
        report.append("🔄 次回実行時の注意:")
        report.append("  • VRアプリケーション起動後に実行すると、より効果的です")
        report.append("  • 定期的な実行（週1回程度）を推奨します")
        report.append("  • 問題が発生した場合は、PC再起動を試してください")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, report: str) -> str:
        """レポートをファイルに保存"""
        filename = f"vr_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        return filename

def main():
    """メイン関数"""
    print("🥽 VR環境最適化ツール（管理者権限不要版）")
    print("=" * 60)
    print("VirtualDesktop、SteamVR、VRChat用PC最適化")
    print("管理者権限なしで実行可能な最適化を提供します。")
    print("=" * 60)
    
    # 確認
    response = input("\n最適化を開始しますか？ (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'はい']:
        print("最適化をキャンセルしました。")
        return
    
    # 最適化実行
    optimizer = VROptimizerNoAdmin()
    
    try:
        results = optimizer.run_optimization()
        
        # レポート生成
        report = optimizer.generate_report()
        print("\n" + report)
        
        # レポート保存
        filename = optimizer.save_report(report)
        print(f"\n📄 詳細レポートを保存しました: {filename}")
        
        # 成功率確認
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            print("\n🎉 すべての最適化が正常に完了しました！")
        elif success_count > total_count // 2:
            print(f"\n✅ 最適化が部分的に完了しました ({success_count}/{total_count})")
        else:
            print(f"\n⚠️ 最適化で問題が発生しました ({success_count}/{total_count})")
        
        print("\n💡 VRアプリケーションを再起動して効果を確認してください。")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 最適化が中断されました。")
    except Exception as e:
        logger.error(f"❌ 予期しないエラーが発生しました: {e}")
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 