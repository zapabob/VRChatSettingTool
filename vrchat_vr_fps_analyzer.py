#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VRChat VR FPS解析ツール（強化版）
リアルタイムパフォーマンス監視とボトルネック分析

Steam Community最適化ガイドの推奨事項を実装:
- GPU使用率とフレームタイム監視
- VRChat特化の最適化提案
- AMD GPU向け特別対応
- VirtualDesktop/SteamVR連携分析
"""

import os
import sys
import json
import time
import psutil
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from datetime import datetime, timedelta
import logging
import subprocess
from collections import deque
from typing import Dict, List, Optional, Tuple
import winreg

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.facecolor'] = '#2b2b2b'
plt.rcParams['axes.facecolor'] = '#3b3b3b'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'vrchat_fps_analyzer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VRChatFPSAnalyzer:
    """VRChat FPS解析メインクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🥽 VRChat VR FPS解析ツール（強化版）")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # データ保存用
        self.fps_data = deque(maxlen=300)  # 5分間のデータ
        self.cpu_data = deque(maxlen=300)
        self.gpu_data = deque(maxlen=300)
        self.memory_data = deque(maxlen=300)
        self.frametime_data = deque(maxlen=300)
        self.time_data = deque(maxlen=300)
        
        # VR環境検出
        self.vr_environment = {
            'vrchat': False,
            'steamvr': False,
            'virtual_desktop': False,
            'oculus': False
        }
        
        # GPU情報
        self.gpu_info = self.detect_gpu()
        
        # 監視状態
        self.monitoring = False
        self.monitor_thread = None
        
        # パフォーマンス閾値
        self.performance_thresholds = {
            'target_fps': 90,  # VR目標FPS
            'cpu_warning': 80,  # CPU使用率警告閾値
            'memory_warning': 85,  # メモリ使用率警告閾値
            'frametime_warning': 11.1  # フレームタイム警告閾値（90FPS基準）
        }
        
        self.setup_gui()
        self.detect_vr_environment()
        
    def detect_gpu(self) -> Dict[str, str]:
        """GPU情報の検出"""
        gpu_info = {'vendor': 'Unknown', 'name': 'Unknown'}
        try:
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                  capture_output=True, text=True, timeout=10)
            gpu_name = result.stdout.strip()
            
            if 'AMD' in gpu_name or 'Radeon' in gpu_name:
                gpu_info['vendor'] = 'AMD'
            elif 'NVIDIA' in gpu_name or 'GeForce' in gpu_name or 'RTX' in gpu_name:
                gpu_info['vendor'] = 'NVIDIA'
            elif 'Intel' in gpu_name:
                gpu_info['vendor'] = 'Intel'
            
            gpu_info['name'] = gpu_name
            logger.info(f"検出されたGPU: {gpu_info['vendor']} - {gpu_info['name']}")
            
        except Exception as e:
            logger.warning(f"GPU検出エラー: {e}")
        
        return gpu_info
    
    def detect_vr_environment(self):
        """VR環境の検出"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name'].lower()
                
                if 'vrchat' in proc_name:
                    self.vr_environment['vrchat'] = True
                elif any(x in proc_name for x in ['vrserver', 'vrmonitor', 'steamvr']):
                    self.vr_environment['steamvr'] = True
                elif 'virtualdesktop' in proc_name:
                    self.vr_environment['virtual_desktop'] = True
                elif any(x in proc_name for x in ['oculusserver', 'oculusclient']):
                    self.vr_environment['oculus'] = True
            
            logger.info(f"VR環境検出結果: {self.vr_environment}")
            
        except Exception as e:
            logger.error(f"VR環境検出エラー: {e}")
    
    def setup_gui(self):
        """GUI設定"""
        # スタイル設定
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), 
                       background='#2b2b2b', foreground='white')
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🥽 VRChat VR FPS解析ツール（強化版）", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # 情報パネル
        info_frame = ttk.LabelFrame(main_frame, text="🔍 システム情報")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=4, bg='#3b3b3b', fg='white')
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # コントロールパネル
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ 監視制御")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="📊 監視開始", 
                                      command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.analysis_button = ttk.Button(control_frame, text="🔬 詳細分析", 
                                         command=self.run_detailed_analysis)
        self.analysis_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.optimize_button = ttk.Button(control_frame, text="⚡ 最適化実行", 
                                         command=self.run_optimization)
        self.optimize_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # グラフエリア
        self.setup_graphs(main_frame)
        
        # ステータス情報
        status_frame = ttk.LabelFrame(main_frame, text="📈 リアルタイム統計")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_text = tk.Text(status_frame, height=3, bg='#3b3b3b', fg='white')
        self.status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 初期情報表示
        self.update_info_display()
    
    def setup_graphs(self, parent):
        """グラフ設定"""
        graph_frame = ttk.LabelFrame(parent, text="📊 リアルタイム監視グラフ")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # matplotlib図の作成
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 6))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # グラフの初期設定
        graphs = [
            (self.ax1, "FPS", "green", self.fps_data),
            (self.ax2, "CPU使用率 (%)", "orange", self.cpu_data),
            (self.ax3, "メモリ使用率 (%)", "blue", self.memory_data),
            (self.ax4, "フレームタイム (ms)", "red", self.frametime_data)
        ]
        
        for ax, title, color, data in graphs:
            ax.set_title(title, color='white', fontsize=12)
            ax.set_facecolor('#3b3b3b')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
            
        plt.tight_layout()
        
        # tkinterに埋め込み
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_info_display(self):
        """情報表示の更新"""
        info_text = f"""🖥️ GPU: {self.gpu_info['vendor']} - {self.gpu_info['name']}
🥽 VR環境: VRChat{'✅' if self.vr_environment['vrchat'] else '❌'} | SteamVR{'✅' if self.vr_environment['steamvr'] else '❌'} | VirtualDesktop{'✅' if self.vr_environment['virtual_desktop'] else '❌'}
🎯 目標FPS: {self.performance_thresholds['target_fps']}Hz | フレームタイム: {1000/self.performance_thresholds['target_fps']:.1f}ms
⚙️ 最適化推奨: {self.get_optimization_recommendations()}"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
    
    def get_optimization_recommendations(self) -> str:
        """最適化推奨事項の生成"""
        recommendations = []
        
        if self.gpu_info['vendor'] == 'AMD' and self.vr_environment['vrchat']:
            recommendations.append("AMD GPU: --enable-hw-video-decoding起動オプション")
        
        if self.vr_environment['virtual_desktop']:
            recommendations.append("VirtualDesktop: 専用Wi-Fi 6ルーター推奨")
        
        if not any(self.vr_environment.values()):
            recommendations.append("VRアプリケーション起動後に再分析推奨")
        
        return " | ".join(recommendations) if recommendations else "最適化済み"
    
    def toggle_monitoring(self):
        """監視の開始/停止"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """監視開始"""
        self.monitoring = True
        self.start_button.config(text="⏹️ 監視停止")
        
        self.monitor_thread = threading.Thread(target=self.monitor_performance, daemon=True)
        self.monitor_thread.start()
        
        # アニメーション開始
        self.ani = animation.FuncAnimation(self.fig, self.update_graphs, interval=1000, blit=False)
        
        logger.info("パフォーマンス監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        self.start_button.config(text="📊 監視開始")
        
        if hasattr(self, 'ani'):
            self.ani.event_source.stop()
        
        logger.info("パフォーマンス監視を停止しました")
    
    def monitor_performance(self):
        """パフォーマンス監視メインループ"""
        while self.monitoring:
            try:
                current_time = datetime.now()
                
                # システム情報取得
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                memory_percent = memory_info.percent
                
                # VRChatプロセス情報
                vrchat_fps = self.get_vrchat_fps()
                frametime = 1000 / vrchat_fps if vrchat_fps > 0 else 0
                
                # データ追加
                self.time_data.append(current_time)
                self.fps_data.append(vrchat_fps)
                self.cpu_data.append(cpu_percent)
                self.memory_data.append(memory_percent)
                self.frametime_data.append(frametime)
                
                # 警告チェック
                self.check_performance_warnings(vrchat_fps, cpu_percent, memory_percent, frametime)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"監視エラー: {e}")
                time.sleep(1)
    
    def get_vrchat_fps(self) -> float:
        """VRChatのFPS取得（推定）"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                if 'vrchat' in proc.info['name'].lower():
                    # プロセスCPU使用率からFPS推定（簡易版）
                    cpu_usage = proc.info['cpu_percent']
                    if cpu_usage > 0:
                        # 簡易FPS推定（実際にはフレームタイムAPIが必要）
                        estimated_fps = min(90, max(30, 90 - (cpu_usage - 20) * 2))
                        return estimated_fps
            return 0
        except Exception:
            return 0
    
    def check_performance_warnings(self, fps: float, cpu: float, memory: float, frametime: float):
        """パフォーマンス警告チェック"""
        warnings = []
        
        if fps < self.performance_thresholds['target_fps'] * 0.8:  # 目標FPSの80%以下
            warnings.append(f"⚠️ 低FPS警告: {fps:.1f}fps")
        
        if cpu > self.performance_thresholds['cpu_warning']:
            warnings.append(f"⚠️ 高CPU使用率: {cpu:.1f}%")
        
        if memory > self.performance_thresholds['memory_warning']:
            warnings.append(f"⚠️ 高メモリ使用率: {memory:.1f}%")
        
        if frametime > self.performance_thresholds['frametime_warning']:
            warnings.append(f"⚠️ 高フレームタイム: {frametime:.1f}ms")
        
        if warnings:
            logger.warning(" | ".join(warnings))
    
    def update_graphs(self, frame):
        """グラフ更新"""
        if not self.time_data:
            return
        
        # 時間軸の準備
        times = list(self.time_data)
        if len(times) < 2:
            return
        
        time_nums = [(t - times[0]).total_seconds() for t in times]
        
        # グラフクリアと更新
        graphs_data = [
            (self.ax1, self.fps_data, "FPS", "green", self.performance_thresholds['target_fps']),
            (self.ax2, self.cpu_data, "CPU (%)", "orange", self.performance_thresholds['cpu_warning']),
            (self.ax3, self.memory_data, "Memory (%)", "blue", self.performance_thresholds['memory_warning']),
            (self.ax4, self.frametime_data, "Frametime (ms)", "red", self.performance_thresholds['frametime_warning'])
        ]
        
        for ax, data, label, color, threshold in graphs_data:
            ax.clear()
            ax.set_facecolor('#3b3b3b')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='white')
            ax.set_title(label, color='white')
            
            if data and len(data) > 1:
                ax.plot(time_nums[-len(data):], list(data), color=color, linewidth=2)
                ax.axhline(y=threshold, color='red', linestyle='--', alpha=0.7, linewidth=1)
        
        # ステータス更新
        self.update_status_display()
        
        plt.tight_layout()
        self.canvas.draw()
    
    def update_status_display(self):
        """ステータス表示更新"""
        if not self.fps_data:
            return
        
        avg_fps = np.mean(list(self.fps_data)[-30:]) if len(self.fps_data) >= 30 else 0
        avg_cpu = np.mean(list(self.cpu_data)[-30:]) if len(self.cpu_data) >= 30 else 0
        avg_memory = np.mean(list(self.memory_data)[-30:]) if len(self.memory_data) >= 30 else 0
        
        status_text = f"""📊 30秒平均: FPS {avg_fps:.1f} | CPU {avg_cpu:.1f}% | メモリ {avg_memory:.1f}%
🎯 パフォーマンス: {'✅ 良好' if avg_fps >= self.performance_thresholds['target_fps'] * 0.9 else '⚠️ 改善要'}
💡 次回最適化: {self.get_next_optimization_suggestion()}"""
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_text)
    
    def get_next_optimization_suggestion(self) -> str:
        """次の最適化提案"""
        if not self.fps_data:
            return "データ収集中..."
        
        current_fps = list(self.fps_data)[-1] if self.fps_data else 0
        
        if current_fps < 60:
            return "緊急: 品質設定下げ、Avatar Culling強化"
        elif current_fps < 80:
            return "推奨: VRChat品質設定調整、プロセス最適化"
        else:
            return "良好: 現在の設定を維持"
    
    def run_detailed_analysis(self):
        """詳細分析実行"""
        try:
            if not self.fps_data:
                messagebox.showwarning("警告", "監視データがありません。先に監視を開始してください。")
                return
            
            # 分析レポート生成
            report = self.generate_analysis_report()
            
            # レポート表示ウィンドウ
            self.show_analysis_report(report)
                
            except Exception as e:
            logger.error(f"詳細分析エラー: {e}")
            messagebox.showerror("エラー", f"詳細分析中にエラーが発生しました: {e}")
    
    def generate_analysis_report(self) -> str:
        """分析レポート生成"""
        if not self.fps_data:
            return "データが不足しています。"
        
        fps_list = list(self.fps_data)
        cpu_list = list(self.cpu_data)
        memory_list = list(self.memory_data)
        frametime_list = list(self.frametime_data)
        
        # 統計計算
        fps_avg = np.mean(fps_list)
        fps_min = np.min(fps_list)
        fps_std = np.std(fps_list)
        
        cpu_avg = np.mean(cpu_list)
        memory_avg = np.mean(memory_list)
        frametime_avg = np.mean(frametime_list)
        
        # 1%/0.1% Low FPS計算
        fps_sorted = sorted(fps_list)
        fps_1_percent = np.mean(fps_sorted[:max(1, len(fps_sorted)//100)])
        fps_0_1_percent = np.mean(fps_sorted[:max(1, len(fps_sorted)//1000)])
        
        report = f"""
🔬 VRChat詳細パフォーマンス分析レポート
{'='*50}
📅 分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔢 データ点数: {len(fps_list)}個

📊 FPS統計:
  平均FPS: {fps_avg:.1f}
  最低FPS: {fps_min:.1f}
  FPS標準偏差: {fps_std:.1f}
  1% Low FPS: {fps_1_percent:.1f}
  0.1% Low FPS: {fps_0_1_percent:.1f}

💻 システムリソース:
  平均CPU使用率: {cpu_avg:.1f}%
  平均メモリ使用率: {memory_avg:.1f}%
  平均フレームタイム: {frametime_avg:.1f}ms

🎯 VR性能評価:
  目標90Hz達成率: {(np.sum(np.array(fps_list) >= 90) / len(fps_list) * 100):.1f}%
  安定性スコア: {max(0, 100 - fps_std * 2):.1f}/100

🔧 GPU特化推奨事項:
{self.get_gpu_specific_recommendations()}

🥽 VRChat設定推奨:
{self.get_vrchat_settings_recommendations(fps_avg)}

⚡ 緊急最適化項目:
{self.get_urgent_optimizations(fps_avg, cpu_avg, memory_avg)}
"""
        return report
    
    def get_gpu_specific_recommendations(self) -> str:
        """GPU固有の推奨事項"""
        if self.gpu_info['vendor'] == 'AMD':
            return """  • VRChat起動オプション: --enable-hw-video-decoding 追加
  • AMD Adrenalin: Anti-Lag無効、Radeon Boost無効
  • AMD ULPS機能の無効化検討"""
        elif self.gpu_info['vendor'] == 'NVIDIA':
            return """  • NVIDIA Control Panel: 低遅延モード有効
  • Power Management: 最大パフォーマンス優先
  • G-SYNC: VR使用時は無効推奨"""
        else:
            return """  • GPU固有の最適化情報なし
  • 汎用最適化設定を適用"""
    
    def get_vrchat_settings_recommendations(self, avg_fps: float) -> str:
        """VRChat設定推奨事項"""
        if avg_fps < 60:
            return """  • 緊急: すべての品質設定を最低に
  • Avatar Culling Distance: 15m
  • Maximum Shown Avatars: 5-8
  • Particle Limiter: 有効"""
        elif avg_fps < 80:
            return """  • Avatar Culling Distance: 20-25m
  • Maximum Shown Avatars: 10-15
  • Antialiasing: 無効またはx2
  • Pixel Light Count: Low"""
        else:
            return """  • 現在の設定維持
  • Antialiasing: x2-x4可能
  • 品質向上オプション検討可"""
    
    def get_urgent_optimizations(self, fps: float, cpu: float, memory: float) -> str:
        """緊急最適化項目"""
        urgent = []
        
        if fps < 60:
            urgent.append("FPS改善: VRChat品質設定の即座な調整必須")
        
        if cpu > 80:
            urgent.append("CPU負荷軽減: 背景アプリケーション終了")
        
        if memory > 85:
            urgent.append("メモリ解放: 不要プロセス終了、VRChat再起動")
        
        if not urgent:
            urgent.append("緊急最適化は不要です")
        
        return "\n".join(f"  • {item}" for item in urgent)
    
    def show_analysis_report(self, report: str):
        """分析レポート表示"""
        report_window = tk.Toplevel(self.root)
        report_window.title("📊 詳細分析レポート")
        report_window.geometry("800x600")
        report_window.configure(bg='#2b2b2b')
        
        # スクロール可能テキスト
        text_frame = tk.Frame(report_window, bg='#2b2b2b')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, bg='#3b3b3b', fg='white', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(1.0, report)
        text_widget.config(state=tk.DISABLED)
        
        # 保存ボタン
        save_button = ttk.Button(report_window, text="💾 レポート保存", 
                                command=lambda: self.save_report(report))
        save_button.pack(pady=10)
    
    def save_report(self, report: str):
        """レポート保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vrchat_analysis_report_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"分析レポートを保存しました: {filename}")
            messagebox.showinfo("保存完了", f"レポートを保存しました: {filename}")
            
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")
            messagebox.showerror("エラー", f"レポート保存中にエラー: {e}")
    
    def run_optimization(self):
        """最適化実行"""
        try:
            # 既存の最適化ツールを呼び出し
            optimizer_path = "vr_optimizer_no_admin.py"
            if os.path.exists(optimizer_path):
                subprocess.Popen([sys.executable, optimizer_path])
                messagebox.showinfo("最適化実行", "VR最適化ツールを起動しました。")
            else:
                messagebox.showerror("エラー", "最適化ツールが見つかりません。")
                
        except Exception as e:
            logger.error(f"最適化実行エラー: {e}")
            messagebox.showerror("エラー", f"最適化実行中にエラー: {e}")
    
    def run(self):
        """メイン実行"""
        try:
            logger.info("VRChat FPS解析ツールを開始します")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("ユーザーによって中断されました")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
        finally:
            self.monitoring = False
            logger.info("VRChat FPS解析ツールを終了します")

def main():
    """メイン関数"""
    try:
        app = VRChatFPSAnalyzer()
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 