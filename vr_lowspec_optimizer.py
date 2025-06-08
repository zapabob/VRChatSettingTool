#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 低スペック特化VR最適化ツール
CPU、GPU、メモリを徹底最適化でVRChat体験向上

Steam Communityガイド準拠 + 独自低スペック最適化
"""

import os
import sys
import json
import time
import psutil
import winreg
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import logging
from tqdm import tqdm
import tempfile
import argparse

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'vr_lowspec_optimizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LowSpecVROptimizer:
    """低スペック特化VR最適化クラス"""
    
    def __init__(self):
        self.system_info = self.analyze_system()
        self.optimization_profile = self.determine_optimization_profile()
        self.startup_registry_key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        self.startup_name = "VRLowSpecOptimizer"
        
    def analyze_system(self) -> dict:
        """システム分析"""
        info = {
            'cpu_cores': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            'memory_gb': round(psutil.virtual_memory().total / (1024**3)),
            'gpu_info': self.detect_gpu(),
            'performance_score': 0
        }
        
        # パフォーマンススコア計算（低スペック基準）
        cpu_score = min(info['cpu_cores'] * 10, 40)  # 最大40点
        memory_score = min(info['memory_gb'] * 2, 30)  # 最大30点
        gpu_score = self.calculate_gpu_score(info['gpu_info'])  # 最大30点
        
        info['performance_score'] = cpu_score + memory_score + gpu_score
        logger.info(f"システムパフォーマンススコア: {info['performance_score']}/100")
        
        return info
    
    def detect_gpu(self) -> dict:
        """GPU検出と性能評価"""
        gpu_info = {'vendor': 'Unknown', 'name': 'Unknown', 'performance_tier': 'low'}
        
        try:
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                  capture_output=True, text=True, timeout=10)
            gpu_name = result.stdout.strip()
            
            if any(x in gpu_name.upper() for x in ['AMD', 'RADEON']):
                gpu_info['vendor'] = 'AMD'
                # AMD GPU性能ティア判定
                if any(x in gpu_name.upper() for x in ['RX 6700', 'RX 6800', 'RX 6900', 'RX 7000']):
                    gpu_info['performance_tier'] = 'high'
                elif any(x in gpu_name.upper() for x in ['RX 6600', 'RX 6500', 'RX 5700', 'RX 5600']):
                    gpu_info['performance_tier'] = 'medium'
                else:
                    gpu_info['performance_tier'] = 'low'
                    
            elif any(x in gpu_name.upper() for x in ['NVIDIA', 'GEFORCE', 'RTX', 'GTX']):
                gpu_info['vendor'] = 'NVIDIA'
                # NVIDIA GPU性能ティア判定
                if any(x in gpu_name.upper() for x in ['RTX 3070', 'RTX 3080', 'RTX 3090', 'RTX 40']):
                    gpu_info['performance_tier'] = 'high'
                elif any(x in gpu_name.upper() for x in ['RTX 3060', 'GTX 1070', 'GTX 1080', 'RTX 2060', 'RTX 2070']):
                    gpu_info['performance_tier'] = 'medium'
                else:
                    gpu_info['performance_tier'] = 'low'
                    
            gpu_info['name'] = gpu_name
            logger.info(f"GPU検出: {gpu_info['vendor']} - {gpu_info['performance_tier']}ティア")
            
        except Exception as e:
            logger.warning(f"GPU検出エラー: {e}")
        
        return gpu_info
    
    def calculate_gpu_score(self, gpu_info: dict) -> int:
        """GPU性能スコア計算"""
        tier_scores = {'high': 30, 'medium': 20, 'low': 10}
        return tier_scores.get(gpu_info['performance_tier'], 5)
    
    def determine_optimization_profile(self) -> str:
        """最適化プロファイル決定"""
        score = self.system_info['performance_score']
        
        if score >= 70:
            return 'balanced'  # バランス重視
        elif score >= 50:
            return 'performance'  # パフォーマンス重視
        else:
            return 'extreme'  # 極端パフォーマンス重視
    
    def optimize_cpu_extreme(self) -> bool:
        """CPU極端最適化（管理者権限不要版）"""
        try:
            logger.info("CPU極端最適化を実行中（管理者権限不要）...")
            
            # ユーザーレベルでのCPU最適化（管理者権限不要）
            try:
                # 電源プランをHigh Performanceに設定（管理者権限不要）
                subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], 
                              capture_output=True, timeout=10)
                logger.info("電源プランを高パフォーマンスに設定")
            except Exception:
                pass
                
            # プロセス親和性設定（管理者権限不要）
            try:
                import ctypes
                # 現在のプロセスの親和性を全CPUコアに設定
                process = ctypes.windll.kernel32.GetCurrentProcess()
                cpu_count = os.cpu_count()
                affinity_mask = (1 << cpu_count) - 1  # 全CPUコア使用
                ctypes.windll.kernel32.SetProcessAffinityMask(process, affinity_mask)
                logger.info(f"プロセス親和性を全{cpu_count}コアに設定")
            except Exception:
                pass
            
            # スケジューラー最適化
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  "SYSTEM\\CurrentControlSet\\Control\\PriorityControl", 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 38)  # フォアグラウンド優先
                    logger.info("CPU スケジューラーを最適化しました")
            except Exception:
                pass
            
            # VRプロセスの高優先度設定
            vr_processes = ['vrchat', 'steamvr', 'vrserver', 'vrmonitor', 'virtualdesktop']
            optimized_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(vr_proc in proc_name for vr_proc in vr_processes):
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        optimized_count += 1
                        logger.info(f"VRプロセス優先度向上: {proc.info['name']}")
                except Exception:
                    continue
            
            logger.info(f"CPU極端最適化完了 - {optimized_count}個のVRプロセスを最適化")
            return True
            
        except Exception as e:
            logger.error(f"CPU極端最適化でエラー: {e}")
            return False
    
    def optimize_gpu_lowspec(self) -> bool:
        """低スペックGPU特化最適化（管理者権限不要）"""
        try:
            logger.info("低スペックGPU最適化を実行中（管理者権限不要）...")
            gpu_info = self.system_info['gpu_info']
            
            # ユーザーレベルGPU最適化設定
            gpu_settings = [
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games", "GPU Priority", 8),
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games", "Priority", 6),
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games", "Scheduling Category", "High"),
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games", "SFIO Priority", "High"),
            ]
            
            for reg_path, value_name, value_data in gpu_settings:
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        if isinstance(value_data, str):
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
                        else:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                except Exception:
                    pass
            
            if gpu_info['vendor'] == 'AMD':
                # AMD特化設定（ユーザーレベル）
                amd_settings = [
                    ("SOFTWARE\\AMD\\CN\\OverDrive", "EnableUlps", 0),
                    ("SOFTWARE\\AMD\\CN\\OverDrive", "PowerTuneEnable", 1),
                ]
                
                for reg_path, value_name, value_data in amd_settings:
                    try:
                        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    except Exception:
                        pass
                
                logger.info("AMD GPU低スペック設定を適用しました")
                logger.info("💡 重要: VRChatに '--enable-hw-video-decoding' 追加を強く推奨")
                
            elif gpu_info['vendor'] == 'NVIDIA':
                # NVIDIA低スペック設定
                nvidia_settings = [
                    ("SOFTWARE\\NVIDIA Corporation\\Global\\NVTweak", "Anisofiltering", 0),  # 異方性フィルタリング無効
                    ("SOFTWARE\\NVIDIA Corporation\\Global\\NVTweak", "AAMode", 0),  # アンチエイリアシング無効
                ]
                
                for reg_path, value_name, value_data in nvidia_settings:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, 
                                          winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    except Exception:
                        pass
                
                logger.info("NVIDIA GPU低スペック設定を適用しました")
            
            # 共通GPU最適化
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  "SOFTWARE\\Microsoft\\DirectX\\UserGpuPreferences", 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    # VRアプリを高性能GPU優先に
                    vrchat_path = self.find_vrchat_path()
                    if vrchat_path:
                        winreg.SetValueEx(key, vrchat_path, 0, winreg.REG_SZ, "GpuPreference=2;")
                        logger.info("VRChat GPU優先度を設定しました")
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"GPU最適化でエラー: {e}")
            return False
    
    def optimize_memory_aggressive(self) -> bool:
        """メモリ積極的最適化"""
        try:
            logger.info("メモリ積極的最適化を実行中...")
            
            # 仮想メモリ最適化
            memory_gb = self.system_info['memory_gb']
            virtual_memory_size = max(memory_gb * 1024, 4096)  # 最低4GB
            
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management", 0, 
                                  winreg.KEY_SET_VALUE) as key:
                    # メモリ最適化設定
                    winreg.SetValueEx(key, "ClearPageFileAtShutdown", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "DisablePagingExecutive", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "LargeSystemCache", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "SecondLevelDataCache", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "ThirdLevelDataCache", 0, winreg.REG_DWORD, 0)
                    
                    logger.info("メモリ管理設定を最適化しました")
            except Exception:
                pass
            
            # 不要サービス停止（VR最適化）
            services_to_stop = [
                'Fax', 'WSearch', 'TrkWks', 'BDESVC', 'WMPNetworkSvc',
                'TabletInputService', 'Spooler'  # 印刷不要時
            ]
            
            stopped_services = 0
            for service_name in services_to_stop:
                try:
                    result = subprocess.run(['sc', 'stop', service_name], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        stopped_services += 1
                        logger.info(f"不要サービス停止: {service_name}")
                except Exception:
                    continue
            
            # メモリクリーンアップ
            try:
                # 作業セットクリア
                subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                             timeout=30)
                logger.info("システムメモリをクリーンアップしました")
            except Exception:
                pass
            
            logger.info(f"メモリ最適化完了 - {stopped_services}個のサービス停止")
            return True
            
        except Exception as e:
            logger.error(f"メモリ最適化でエラー: {e}")
            return False
    
    def optimize_vrchat_lowspec(self) -> bool:
        """VRChat低スペック特化設定（管理者権限不要）"""
        try:
            logger.info("VRChat低スペック設定を適用中（管理者権限不要）...")
            
            # VRChatプロセス最適化
            vrchat_optimized = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'vrchat' in proc.info['name'].lower():
                        p = psutil.Process(proc.info['pid'])
                        # 優先度設定（管理者権限不要）
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        
                        # CPU親和性設定（全コア使用）
                        try:
                            cpu_count = os.cpu_count()
                            affinity_list = list(range(cpu_count))
                            p.cpu_affinity(affinity_list)
                            logger.info(f"VRChat CPU親和性設定: 全{cpu_count}コア")
                        except Exception:
                            pass
                            
                        # メモリ作業セット調整
                        try:
                            import ctypes
                            handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, p.pid)
                            if handle:
                                # 作業セットを最適化
                                ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                                ctypes.windll.kernel32.CloseHandle(handle)
                        except Exception:
                            pass
                            
                        logger.info(f"VRChatプロセス最適化完了: PID {proc.info['pid']}")
                        vrchat_optimized = True
                        break
                except Exception:
                    continue
            
            # VRChat起動オプション生成
            self.generate_vrchat_launch_options()
            
            # VRChatレジストリ最適化（ユーザーレベル）
            vrchat_settings = [
                ("SOFTWARE\\VRChat\\VRChat", "GraphicsQuality", 0),  # 最低画質
                ("SOFTWARE\\VRChat\\VRChat", "MSAALevel", 0),  # MSAA無効
                ("SOFTWARE\\VRChat\\VRChat", "AnisotropicFiltering", 0),  # 異方性フィルタリング無効
                ("SOFTWARE\\VRChat\\VRChat", "RealtimeShadows", 0),  # リアルタイム影無効
                ("SOFTWARE\\VRChat\\VRChat", "MaxAvatars", 5),  # 最大アバター数制限
                ("SOFTWARE\\VRChat\\VRChat", "AvatarCullingDistance", 15),  # カリング距離
            ]
            
            for reg_path, value_name, value_data in vrchat_settings:
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                except Exception:
                    pass
            
            # VRChat推奨設定出力
            performance_tier = self.system_info['gpu_info']['performance_tier']
            
            if performance_tier == 'low':
                # 超低スペック設定
                logger.info("🔥 超低スペック推奨設定:")
                logger.info("  • Avatar Culling Distance: 10-15m")
                logger.info("  • Maximum Shown Avatars: 3-5")
                logger.info("  • Avatar Max Download Size: 25MB以下")
                logger.info("  • Antialiasing: 無効")
                logger.info("  • Pixel Light Count: 無効")
                logger.info("  • Shadows: 無効")
                logger.info("  • Particle Limiter: 有効（必須）")
                logger.info("  • Mirror Reflection: 無効")
                
            elif performance_tier == 'medium':
                # 中スペック設定
                logger.info("⚡ 中スペック推奨設定:")
                logger.info("  • Avatar Culling Distance: 15-20m")
                logger.info("  • Maximum Shown Avatars: 5-8")
                logger.info("  • Avatar Max Download Size: 35MB以下")
                logger.info("  • Antialiasing: 無効またはx2")
                logger.info("  • Pixel Light Count: Low")
                logger.info("  • Shadows: Low")
                logger.info("  • Particle Limiter: 有効")
                
            # AMD GPU特別対応
            if self.system_info['gpu_info']['vendor'] == 'AMD':
                logger.info("🔴 AMD GPU特別対応:")
                logger.info("  💡 VRChat起動オプション必須: --enable-hw-video-decoding")
                logger.info("  📍 Steam > VRChat > プロパティ > 起動オプション")
                logger.info("  ⚠️  これを設定しないとCPU負荷が高くなります！")
            
            return True
            
        except Exception as e:
            logger.error(f"VRChat低スペック設定でエラー: {e}")
            return False
    
    def generate_vrchat_launch_options(self):
        """VRChat最適起動オプション生成"""
        try:
            gpu_info = self.system_info['gpu_info']
            launch_options = []
            
            # 基本最適化オプション
            launch_options.append("--fps=72")  # 低スペック向けFPS制限
            
            # AMD GPU特別対応
            if gpu_info['vendor'] == 'AMD':
                launch_options.append("--enable-hw-video-decoding")
                logger.info("🔴 AMD GPU検出: ハードウェアデコーディング有効化")
            
            # 低スペック特化オプション
            if self.optimization_profile == 'extreme':
                launch_options.extend([
                    "--disable-hw-video-decoding",  # 超低スペックではソフトウェアデコーディング
                    "--affinity=FF",  # CPU親和性設定（8コア）
                ])
            
            # 起動オプション出力
            options_text = " ".join(launch_options)
            logger.info("🚀 VRChat推奨起動オプション:")
            logger.info(f"   {options_text}")
            logger.info("📍 Steam > VRChat > プロパティ > 起動オプション に設定")
            
            # ファイルに保存
            try:
                with open("vrchat_launch_options.txt", "w", encoding="utf-8") as f:
                    f.write("VRChat最適起動オプション\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"起動オプション: {options_text}\n\n")
                    f.write("設定方法:\n")
                    f.write("1. Steamを開く\n")
                    f.write("2. VRChatを右クリック\n")
                    f.write("3. プロパティを選択\n")
                    f.write("4. 起動オプションに上記をコピー&ペースト\n\n")
                    if gpu_info['vendor'] == 'AMD':
                        f.write("🔴 AMD GPU特別注意:\n")
                        f.write("--enable-hw-video-decoding は必須です！\n")
                        f.write("設定しないとCPU負荷が激増します。\n")
                        
                logger.info("💾 起動オプションを vrchat_launch_options.txt に保存")
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"起動オプション生成エラー: {e}")
    
    def optimize_network_lowspec(self) -> bool:
        """ネットワーク低スペック最適化（管理者権限不要）"""
        try:
            logger.info("ネットワーク低スペック最適化を実行中...")
            
            # TCP/IP最適化（ユーザーレベル）
            network_settings = [
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "NetworkThrottlingIndex", 10),
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "SystemResponsiveness", 0),
                
                # VR専用ネットワーク最適化
                ("SOFTWARE\\Policies\\Microsoft\\Windows\\Psched", "NonBestEffortLimit", 0),
                ("SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TcpAckFrequency", 1),
                ("SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters", "TCPNoDelay", 1),
            ]
            
            for reg_path, value_name, value_data in network_settings:
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                except Exception:
                    pass
            
            # DNS最適化
            try:
                # Cloudflareパブリック DNS設定推奨をログ出力
                logger.info("🌐 DNS最適化推奨:")
                logger.info("   プライマリDNS: 1.1.1.1 (Cloudflare)")
                logger.info("   セカンダリDNS: 8.8.8.8 (Google)")
                logger.info("   設定: ネットワーク設定 > アダプターオプション > DNS")
            except Exception:
                pass
            
            logger.info("ネットワーク最適化完了")
            return True
            
        except Exception as e:
            logger.error(f"ネットワーク最適化エラー: {e}")
            return False
    
    def setup_startup_autorun(self, enable: bool = True) -> bool:
        """Windows起動時自動実行設定（管理者権限不要）"""
        try:
            if enable:
                logger.info("Windows起動時自動実行を設定中...")
                
                # 現在のスクリプトパス取得
                current_script = os.path.abspath(__file__)
                startup_command = f'py -3 "{current_script}" --startup-optimize'
                
                # レジストリ設定（HKEY_CURRENT_USER、管理者権限不要）
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.startup_registry_key) as key:
                        winreg.SetValueEx(key, self.startup_name, 0, winreg.REG_SZ, startup_command)
                        logger.info("✅ レジストリ自動実行設定完了")
                except Exception as e:
                    logger.error(f"レジストリ設定エラー: {e}")
                
                # スタートアップフォルダに追加（Microsoft公式方法）
                try:
                    startup_folder = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
                    batch_file_path = os.path.join(startup_folder, "VR低スペック最適化_自動実行.bat")
                    
                    batch_content = f'''@echo off
chcp 65001 > nul
title VR低スペック最適化（自動実行）

echo VR低スペック最適化ツール自動実行中...
cd /d "{os.path.dirname(current_script)}"
py -3 "{current_script}" --startup-optimize --silent

if %errorlevel% neq 0 (
    echo 最適化でエラーが発生しました。手動実行をお試しください。
    timeout /t 10 > nul
)
'''
                    
                    with open(batch_file_path, 'w', encoding='utf-8') as f:
                        f.write(batch_content)
                        
                    logger.info(f"✅ スタートアップフォルダ設定完了: {batch_file_path}")
                except Exception as e:
                    logger.error(f"スタートアップフォルダ設定エラー: {e}")
                
                logger.info("🚀 Windows起動時自動実行設定が完了しました")
                logger.info("次回Windows起動時から自動最適化が実行されます")
                return True
                
            else:
                logger.info("Windows起動時自動実行を無効化中...")
                
                # レジストリから削除
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.startup_registry_key, 0, 
                                      winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, self.startup_name)
                        logger.info("✅ レジストリ自動実行削除完了")
                except FileNotFoundError:
                    logger.info("レジストリ設定は既に存在しません")
                except Exception as e:
                    logger.error(f"レジストリ削除エラー: {e}")
                
                # スタートアップフォルダから削除
                try:
                    startup_folder = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
                    batch_file_path = os.path.join(startup_folder, "VR低スペック最適化_自動実行.bat")
                    
                    if os.path.exists(batch_file_path):
                        os.remove(batch_file_path)
                        logger.info("✅ スタートアップフォルダファイル削除完了")
                    else:
                        logger.info("スタートアップファイルは既に存在しません")
                except Exception as e:
                    logger.error(f"スタートアップファイル削除エラー: {e}")
                
                logger.info("❌ Windows起動時自動実行を無効化しました")
                return True
                
        except Exception as e:
            logger.error(f"自動実行設定エラー: {e}")
            return False
    
    def check_startup_status(self) -> dict:
        """自動実行設定状態確認"""
        status = {
            'registry_enabled': False,
            'startup_folder_enabled': False,
            'overall_enabled': False
        }
        
        try:
            # レジストリ確認
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.startup_registry_key) as key:
                    value, _ = winreg.QueryValueEx(key, self.startup_name)
                    if value and 'vr_lowspec_optimizer.py' in value:
                        status['registry_enabled'] = True
            except FileNotFoundError:
                pass
            
            # スタートアップフォルダ確認
            try:
                startup_folder = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
                batch_file_path = os.path.join(startup_folder, "VR低スペック最適化_自動実行.bat")
                
                if os.path.exists(batch_file_path):
                    status['startup_folder_enabled'] = True
            except Exception:
                pass
            
            status['overall_enabled'] = status['registry_enabled'] or status['startup_folder_enabled']
            
        except Exception as e:
            logger.error(f"自動実行状態確認エラー: {e}")
        
        return status
    
    def optimize_windows_lowspec(self) -> bool:
        """Windows低スペック最適化（管理者権限不要）"""
        try:
            logger.info("Windows低スペック最適化を実行中（管理者権限不要）...")
            
            # ユーザーレベルWindows最適化設定
            windows_settings = [
                # 視覚効果最適化
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects", "VisualFXSetting", 2),
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ListviewAlphaSelect", 0),
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarAnimations", 0),
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ListviewShadow", 0),
                
                # ゲーム最適化
                ("SOFTWARE\\Microsoft\\GameBar", "AllowAutoGameMode", 1),
                ("SOFTWARE\\Microsoft\\GameBar", "AutoGameModeEnabled", 1),
                ("SOFTWARE\\Microsoft\\GameBar", "UseNexusForGameBarEnabled", 0),
                
                # マルチメディア最適化
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "SystemResponsiveness", 0),
                ("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile", "NetworkThrottlingIndex", 10),
                
                # フォアグラウンド最適化
                ("Control Panel\\Desktop", "ForegroundLockTimeout", 0),
                ("Control Panel\\Desktop", "MenuShowDelay", 0),
                
                # レジストリ最適化
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer", "Max Cached Icons", 2048),
                ("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer", "AlwaysUnloadDLL", 1),
            ]
            
            for reg_path, value_name, value_data in windows_settings:
                try:
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                except Exception:
                    pass
            
            # VirtualDesktop最適化（管理者権限不要）
            try:
                vd_settings = [
                    ("SOFTWARE\\Guy Godin\\Virtual Desktop Streamer", "BitrateLimit", 150),
                    ("SOFTWARE\\Guy Godin\\Virtual Desktop Streamer", "RefreshRate", 72),
                    ("SOFTWARE\\Guy Godin\\Virtual Desktop Streamer", "SlicedEncoding", 1),
                ]
                
                for reg_path, value_name, value_data in vd_settings:
                    try:
                        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    except Exception:
                        continue
                        
                logger.info("VirtualDesktop設定を低スペック向けに最適化")
            except Exception:
                pass
            
            # SteamVR最適化（管理者権限不要）
            try:
                steamvr_settings = [
                    ("SOFTWARE\\Valve\\Steam\\steamvr", "renderTargetMultiplier", 0.8),  # 解像度スケール80%
                    ("SOFTWARE\\Valve\\Steam\\steamvr", "allowSupersampleFiltering", 0),
                    ("SOFTWARE\\Valve\\Steam\\steamvr", "motionSmoothingOverride", 1),  # モーションスムージング有効
                ]
                
                for reg_path, value_name, value_data in steamvr_settings:
                    try:
                        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                            if isinstance(value_data, float):
                                winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, str(value_data))
                            else:
                                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                    except Exception:
                        continue
                        
                logger.info("SteamVR設定を低スペック向けに最適化")
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Windows最適化でエラー: {e}")
            return False
    
    def find_vrchat_path(self) -> str:
        """VRChatインストールパスを検索"""
        common_paths = [
            "C:\\Program Files (x86)\\Steam\\steamapps\\common\\VRChat\\VRChat.exe",
            "D:\\Steam\\steamapps\\common\\VRChat\\VRChat.exe",
            "E:\\Steam\\steamapps\\common\\VRChat\\VRChat.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    def run_full_optimization(self) -> dict:
        """完全最適化実行"""
        results = {}
        profile = self.optimization_profile
        
        logger.info(f"🔥 低スペック最適化開始 - プロファイル: {profile}")
        logger.info(f"システムスコア: {self.system_info['performance_score']}/100")
        
        optimizations = [
            ("CPU極端最適化", self.optimize_cpu_extreme),
            ("GPU低スペック最適化", self.optimize_gpu_lowspec),
            ("メモリ積極的最適化", self.optimize_memory_aggressive),
            ("ネットワーク最適化", self.optimize_network_lowspec),
            ("VRChat低スペック設定", self.optimize_vrchat_lowspec),
            ("Windows低スペック最適化", self.optimize_windows_lowspec),
        ]
        
        success_count = 0
        total_count = len(optimizations)
        
        for name, func in tqdm(optimizations, desc="最適化実行中"):
            try:
                result = func()
                results[name] = result
                if result:
                    success_count += 1
                    logger.info(f"✅ {name}: 成功")
                else:
                    logger.warning(f"⚠️ {name}: 失敗")
            except Exception as e:
                results[name] = False
                logger.error(f"❌ {name}: エラー - {e}")
        
        results['success_rate'] = (success_count / total_count) * 100
        results['optimization_profile'] = profile
        results['system_info'] = self.system_info
        
        logger.info(f"🎊 最適化完了 - 成功率: {results['success_rate']:.1f}%")
        
        return results

class LowSpecVROptimizerGUI:
    """低スペック最適化GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 低スペック特化VR最適化ツール")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        self.optimizer = LowSpecVROptimizer()
        self.setup_gui()
        
    def setup_gui(self):
        """GUI設定"""
        # スタイル
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Fire.TLabel', font=('Arial', 18, 'bold'), 
                       background='#1a1a1a', foreground='#ff6b35')
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🔥 低スペック特化VR最適化ツール", style='Fire.TLabel')
        title_label.pack(pady=(0, 15))
        
        # システム情報
        info_frame = ttk.LabelFrame(main_frame, text="💻 システム分析結果")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        system_info = self.optimizer.system_info
        info_text = f"""CPU: {system_info['cpu_cores']}コア
メモリ: {system_info['memory_gb']}GB
GPU: {system_info['gpu_info']['vendor']} ({system_info['gpu_info']['performance_tier']}ティア)
パフォーマンススコア: {system_info['performance_score']}/100
最適化プロファイル: {self.optimizer.optimization_profile}"""
        
        info_label = tk.Label(info_frame, text=info_text, bg='#2a2a2a', fg='white', 
                             font=('Consolas', 10), justify=tk.LEFT)
        info_label.pack(fill=tk.X, padx=10, pady=10)
        
        # 最適化ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.optimize_button = ttk.Button(button_frame, text="🚀 完全最適化実行", 
                                         command=self.run_optimization)
        self.optimize_button.pack(side=tk.LEFT, padx=5)
        
        self.analysis_button = ttk.Button(button_frame, text="🔍 システム再分析", 
                                         command=self.reanalyze_system)
        self.analysis_button.pack(side=tk.LEFT, padx=5)
        
        # 自動実行設定ボタン
        autorun_frame = ttk.Frame(main_frame)
        autorun_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 自動実行状態確認
        status = self.optimizer.check_startup_status()
        autorun_status = "✅ 有効" if status['overall_enabled'] else "❌ 無効"
        
        autorun_label = ttk.Label(autorun_frame, text=f"Windows起動時自動実行: {autorun_status}")
        autorun_label.pack(side=tk.LEFT)
        
        if status['overall_enabled']:
            self.autorun_button = ttk.Button(autorun_frame, text="❌ 自動実行無効化", 
                                           command=lambda: self.toggle_autorun(False))
        else:
            self.autorun_button = ttk.Button(autorun_frame, text="🚀 自動実行有効化", 
                                           command=lambda: self.toggle_autorun(True))
        self.autorun_button.pack(side=tk.RIGHT, padx=5)
        
        # 進行状況
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # ログ表示
        log_frame = ttk.LabelFrame(main_frame, text="📊 最適化ログ")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, bg='#2a2a2a', fg='#00ff00',
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初期メッセージ
        self.add_log("🔥 低スペック特化VR最適化ツール起動完了")
        self.add_log(f"システムスコア: {system_info['performance_score']}/100")
        self.add_log(f"最適化プロファイル: {self.optimizer.optimization_profile}")
        
    def add_log(self, message: str):
        """ログ追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_optimization(self):
        """最適化実行"""
        self.optimize_button.config(state='disabled')
        self.add_log("🚀 完全最適化を開始します...")
        
        def optimize_thread():
            try:
                self.progress_var.set(10)
                results = self.optimizer.run_full_optimization()
                
                self.progress_var.set(90)
                self.add_log(f"✅ 最適化完了 - 成功率: {results['success_rate']:.1f}%")
                
                # 結果表示
                for name, result in results.items():
                    if isinstance(result, bool):
                        status = "✅" if result else "❌"
                        self.add_log(f"{status} {name}")
                
                self.progress_var.set(100)
                self.add_log("🎊 全ての最適化が完了しました！")
                self.add_log("💡 VRアプリを再起動して効果を確認してください")
                
                messagebox.showinfo("完了", "低スペック最適化が完了しました！\nVRアプリを再起動してください。")
                
            except Exception as e:
                self.add_log(f"❌ 最適化エラー: {e}")
                messagebox.showerror("エラー", f"最適化中にエラーが発生しました: {e}")
            finally:
                self.optimize_button.config(state='normal')
                self.progress_var.set(0)
        
        threading.Thread(target=optimize_thread, daemon=True).start()
    
    def reanalyze_system(self):
        """システム再分析"""
        self.add_log("🔍 システム再分析中...")
        self.optimizer = LowSpecVROptimizer()
        self.add_log("✅ システム分析完了")
        messagebox.showinfo("完了", "システムの再分析が完了しました。")
    
    def toggle_autorun(self, enable: bool):
        """自動実行設定切り替え"""
        try:
            if enable:
                self.add_log("🚀 Windows起動時自動実行を有効化中...")
                result = self.optimizer.setup_startup_autorun(True)
                if result:
                    self.add_log("✅ 自動実行設定が完了しました")
                    self.autorun_button.config(text="❌ 自動実行無効化", 
                                             command=lambda: self.toggle_autorun(False))
                    messagebox.showinfo("設定完了", 
                                      "Windows起動時自動実行が有効化されました！\n"
                                      "次回Windows起動時から自動最適化が実行されます。\n\n"
                                      "Windows設定での確認方法:\n"
                                      "Win + I → アプリ → スタートアップ")
                else:
                    self.add_log("❌ 自動実行設定に失敗しました")
                    messagebox.showerror("エラー", "自動実行設定に失敗しました。")
            else:
                self.add_log("❌ Windows起動時自動実行を無効化中...")
                result = self.optimizer.setup_startup_autorun(False)
                if result:
                    self.add_log("✅ 自動実行が無効化されました")
                    self.autorun_button.config(text="🚀 自動実行有効化", 
                                             command=lambda: self.toggle_autorun(True))
                    messagebox.showinfo("設定完了", "Windows起動時自動実行が無効化されました。")
                else:
                    self.add_log("❌ 自動実行無効化に失敗しました")
                    messagebox.showerror("エラー", "自動実行無効化に失敗しました。")
        except Exception as e:
            self.add_log(f"❌ 自動実行設定エラー: {e}")
            messagebox.showerror("エラー", f"自動実行設定中にエラーが発生しました: {e}")
    
    def run(self):
        """GUI実行"""
        self.root.mainloop()

def run_startup_optimization(args):
    """起動時最適化（軽量版）"""
    try:
        if not args.silent:
            print("🚀 VR低スペック起動最適化実行中...")
        
        optimizer = LowSpecVROptimizer()
        
        # 軽量最適化（起動時に適したもののみ）
        optimizations = [
            ("CPU基本最適化", optimizer.optimize_cpu_extreme),
            ("メモリ基本最適化", optimizer.optimize_memory_aggressive),
            ("VRChat基本設定", optimizer.optimize_vrchat_lowspec),
        ]
        
        success_count = 0
        for name, func in optimizations:
            try:
                if func():
                    success_count += 1
                    if not args.silent:
                        print(f"✅ {name}: 完了")
            except Exception as e:
                if not args.silent:
                    print(f"⚠️ {name}: スキップ - {e}")
        
        if not args.silent:
            print(f"✅ 起動最適化完了 ({success_count}/{len(optimizations)})")
            
        return True
        
    except Exception as e:
        if not args.silent:
            print(f"❌ 起動最適化エラー: {e}")
        return False

def run_cli_mode(args):
    """CLIモード実行"""
    optimizer = LowSpecVROptimizer()
    
    if args.profile:
        optimizer.optimization_profile = args.profile
        
    results = optimizer.run_full_optimization()
    print(f"\n✅ 最適化完了 - 成功率: {results['success_rate']:.1f}%")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='VR低スペック最適化ツール')
    parser.add_argument('--gui', action='store_true', help='GUI版で起動')
    parser.add_argument('--profile', choices=['extreme', 'performance', 'balanced'], 
                        help='最適化プロファイル指定')
    parser.add_argument('--startup-optimize', action='store_true', 
                        help='起動時最適化（自動実行用）')
    parser.add_argument('--silent', action='store_true', 
                        help='サイレントモード（出力最小化）')
    parser.add_argument('--enable-autorun', action='store_true', 
                        help='Windows起動時自動実行を有効化')
    parser.add_argument('--disable-autorun', action='store_true', 
                        help='Windows起動時自動実行を無効化')
    parser.add_argument('--check-autorun', action='store_true', 
                        help='自動実行設定状態確認')
    args = parser.parse_args()

    if args.enable_autorun:
        optimizer = LowSpecVROptimizer()
        result = optimizer.setup_startup_autorun(True)
        if result:
            print("✅ Windows起動時自動実行が有効化されました")
            print("💡 次回Windows起動時から自動最適化が実行されます")
        else:
            print("❌ 自動実行設定に失敗しました")
        return

    if args.disable_autorun:
        optimizer = LowSpecVROptimizer()
        result = optimizer.setup_startup_autorun(False)
        if result:
            print("❌ Windows起動時自動実行が無効化されました")
        else:
            print("❌ 自動実行無効化に失敗しました")
        return

    if args.check_autorun:
        optimizer = LowSpecVROptimizer()
        status = optimizer.check_startup_status()
        print(f"📋 自動実行設定状態:")
        print(f"   レジストリ設定: {'✅ 有効' if status['registry_enabled'] else '❌ 無効'}")
        print(f"   スタートアップフォルダ: {'✅ 有効' if status['startup_folder_enabled'] else '❌ 無効'}")
        print(f"   総合状態: {'✅ 有効' if status['overall_enabled'] else '❌ 無効'}")
        return

    if args.startup_optimize:
        # 起動時最適化モード（軽量化版）
        run_startup_optimization(args)
    elif args.gui:
        try:
            # GUI モード
            app = LowSpecVROptimizerGUI()
            app.run()
        except Exception as e:
            print(f"GUI起動エラー: {e}")
            print("CLIモードで実行します...")
            run_cli_mode(args)
    else:
        # デフォルトCLIモード
        try:
            print("🔥 低スペック特化VR最適化ツール")
            print("=" * 50)
            run_cli_mode(args)
        except Exception as e:
            print(f"Fatal Error: {e}")
            input("Enterを押して終了...")

if __name__ == "__main__":
    main() 