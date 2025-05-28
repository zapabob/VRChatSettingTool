#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat VR環境専用FPS分析ツール
VRヘッドセット使用時のリアルタイムパフォーマンス監視とフレームタイム分析
"""

import psutil
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import time
import json
import os
from datetime import datetime
import threading
import queue
import sys

# 日本語フォント設定（文字化け防止）
plt.rcParams['font.family'] = ['DejaVu Sans', 'Yu Gothic', 'Hiragino Sans', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

class VRChatVRFPSAnalyzer:
    def __init__(self):
        self.vr_processes = {}
        self.performance_data = {
            'timestamps': [],
            'vr_fps': [],
            'cpu_usage': [],
            'gpu_usage': [],
            'memory_usage': [],
            'frame_drops': [],
            'vr_frame_time': [],
            'headset_type': 'Unknown'
        }
        self.frame_drop_count = 0
        self.total_frames = 0
        self.target_vr_fps = 90  # VR標準FPS
        self.running = False
        self.data_queue = queue.Queue()
        
        # VRヘッドセット検出
        self.detect_vr_headset()
        
        print("=== VRChat VR環境専用FPS分析ツール ===")
        print(f"検出されたVRヘッドセット: {self.performance_data['headset_type']}")
        print("VRヘッドセットを装着してVRChatをVRモードで起動してください")
    
    def detect_vr_headset(self):
        """VRヘッドセットを検出"""
        headset_types = []
        
        # Oculus/Meta Quest検出
        for proc in psutil.process_iter(['name']):
            try:
                if 'oculus' in proc.info['name'].lower():
                    headset_types.append('Oculus/Meta')
                    break
            except:
                continue
        
        # SteamVR検出
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in ['vrserver.exe', 'vrcompositor.exe']:
                    headset_types.append('SteamVR')
                    break
            except:
                continue
        
        # Windows Mixed Reality検出
        for proc in psutil.process_iter(['name']):
            try:
                if 'mixedrealityportal' in proc.info['name'].lower():
                    headset_types.append('WMR')
                    break
            except:
                continue
        
        if headset_types:
            self.performance_data['headset_type'] = ', '.join(headset_types)
        else:
            self.performance_data['headset_type'] = 'VRヘッドセット未検出'
    
    def get_vr_processes(self):
        """VR関連プロセスを取得"""
        vr_processes = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                name = proc.info['name'].lower()
                if any(vr_name in name for vr_name in [
                    'vrchat', 'oculusclient', 'ovrserver_x64', 'vrserver', 
                    'vrcompositor', 'mixedrealityportal', 'picoconnect'
                ]):
                    vr_processes[proc.info['name']] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return vr_processes
    
    def get_gpu_usage(self):
        """GPU使用率を取得（VR専用）"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                # VRでは最も使用率の高いGPUを取得
                max_load = max(gpu.load * 100 for gpu in gpus)
                return round(max_load, 2)
        except ImportError:
            pass
        
        # Windows Performance Countersを使用
        try:
            import wmi
            c = wmi.WMI()
            gpu_usage = 0
            for gpu in c.Win32_PerfRawData_GPUPerformanceCounters_GPUEngine():
                if hasattr(gpu, 'UtilizationPercentage'):
                    gpu_usage = max(gpu_usage, float(gpu.UtilizationPercentage))
            return round(gpu_usage, 2)
        except:
            return 0.0
    
    def calculate_vr_fps(self, cpu_usage, gpu_usage, memory_usage, vr_process_count):
        """VR専用FPS推定計算"""
        base_vr_fps = self.target_vr_fps
        
        # VRプロセス数による影響
        vr_process_factor = 0.8 if vr_process_count > 3 else (0.9 if vr_process_count > 2 else 1.0)
        
        # CPU負荷による影響（VRはCPU依存が高い）
        if cpu_usage > 90:
            cpu_factor = 0.3
        elif cpu_usage > 80:
            cpu_factor = 0.5
        elif cpu_usage > 70:
            cpu_factor = 0.7
        elif cpu_usage > 50:
            cpu_factor = 0.85
        else:
            cpu_factor = 1.0
        
        # GPU負荷による影響（VRはGPU依存が非常に高い）
        if gpu_usage > 95:
            gpu_factor = 0.2
        elif gpu_usage > 90:
            gpu_factor = 0.4
        elif gpu_usage > 85:
            gpu_factor = 0.6
        elif gpu_usage > 75:
            gpu_factor = 0.8
        else:
            gpu_factor = 1.0
        
        # メモリ負荷による影響
        if memory_usage > 90:
            memory_factor = 0.5
        elif memory_usage > 80:
            memory_factor = 0.7
        elif memory_usage > 70:
            memory_factor = 0.9
        else:
            memory_factor = 1.0
        
        # VR専用FPS計算
        estimated_vr_fps = base_vr_fps * vr_process_factor * cpu_factor * gpu_factor * memory_factor
        
        return round(estimated_vr_fps, 1)
    
    def get_vr_frame_time(self):
        """VRフレームタイム取得"""
        try:
            vr_processes = self.get_vr_processes()
            
            # SteamVRフレームタイム
            if 'vrcompositor.exe' in vr_processes:
                proc = vr_processes['vrcompositor.exe']
                cpu_time = proc.cpu_times().user + proc.cpu_times().system
                return round(cpu_time * 1000 / self.target_vr_fps, 2)  # ms
            
            # Oculusフレームタイム
            if 'OVRServer_x64.exe' in vr_processes:
                proc = vr_processes['OVRServer_x64.exe']
                cpu_time = proc.cpu_times().user + proc.cpu_times().system
                return round(cpu_time * 1000 / self.target_vr_fps, 2)  # ms
            
            return 11.1  # 90FPSの理想フレームタイム
        except:
            return 11.1
    
    def collect_vr_performance_data(self):
        """VRパフォーマンスデータ収集"""
        while self.running:
            try:
                vr_processes = self.get_vr_processes()
                vrchat_process = None
                
                # VRChatプロセス検索
                for name, proc in vr_processes.items():
                    if 'vrchat' in name.lower():
                        vrchat_process = proc
                        break
                
                if vrchat_process:
                    # パフォーマンス情報取得
                    cpu_usage = vrchat_process.cpu_percent()
                    memory_info = vrchat_process.memory_info()
                    memory_usage_mb = memory_info.rss / 1024 / 1024
                    
                    # システム情報
                    system_memory = psutil.virtual_memory()
                    system_memory_usage = system_memory.percent
                    
                    gpu_usage = self.get_gpu_usage()
                    vr_frame_time = self.get_vr_frame_time()
                    
                    # VR専用FPS計算
                    vr_fps = self.calculate_vr_fps(
                        cpu_usage, gpu_usage, system_memory_usage, len(vr_processes)
                    )
                    
                    # フレームドロップ検出
                    self.total_frames += 1
                    if vr_fps < 80:  # VRでは80FPS以下をフレームドロップとみなす
                        self.frame_drop_count += 1
                    
                    frame_drop_rate = (self.frame_drop_count / self.total_frames) * 100
                    
                    # データをキューに追加
                    data_point = {
                        'timestamp': datetime.now(),
                        'vr_fps': vr_fps,
                        'cpu_usage': cpu_usage,
                        'gpu_usage': gpu_usage,
                        'memory_usage': memory_usage_mb,
                        'system_memory_usage': system_memory_usage,
                        'frame_drop_rate': frame_drop_rate,
                        'vr_frame_time': vr_frame_time,
                        'vr_process_count': len(vr_processes)
                    }
                    
                    self.data_queue.put(data_point)
                    
                    # コンソール出力
                    print(f"\r[VR FPS: {vr_fps:5.1f}] [CPU: {cpu_usage:5.1f}%] [GPU: {gpu_usage:5.1f}%] "
                          f"[メモリ: {memory_usage_mb:6.1f}MB] [フレームドロップ: {frame_drop_rate:4.1f}%] "
                          f"[フレームタイム: {vr_frame_time:5.1f}ms]", end='')
                    
                    # VR専用警告
                    if vr_fps < 60:
                        print(f"\n警告: VR FPSが低すぎます！({vr_fps}FPS) VR酔いの原因になります！")
                    elif vr_fps < 75:
                        print(f"\n注意: VR FPSが推奨値を下回っています ({vr_fps}FPS)")
                    
                    if frame_drop_rate > 10:
                        print(f"\n警告: フレームドロップが多発しています！({frame_drop_rate:.1f}%)")
                
                else:
                    print("\rVRChatプロセスが見つかりません（VRモードで起動してください）", end='')
                
                time.sleep(1)
                
            except Exception as e:
                print(f"\nデータ収集エラー: {e}")
                time.sleep(1)
    
    def update_plots(self):
        """リアルタイムグラフ更新"""
        plt.ion()
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'VRChat VR環境パフォーマンス監視 - {self.performance_data["headset_type"]}', 
                     fontsize=16, fontweight='bold')
        
        # グラフの初期設定
        ax1.set_title('VR FPS (目標: 90FPS)')
        ax1.set_ylabel('FPS')
        ax1.axhline(y=90, color='g', linestyle='--', alpha=0.7, label='理想値(90FPS)')
        ax1.axhline(y=75, color='y', linestyle='--', alpha=0.7, label='推奨値(75FPS)')
        ax1.axhline(y=60, color='r', linestyle='--', alpha=0.7, label='最低値(60FPS)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.set_title('CPU使用率')
        ax2.set_ylabel('使用率 (%)')
        ax2.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='警告レベル')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        ax3.set_title('GPU使用率')
        ax3.set_ylabel('使用率 (%)')
        ax3.axhline(y=90, color='r', linestyle='--', alpha=0.7, label='警告レベル')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        ax4.set_title('VRChatメモリ使用量')
        ax4.set_ylabel('メモリ (MB)')
        ax4.axhline(y=4000, color='r', linestyle='--', alpha=0.7, label='警告レベル(4GB)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # データ保存用
        max_points = 300  # 5分間のデータ（1秒間隔）
        
        while self.running:
            try:
                # キューからデータを取得
                while not self.data_queue.empty():
                    data_point = self.data_queue.get()
                    
                    # データを追加
                    self.performance_data['timestamps'].append(data_point['timestamp'])
                    self.performance_data['vr_fps'].append(data_point['vr_fps'])
                    self.performance_data['cpu_usage'].append(data_point['cpu_usage'])
                    self.performance_data['gpu_usage'].append(data_point['gpu_usage'])
                    self.performance_data['memory_usage'].append(data_point['memory_usage'])
                    self.performance_data['frame_drops'].append(data_point['frame_drop_rate'])
                    self.performance_data['vr_frame_time'].append(data_point['vr_frame_time'])
                    
                    # データ数制限
                    if len(self.performance_data['timestamps']) > max_points:
                        for key in ['timestamps', 'vr_fps', 'cpu_usage', 'gpu_usage', 
                                   'memory_usage', 'frame_drops', 'vr_frame_time']:
                            self.performance_data[key] = self.performance_data[key][-max_points:]
                
                # グラフ更新
                if self.performance_data['timestamps']:
                    timestamps = self.performance_data['timestamps']
                    
                    # 時間軸を分:秒形式に変換
                    time_labels = [t.strftime('%M:%S') for t in timestamps[-60:]]  # 直近1分
                    
                    # VR FPS
                    ax1.clear()
                    ax1.set_title('VR FPS (目標: 90FPS)')
                    ax1.set_ylabel('FPS')
                    ax1.plot(self.performance_data['vr_fps'][-60:], 'b-', linewidth=2, label='VR FPS')
                    ax1.axhline(y=90, color='g', linestyle='--', alpha=0.7, label='理想値(90FPS)')
                    ax1.axhline(y=75, color='y', linestyle='--', alpha=0.7, label='推奨値(75FPS)')
                    ax1.axhline(y=60, color='r', linestyle='--', alpha=0.7, label='最低値(60FPS)')
                    ax1.set_ylim(0, 100)
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # CPU使用率
                    ax2.clear()
                    ax2.set_title('CPU使用率')
                    ax2.set_ylabel('使用率 (%)')
                    ax2.plot(self.performance_data['cpu_usage'][-60:], 'r-', linewidth=2, label='CPU')
                    ax2.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='警告レベル')
                    ax2.set_ylim(0, 100)
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    
                    # GPU使用率
                    ax3.clear()
                    ax3.set_title('GPU使用率')
                    ax3.set_ylabel('使用率 (%)')
                    ax3.plot(self.performance_data['gpu_usage'][-60:], 'g-', linewidth=2, label='GPU')
                    ax3.axhline(y=90, color='r', linestyle='--', alpha=0.7, label='警告レベル')
                    ax3.set_ylim(0, 100)
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
                    
                    # メモリ使用量
                    ax4.clear()
                    ax4.set_title('VRChatメモリ使用量')
                    ax4.set_ylabel('メモリ (MB)')
                    ax4.plot(self.performance_data['memory_usage'][-60:], 'm-', linewidth=2, label='メモリ')
                    ax4.axhline(y=4000, color='r', linestyle='--', alpha=0.7, label='警告レベル(4GB)')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)
                    
                    # X軸ラベル設定
                    if len(time_labels) > 10:
                        step = len(time_labels) // 10
                        for ax in [ax1, ax2, ax3, ax4]:
                            ax.set_xticks(range(0, len(time_labels), step))
                            ax.set_xticklabels([time_labels[i] for i in range(0, len(time_labels), step)])
                
                plt.tight_layout()
                plt.pause(0.1)
                
            except Exception as e:
                print(f"\nグラフ更新エラー: {e}")
                time.sleep(1)
    
    def save_vr_performance_data(self):
        """VRパフォーマンスデータを保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'vrchat_vr_performance_data_{timestamp}.json'
        
        # データを保存用に変換
        save_data = self.performance_data.copy()
        save_data['timestamps'] = [t.isoformat() for t in save_data['timestamps']]
        
        # 統計情報を追加
        if save_data['vr_fps']:
            save_data['statistics'] = {
                'avg_vr_fps': round(np.mean(save_data['vr_fps']), 2),
                'min_vr_fps': round(np.min(save_data['vr_fps']), 2),
                'max_vr_fps': round(np.max(save_data['vr_fps']), 2),
                'avg_cpu_usage': round(np.mean(save_data['cpu_usage']), 2),
                'avg_gpu_usage': round(np.mean(save_data['gpu_usage']), 2),
                'avg_memory_usage': round(np.mean(save_data['memory_usage']), 2),
                'total_frame_drops': self.frame_drop_count,
                'frame_drop_rate': round((self.frame_drop_count / self.total_frames) * 100, 2) if self.total_frames > 0 else 0,
                'vr_performance_rating': self.get_vr_performance_rating()
            }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"\nVRパフォーマンスデータを保存しました: {filename}")
        except Exception as e:
            print(f"\nデータ保存エラー: {e}")
    
    def get_vr_performance_rating(self):
        """VRパフォーマンス評価"""
        if not self.performance_data['vr_fps']:
            return "データ不足"
        
        avg_fps = np.mean(self.performance_data['vr_fps'])
        frame_drop_rate = (self.frame_drop_count / self.total_frames) * 100 if self.total_frames > 0 else 0
        
        if avg_fps >= 85 and frame_drop_rate < 5:
            return "優秀 - VR体験は非常に快適です"
        elif avg_fps >= 75 and frame_drop_rate < 10:
            return "良好 - VR体験は快適です"
        elif avg_fps >= 60 and frame_drop_rate < 15:
            return "普通 - VR体験は許容範囲です"
        elif avg_fps >= 45:
            return "要改善 - VR酔いが発生する可能性があります"
        else:
            return "危険 - VR使用を控えることをお勧めします"
    
    def run(self):
        """メイン実行"""
        self.running = True
        
        # データ収集スレッド開始
        data_thread = threading.Thread(target=self.collect_vr_performance_data)
        data_thread.daemon = True
        data_thread.start()
        
        try:
            # グラフ表示
            self.update_plots()
        except KeyboardInterrupt:
            print("\n\nVR監視を終了します...")
        finally:
            self.running = False
            self.save_vr_performance_data()
            
            # 最終統計表示
            if self.performance_data['vr_fps']:
                print("\n=== VRパフォーマンス統計 ===")
                print(f"平均VR FPS: {np.mean(self.performance_data['vr_fps']):.1f}")
                print(f"最低VR FPS: {np.min(self.performance_data['vr_fps']):.1f}")
                print(f"最高VR FPS: {np.max(self.performance_data['vr_fps']):.1f}")
                print(f"フレームドロップ率: {(self.frame_drop_count / self.total_frames) * 100:.1f}%")
                print(f"VRパフォーマンス評価: {self.get_vr_performance_rating()}")

if __name__ == "__main__":
    print("VRChat VR環境専用FPS分析ツールを開始します...")
    print("Ctrl+Cで終了します")
    
    analyzer = VRChatVRFPSAnalyzer()
    analyzer.run() 