import streamlit as st
import psutil
import GPUtil
import time
import subprocess
import threading
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta
import numpy as np
import wmi
import os
import sys

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

# ページ設定
st.set_page_config(
    page_title="VR環境システム監視ダッシュボード",
    page_icon="🥽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# グローバル変数
if 'monitoring_data' not in st.session_state:
    st.session_state.monitoring_data = {
        'timestamps': [],
        'cpu_usage': [],
        'cpu_temp': [],
        'memory_usage': [],
        'gpu_usage': [],
        'gpu_temp': [],
        'vram_usage': [],
        'vr_processes': []
    }

if 'auto_recovery_enabled' not in st.session_state:
    st.session_state.auto_recovery_enabled = False

if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False

class VRSystemMonitor:
    def __init__(self):
        self.wmi_connection = None
        try:
            self.wmi_connection = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        except:
            try:
                self.wmi_connection = wmi.WMI(namespace="root\\LibreHardwareMonitor")
            except:
                self.wmi_connection = None

    def get_cpu_temperature(self):
        """CPU温度を取得"""
        try:
            if self.wmi_connection:
                temperature_infos = self.wmi_connection.Sensor()
                for sensor in temperature_infos:
                    if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                        return round(sensor.Value, 1) if sensor.Value else None
            
            # 代替方法: psutil (Linux/一部Windows)
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            return round(entries[0].current, 1) if entries else None
            
            return None
        except Exception as e:
            return None

    def get_gpu_info(self):
        """GPU情報を取得"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # 最初のGPUを使用
                return {
                    'usage': round(gpu.load * 100, 1),
                    'temperature': round(gpu.temperature, 1),
                    'vram_used': round(gpu.memoryUsed, 1),
                    'vram_total': round(gpu.memoryTotal, 1),
                    'vram_usage_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1),
                    'name': gpu.name
                }
            return None
        except Exception as e:
            return None

    def get_system_info(self):
        """システム情報を取得"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # CPU温度
            cpu_temp = self.get_cpu_temperature()
            
            # GPU情報
            gpu_info = self.get_gpu_info()
            
            return {
                'cpu_usage': cpu_usage,
                'cpu_temp': cpu_temp,
                'memory_usage': memory_usage,
                'memory_used_gb': round(memory.used / (1024**3), 1),
                'memory_total_gb': round(memory.total / (1024**3), 1),
                'gpu_info': gpu_info,
                'timestamp': datetime.now()
            }
        except Exception as e:
            st.error(f"システム情報取得エラー: {e}")
            return None

    def check_vr_processes(self):
        """VR関連プロセスの状態確認"""
        vr_processes = {
            'VRChat': False,
            'VirtualDesktop.Streamer': False,
            'VirtualDesktop.Service': False,
            'SteamVR': False,
            'OculusClient': False
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name']
                
                if 'VRChat' in proc_name:
                    vr_processes['VRChat'] = True
                elif 'VirtualDesktop.Streamer' in proc_name:
                    vr_processes['VirtualDesktop.Streamer'] = True
                elif 'VirtualDesktop.Service' in proc_name:
                    vr_processes['VirtualDesktop.Service'] = True
                elif 'vrserver' in proc_name or 'SteamVR' in proc_name:
                    vr_processes['SteamVR'] = True
                elif 'OculusClient' in proc_name:
                    vr_processes['OculusClient'] = True
                    
        except Exception as e:
            st.error(f"プロセス確認エラー: {e}")
            
        return vr_processes

    def restart_virtual_desktop(self):
        """Virtual Desktopを再起動"""
        try:
            # Virtual Desktop Streamerのパスを探す
            vd_paths = [
                r"C:\Program Files\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe",
                r"C:\Program Files (x86)\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe",
                os.path.expanduser(r"~\AppData\Local\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe")
            ]
            
            vd_path = None
            for path in vd_paths:
                if os.path.exists(path):
                    vd_path = path
                    break
            
            if vd_path:
                # Virtual Desktopを起動
                subprocess.Popen([vd_path], shell=True)
                return True
            else:
                st.error("Virtual Desktop Streamerが見つかりません")
                return False
                
        except Exception as e:
            st.error(f"Virtual Desktop再起動エラー: {e}")
            return False

def update_monitoring_data():
    """監視データを更新"""
    monitor = VRSystemMonitor()
    system_info = monitor.get_system_info()
    vr_processes = monitor.check_vr_processes()
    
    if system_info:
        # データを追加
        st.session_state.monitoring_data['timestamps'].append(system_info['timestamp'])
        st.session_state.monitoring_data['cpu_usage'].append(system_info['cpu_usage'])
        st.session_state.monitoring_data['cpu_temp'].append(system_info['cpu_temp'])
        st.session_state.monitoring_data['memory_usage'].append(system_info['memory_usage'])
        st.session_state.monitoring_data['vr_processes'].append(vr_processes)
        
        if system_info['gpu_info']:
            st.session_state.monitoring_data['gpu_usage'].append(system_info['gpu_info']['usage'])
            st.session_state.monitoring_data['gpu_temp'].append(system_info['gpu_info']['temperature'])
            st.session_state.monitoring_data['vram_usage'].append(system_info['gpu_info']['vram_usage_percent'])
        else:
            st.session_state.monitoring_data['gpu_usage'].append(0)
            st.session_state.monitoring_data['gpu_temp'].append(0)
            st.session_state.monitoring_data['vram_usage'].append(0)
        
        # 古いデータを削除（最新100件のみ保持）
        max_data_points = 100
        for key in st.session_state.monitoring_data:
            if len(st.session_state.monitoring_data[key]) > max_data_points:
                st.session_state.monitoring_data[key] = st.session_state.monitoring_data[key][-max_data_points:]

def auto_recovery_check():
    """自動復旧チェック"""
    if not st.session_state.auto_recovery_enabled:
        return
    
    monitor = VRSystemMonitor()
    vr_processes = monitor.check_vr_processes()
    
    # Virtual Desktop Streamerが停止している場合
    if not vr_processes['VirtualDesktop.Streamer']:
        st.warning("🔄 Virtual Desktop Streamerが停止しています。自動復旧を試行中...")
        if monitor.restart_virtual_desktop():
            st.success("✅ Virtual Desktop Streamerを再起動しました")
        else:
            st.error("❌ Virtual Desktop Streamerの再起動に失敗しました")

def create_performance_chart(data_key, title, color, unit=""):
    """パフォーマンスチャートを作成"""
    if not st.session_state.monitoring_data['timestamps']:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    timestamps = st.session_state.monitoring_data['timestamps']
    values = st.session_state.monitoring_data[data_key]
    
    # Noneや無効な値を除外
    valid_data = [(t, v) for t, v in zip(timestamps, values) if v is not None and v != 0]
    
    if valid_data:
        times, vals = zip(*valid_data)
        ax.plot(times, vals, color=color, linewidth=2, marker='o', markersize=3)
        ax.fill_between(times, vals, alpha=0.3, color=color)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(f"{unit}", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    # Y軸の範囲設定
    if data_key in ['cpu_usage', 'memory_usage', 'gpu_usage', 'vram_usage']:
        ax.set_ylim(0, 100)
    elif data_key in ['cpu_temp', 'gpu_temp']:
        ax.set_ylim(0, 100)
    
    plt.tight_layout()
    return fig

# メイン画面
def main():
    st.title("🥽 VR環境システム監視ダッシュボード")
    st.markdown("---")
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 監視設定")
        
        # 監視開始/停止
        if st.button("🔄 監視開始" if not st.session_state.monitoring_active else "⏹️ 監視停止"):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
        
        # 自動復旧設定
        st.session_state.auto_recovery_enabled = st.checkbox(
            "🔧 Virtual Desktop自動復旧", 
            value=st.session_state.auto_recovery_enabled
        )
        
        # データクリア
        if st.button("🗑️ データクリア"):
            for key in st.session_state.monitoring_data:
                st.session_state.monitoring_data[key] = []
            st.success("データをクリアしました")
        
        st.markdown("---")
        st.header("📊 監視項目")
        st.markdown("""
        - **CPU使用率・温度**
        - **メモリ使用率**
        - **GPU使用率・温度**
        - **VRAM使用率**
        - **VR関連プロセス**
        """)
    
    # 監視データ更新
    if st.session_state.monitoring_active:
        update_monitoring_data()
        auto_recovery_check()
    
    # 現在のシステム状態表示
    monitor = VRSystemMonitor()
    current_info = monitor.get_system_info()
    vr_processes = monitor.check_vr_processes()
    
    if current_info:
        # メトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "CPU使用率", 
                f"{current_info['cpu_usage']:.1f}%",
                delta=None
            )
            if current_info['cpu_temp']:
                st.metric(
                    "CPU温度", 
                    f"{current_info['cpu_temp']:.1f}°C",
                    delta=None
                )
        
        with col2:
            st.metric(
                "メモリ使用率", 
                f"{current_info['memory_usage']:.1f}%",
                delta=None
            )
            st.metric(
                "メモリ使用量", 
                f"{current_info['memory_used_gb']:.1f}GB / {current_info['memory_total_gb']:.1f}GB",
                delta=None
            )
        
        with col3:
            if current_info['gpu_info']:
                gpu_info = current_info['gpu_info']
                st.metric(
                    "GPU使用率", 
                    f"{gpu_info['usage']:.1f}%",
                    delta=None
                )
                st.metric(
                    "GPU温度", 
                    f"{gpu_info['temperature']:.1f}°C",
                    delta=None
                )
        
        with col4:
            if current_info['gpu_info']:
                gpu_info = current_info['gpu_info']
                st.metric(
                    "VRAM使用率", 
                    f"{gpu_info['vram_usage_percent']:.1f}%",
                    delta=None
                )
                st.metric(
                    "VRAM使用量", 
                    f"{gpu_info['vram_used']:.1f}GB / {gpu_info['vram_total']:.1f}GB",
                    delta=None
                )
    
    st.markdown("---")
    
    # VR関連プロセス状態
    st.header("🎮 VR関連プロセス状態")
    
    process_cols = st.columns(5)
    process_names = ['VRChat', 'VirtualDesktop.Streamer', 'VirtualDesktop.Service', 'SteamVR', 'OculusClient']
    
    for i, (col, process_name) in enumerate(zip(process_cols, process_names)):
        with col:
            status = vr_processes.get(process_name, False)
            status_text = "🟢 実行中" if status else "🔴 停止中"
            st.metric(process_name, status_text)
    
    # Virtual Desktop手動再起動ボタン
    if st.button("🔄 Virtual Desktop手動再起動"):
        if monitor.restart_virtual_desktop():
            st.success("✅ Virtual Desktop Streamerを再起動しました")
        else:
            st.error("❌ Virtual Desktop Streamerの再起動に失敗しました")
    
    st.markdown("---")
    
    # パフォーマンスチャート
    if st.session_state.monitoring_data['timestamps']:
        st.header("📈 パフォーマンス履歴")
        
        # CPU関連
        col1, col2 = st.columns(2)
        with col1:
            cpu_chart = create_performance_chart('cpu_usage', 'CPU使用率', '#FF6B6B', '%')
            if cpu_chart:
                st.pyplot(cpu_chart)
        
        with col2:
            cpu_temp_chart = create_performance_chart('cpu_temp', 'CPU温度', '#4ECDC4', '°C')
            if cpu_temp_chart:
                st.pyplot(cpu_temp_chart)
        
        # メモリ
        memory_chart = create_performance_chart('memory_usage', 'メモリ使用率', '#45B7D1', '%')
        if memory_chart:
            st.pyplot(memory_chart)
        
        # GPU関連
        col3, col4 = st.columns(2)
        with col3:
            gpu_chart = create_performance_chart('gpu_usage', 'GPU使用率', '#96CEB4', '%')
            if gpu_chart:
                st.pyplot(gpu_chart)
        
        with col4:
            gpu_temp_chart = create_performance_chart('gpu_temp', 'GPU温度', '#FFEAA7', '°C')
            if gpu_temp_chart:
                st.pyplot(gpu_temp_chart)
        
        # VRAM
        vram_chart = create_performance_chart('vram_usage', 'VRAM使用率', '#DDA0DD', '%')
        if vram_chart:
            st.pyplot(vram_chart)
    
    # 自動更新
    if st.session_state.monitoring_active:
        time.sleep(2)
        st.rerun()

if __name__ == "__main__":
    main() 