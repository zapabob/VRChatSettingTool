#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VR環境高度最適化ツール（管理者権限不要版）
VirtualDesktop、SteamVR、VRChat用PC最適化

高度な最適化機能とリアルタイム監視を提供します。
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
from typing import Dict, List, Optional, Tuple
import logging
from tqdm import tqdm
import configparser

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'vr_advanced_optimizer_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VRAdvancedOptimizerGUI:
    """VR高度最適化ツールのGUIクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VR環境高度最適化ツール（管理者権限不要版）")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # 設定ファイル
        self.config_file = "vr_optimizer_config.ini"
        self.load_config()
        
        # 最適化エンジン
        self.optimizer = VRAdvancedOptimizer()
        
        # 監視スレッド
        self.monitoring = False
        self.monitor_thread = None
        
        self.setup_gui()
        
    def load_config(self):
        """設定ファイルの読み込み"""
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # デフォルト設定
            self.config['OPTIMIZATION'] = {
                'level': 'balanced',
                'auto_optimize': 'false',
                'monitor_interval': '5',
                'enable_network_opt': 'true',
                'enable_process_opt': 'true',
                'enable_power_opt': 'true',
                'enable_gpu_opt': 'true',
                'enable_memory_opt': 'true'
            }
            self.save_config()
    
    def save_config(self):
        """設定ファイルの保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def setup_gui(self):
        """GUI設定"""
        # スタイル設定
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#2b2b2b', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#2b2b2b', foreground='white')
        style.configure('Info.TLabel', font=('Arial', 10), background='#2b2b2b', foreground='white')
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🥽 VR環境高度最適化ツール", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="VirtualDesktop、SteamVR、VRChat用PC最適化（管理者権限不要）", style='Info.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # ノートブック（タブ）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # タブ作成
        self.create_optimization_tab()
        self.create_monitoring_tab()
        self.create_settings_tab()
        self.create_log_tab()
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def create_optimization_tab(self):
        """最適化タブの作成"""
        opt_frame = ttk.Frame(self.notebook)
        self.notebook.add(opt_frame, text="🚀 最適化")
        
        # VR環境検出
        detect_frame = ttk.LabelFrame(opt_frame, text="🔍 VR環境検出")
        detect_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.detect_button = ttk.Button(detect_frame, text="VR環境を検出", command=self.detect_vr_environment)
        self.detect_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.detect_result = tk.Text(detect_frame, height=4, width=60)
        self.detect_result.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 最適化オプション
        options_frame = ttk.LabelFrame(opt_frame, text="⚙️ 最適化オプション")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.opt_vars = {}
        options = [
            ('network_opt', 'ネットワーク最適化'),
            ('process_opt', 'プロセス優先度最適化'),
            ('power_opt', '電源設定最適化'),
            ('gpu_opt', 'GPU設定最適化'),
            ('memory_opt', 'メモリ設定最適化'),
            ('vr_specific_opt', 'VR専用設定最適化')
        ]
        
        for i, (key, text) in enumerate(options):
            var = tk.BooleanVar(value=True)
            self.opt_vars[key] = var
            cb = ttk.Checkbutton(options_frame, text=text, variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # 最適化レベル
        level_frame = ttk.LabelFrame(opt_frame, text="📊 最適化レベル")
        level_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.opt_level = tk.StringVar(value=self.config.get('OPTIMIZATION', 'level', fallback='balanced'))
        levels = [('conservative', '控えめ'), ('balanced', 'バランス'), ('aggressive', '積極的')]
        
        for value, text in levels:
            rb = ttk.Radiobutton(level_frame, text=text, variable=self.opt_level, value=value)
            rb.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 実行ボタン
        button_frame = ttk.Frame(opt_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.optimize_button = ttk.Button(button_frame, text="🚀 最適化実行", command=self.run_optimization)
        self.optimize_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="🔄 設定リセット", command=self.reset_settings)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 進行状況
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(opt_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
    def create_monitoring_tab(self):
        """監視タブの作成"""
        mon_frame = ttk.Frame(self.notebook)
        self.notebook.add(mon_frame, text="📊 リアルタイム監視")
        
        # 監視制御
        control_frame = ttk.LabelFrame(mon_frame, text="🎛️ 監視制御")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.monitor_button = ttk.Button(control_frame, text="📊 監視開始", command=self.toggle_monitoring)
        self.monitor_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.auto_optimize_var = tk.BooleanVar(value=self.config.getboolean('OPTIMIZATION', 'auto_optimize', fallback=False))
        auto_cb = ttk.Checkbutton(control_frame, text="自動最適化", variable=self.auto_optimize_var)
        auto_cb.pack(side=tk.LEFT, padx=10, pady=5)
        
        # システム情報表示
        info_frame = ttk.LabelFrame(mon_frame, text="💻 システム情報")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.system_info = scrolledtext.ScrolledText(info_frame, height=15, width=80)
        self.system_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_settings_tab(self):
        """設定タブの作成"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ 設定")
        
        # 監視間隔設定
        interval_frame = ttk.LabelFrame(settings_frame, text="⏱️ 監視間隔")
        interval_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interval_frame, text="監視間隔（秒）:").pack(side=tk.LEFT, padx=5, pady=5)
        self.interval_var = tk.StringVar(value=self.config.get('OPTIMIZATION', 'monitor_interval', fallback='5'))
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 設定保存
        save_button = ttk.Button(settings_frame, text="💾 設定保存", command=self.save_settings)
        save_button.pack(pady=10)
        
        # 設定情報表示
        config_frame = ttk.LabelFrame(settings_frame, text="📋 現在の設定")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.config_display = scrolledtext.ScrolledText(config_frame, height=10, width=80)
        self.config_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_config_display()
        
    def create_log_tab(self):
        """ログタブの作成"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📝 ログ")
        
        # ログ制御
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        clear_button = ttk.Button(log_control_frame, text="🗑️ ログクリア", command=self.clear_log)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        export_button = ttk.Button(log_control_frame, text="📤 ログエクスポート", command=self.export_log)
        export_button.pack(side=tk.LEFT, padx=5)
        
        # ログ表示
        self.log_display = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def detect_vr_environment(self):
        """VR環境検出"""
        self.status_var.set("VR環境を検出中...")
        self.detect_result.delete(1.0, tk.END)
        
        detected = self.optimizer.detect_vr_environment()
        
        result_text = "🔍 VR環境検出結果:\n"
        for app, status in detected.items():
            emoji = "✅" if status else "❌"
            result_text += f"{emoji} {app}: {'検出' if status else '未検出'}\n"
        
        self.detect_result.insert(tk.END, result_text)
        self.status_var.set("VR環境検出完了")
        
    def run_optimization(self):
        """最適化実行"""
        self.status_var.set("最適化を実行中...")
        self.optimize_button.config(state='disabled')
        
        # 設定を最適化エンジンに反映
        self.optimizer.config['optimization_level'] = self.opt_level.get()
        
        # 最適化実行（別スレッドで）
        def optimize_thread():
            try:
                results = self.optimizer.run_optimization()
                
                # 結果をログに表示
                self.root.after(0, lambda: self.show_optimization_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("エラー", f"最適化中にエラーが発生しました: {e}"))
            finally:
                self.root.after(0, lambda: self.optimize_button.config(state='normal'))
                self.root.after(0, lambda: self.status_var.set("最適化完了"))
        
        threading.Thread(target=optimize_thread, daemon=True).start()
        
    def show_optimization_results(self, results):
        """最適化結果の表示"""
        report = self.optimizer.generate_report()
        self.log_display.insert(tk.END, f"\n{report}\n")
        self.log_display.see(tk.END)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            messagebox.showinfo("完了", "🎉 すべての最適化が正常に完了しました！")
        elif success_count > total_count // 2:
            messagebox.showinfo("部分完了", f"✅ 最適化が部分的に完了しました ({success_count}/{total_count})")
        else:
            messagebox.showwarning("問題発生", f"⚠️ 最適化で問題が発生しました ({success_count}/{total_count})")
    
    def toggle_monitoring(self):
        """監視の開始/停止"""
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """監視開始"""
        self.monitoring = True
        self.monitor_button.config(text="⏹️ 監視停止")
        self.status_var.set("リアルタイム監視中...")
        
        def monitor_thread():
            while self.monitoring:
                try:
                    # システム情報取得
                    info = self.get_system_info()
                    self.root.after(0, lambda: self.update_system_info(info))
                    
                    # 自動最適化チェック
                    if self.auto_optimize_var.get():
                        self.check_auto_optimization()
                    
                    time.sleep(int(self.interval_var.get()))
                    
                except Exception as e:
                    logger.error(f"監視エラー: {e}")
                    break
        
        self.monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        self.monitor_button.config(text="📊 監視開始")
        self.status_var.set("監視停止")
    
    def get_system_info(self):
        """システム情報取得"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # VRプロセス確認
        vr_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if any(vr_name.lower() in proc.info['name'].lower() 
                      for vr_name in ['vrchat', 'steam', 'virtual', 'oculus']):
                    vr_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used // (1024**3),
            'memory_total_gb': memory.total // (1024**3),
            'vr_processes': vr_processes
        }
    
    def update_system_info(self, info):
        """システム情報表示更新"""
        self.system_info.delete(1.0, tk.END)
        
        text = f"🕒 更新時刻: {info['timestamp']}\n\n"
        text += f"💻 システム状態:\n"
        text += f"  CPU使用率: {info['cpu_percent']:.1f}%\n"
        text += f"  メモリ使用率: {info['memory_percent']:.1f}% ({info['memory_used_gb']:.1f}GB / {info['memory_total_gb']:.1f}GB)\n\n"
        
        text += f"🎮 VR関連プロセス:\n"
        if info['vr_processes']:
            for proc in info['vr_processes']:
                text += f"  {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}%, MEM: {proc['memory_percent']:.1f}%\n"
        else:
            text += "  VR関連プロセスが検出されませんでした\n"
        
        self.system_info.insert(tk.END, text)
    
    def check_auto_optimization(self):
        """自動最適化チェック"""
        # CPU使用率が高い場合の自動最適化
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            logger.info("CPU使用率が高いため、自動最適化を実行します")
            self.optimizer.optimize_process_priorities()
    
    def save_settings(self):
        """設定保存"""
        self.config.set('OPTIMIZATION', 'level', self.opt_level.get())
        self.config.set('OPTIMIZATION', 'auto_optimize', str(self.auto_optimize_var.get()).lower())
        self.config.set('OPTIMIZATION', 'monitor_interval', self.interval_var.get())
        
        for key, var in self.opt_vars.items():
            self.config.set('OPTIMIZATION', f'enable_{key}', str(var.get()).lower())
        
        self.save_config()
        self.update_config_display()
        messagebox.showinfo("保存完了", "設定が保存されました")
    
    def update_config_display(self):
        """設定表示更新"""
        self.config_display.delete(1.0, tk.END)
        
        text = "📋 現在の設定:\n\n"
        for section in self.config.sections():
            text += f"[{section}]\n"
            for key, value in self.config.items(section):
                text += f"  {key} = {value}\n"
            text += "\n"
        
        self.config_display.insert(tk.END, text)
    
    def reset_settings(self):
        """設定リセット"""
        if messagebox.askyesno("確認", "設定をデフォルトにリセットしますか？"):
            for var in self.opt_vars.values():
                var.set(True)
            self.opt_level.set('balanced')
            self.auto_optimize_var.set(False)
            self.interval_var.set('5')
            messagebox.showinfo("リセット完了", "設定がリセットされました")
    
    def clear_log(self):
        """ログクリア"""
        self.log_display.delete(1.0, tk.END)
    
    def export_log(self):
        """ログエクスポート"""
        log_content = self.log_display.get(1.0, tk.END)
        filename = f"vr_optimizer_gui_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        messagebox.showinfo("エクスポート完了", f"ログを保存しました: {filename}")
    
    def run(self):
        """GUI実行"""
        self.root.mainloop()

class VRAdvancedOptimizer:
    """VR高度最適化エンジン"""
    
    def __init__(self):
        self.config = {
            'optimization_level': 'balanced',
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
        """プロセス優先度の最適化"""
        logger.info("⚡ プロセス優先度を最適化中...")
        
        try:
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
                        if proc.username() == psutil.Process().username():
                            proc.nice(vr_processes[proc_name])
                            optimized_count += 1
                            logger.info(f"✅ {proc_name} の優先度を最適化しました")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"✅ {optimized_count}個のプロセス優先度を最適化しました")
            return True
            
        except Exception as e:
            logger.error(f"❌ プロセス優先度最適化エラー: {e}")
            return False
    
    def run_optimization(self) -> Dict[str, bool]:
        """最適化の実行"""
        logger.info("🚀 VR環境最適化を開始します...")
        
        self.detect_vr_environment()
        
        optimizations = [
            ("プロセス優先度最適化", self.optimize_process_priorities),
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
        report.append("🥽 VR環境高度最適化レポート")
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
        
        return "\n".join(report)

def main():
    """メイン関数"""
    try:
        # GUI版を起動
        app = VRAdvancedOptimizerGUI()
        app.run()
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}")
        print(f"❌ アプリケーションの起動に失敗しました: {e}")

if __name__ == "__main__":
    main() 