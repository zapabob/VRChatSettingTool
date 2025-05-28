import os
import sys
import subprocess
import time
import logging
import winreg
import psutil
import threading
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vr_integrated_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VRIntegratedManager:
    def __init__(self):
        self.startup_delay = 30  # 起動後30秒待機
        self.retry_attempts = 3
        self.retry_delay = 10
        self.check_interval = 30  # 30秒間隔でチェック
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5分間のクールダウン
        self.monitoring_active = False
        
        # アプリケーションパス候補
        self.app_paths = {
            'VirtualDesktop': [
                r"C:\Program Files\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe",
                r"C:\Program Files (x86)\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe",
                os.path.expanduser(r"~\AppData\Local\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe")
            ],
            'SteamVR': [
                r"C:\Program Files (x86)\Steam\steamapps\common\SteamVR\bin\win64\vrstartup.exe",
                r"C:\Program Files\Steam\steamapps\common\SteamVR\bin\win64\vrstartup.exe",
                r"D:\Steam\steamapps\common\SteamVR\bin\win64\vrstartup.exe",
                r"E:\Steam\steamapps\common\SteamVR\bin\win64\vrstartup.exe"
            ],
            'Steam': [
                r"C:\Program Files (x86)\Steam\Steam.exe",
                r"C:\Program Files\Steam\Steam.exe",
                r"D:\Steam\Steam.exe",
                r"E:\Steam\Steam.exe"
            ],
            'VRChat': [
                r"C:\Program Files (x86)\Steam\steamapps\common\VRChat\VRChat.exe",
                r"C:\Program Files\Steam\steamapps\common\VRChat\VRChat.exe",
                r"D:\Steam\steamapps\common\VRChat\VRChat.exe",
                r"E:\Steam\steamapps\common\VRChat\VRChat.exe",
                r"C:\Program Files\Oculus\Software\vrchat-vrchat\VRChat.exe",
                r"C:\Program Files (x86)\Oculus\Software\vrchat-vrchat\VRChat.exe"
            ]
        }
        
        self.found_paths = self.find_application_paths()
    
    def find_application_paths(self):
        """アプリケーションのパスを検索"""
        found = {}
        
        for app_name, paths in self.app_paths.items():
            for path in paths:
                if os.path.exists(path):
                    found[app_name] = path
                    logging.info(f"{app_name} found: {path}")
                    break
            
            if app_name not in found:
                logging.warning(f"{app_name} not found")
        
        return found
    
    def is_process_running(self, process_name):
        """プロセスが実行中かチェック"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logging.error(f"プロセスチェックエラー: {e}")
            return False
    
    def start_application(self, app_name, path, wait_for_process=None):
        """アプリケーションを起動"""
        try:
            logging.info(f"{app_name}を起動中: {path}")
            
            if app_name == 'Steam':
                subprocess.Popen([path, '-silent'], shell=True)
            elif app_name == 'VRChat':
                if self.is_process_running('vrserver'):
                    logging.info("SteamVRが起動中です。VRChatをVRモードで起動します")
                    subprocess.Popen([path], shell=True)
                else:
                    logging.warning("SteamVRが起動していません。VRChatの起動をスキップします")
                    return False
            else:
                subprocess.Popen([path], shell=True)
            
            if wait_for_process:
                for i in range(30):
                    if self.is_process_running(wait_for_process):
                        logging.info(f"{app_name}の起動を確認しました")
                        return True
                    time.sleep(1)
                
                logging.warning(f"{app_name}のプロセス起動を確認できませんでした")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"{app_name}起動エラー: {e}")
            return False
    
    def startup_sequence(self):
        """VRアプリケーション起動シーケンス"""
        logging.info("VR環境起動シーケンスを開始します")
        
        logging.info(f"システム安定化のため{self.startup_delay}秒待機中...")
        for i in tqdm(range(self.startup_delay), desc="起動待機", leave=False):
            time.sleep(1)
        
        success_count = 0
        total_apps = len(self.found_paths)
        
        # 1. Steam起動
        if 'Steam' in self.found_paths:
            if not self.is_process_running('Steam'):
                for attempt in range(self.retry_attempts):
                    if self.start_application('Steam', self.found_paths['Steam'], 'Steam'):
                        success_count += 1
                        time.sleep(5)
                        break
                    else:
                        logging.warning(f"Steam起動試行 {attempt + 1}/{self.retry_attempts} 失敗")
                        time.sleep(self.retry_delay)
            else:
                logging.info("Steamは既に実行中です")
                success_count += 1
        
        # 2. Virtual Desktop起動
        if 'VirtualDesktop' in self.found_paths:
            if not self.is_process_running('VirtualDesktop.Streamer'):
                for attempt in range(self.retry_attempts):
                    if self.start_application('Virtual Desktop', self.found_paths['VirtualDesktop'], 'VirtualDesktop.Streamer'):
                        success_count += 1
                        time.sleep(3)
                        break
                    else:
                        logging.warning(f"Virtual Desktop起動試行 {attempt + 1}/{self.retry_attempts} 失敗")
                        time.sleep(self.retry_delay)
            else:
                logging.info("Virtual Desktop Streamerは既に実行中です")
                success_count += 1
        
        # 3. SteamVR起動
        if 'SteamVR' in self.found_paths:
            if not self.is_process_running('vrserver'):
                if self.is_process_running('Steam'):
                    time.sleep(5)
                    
                    for attempt in range(self.retry_attempts):
                        if self.start_application('SteamVR', self.found_paths['SteamVR'], 'vrserver'):
                            success_count += 1
                            logging.info("SteamVRの完全起動を待機中...")
                            time.sleep(10)
                            break
                        else:
                            logging.warning(f"SteamVR起動試行 {attempt + 1}/{self.retry_attempts} 失敗")
                            time.sleep(self.retry_delay)
                else:
                    logging.error("SteamVR起動にはSteamが必要ですが、Steamが実行されていません")
            else:
                logging.info("SteamVRは既に実行中です")
                success_count += 1
        
        # 4. VRChat起動
        if 'VRChat' in self.found_paths:
            if not self.is_process_running('VRChat'):
                if self.is_process_running('vrserver'):
                    logging.info("SteamVRの起動を確認しました。VRChatをVRモードで起動します")
                    for attempt in range(self.retry_attempts):
                        if self.start_application('VRChat', self.found_paths['VRChat'], 'VRChat'):
                            success_count += 1
                            logging.info("✅ VRChatがVRモードで起動しました")
                            break
                        else:
                            logging.warning(f"VRChat起動試行 {attempt + 1}/{self.retry_attempts} 失敗")
                            time.sleep(self.retry_delay)
                else:
                    logging.warning("SteamVRが起動していないため、VRChatの起動をスキップします")
            else:
                logging.info("VRChatは既に実行中です")
                success_count += 1
        
        logging.info(f"VR環境起動シーケンス完了: {success_count}/{total_apps} 成功")
        
        if success_count == total_apps:
            logging.info("✅ すべてのVRアプリケーションが正常に起動しました")
        else:
            logging.warning(f"⚠️ 一部のアプリケーション起動に失敗しました ({total_apps - success_count}個)")
        
        return success_count == total_apps
    
    def install_startup_service(self):
        """Windows起動時の自動実行を設定"""
        try:
            script_path = os.path.abspath(__file__)
            python_path = sys.executable
            
            batch_content = f'''@echo off
cd /d "{os.path.dirname(script_path)}"
"{python_path}" "{script_path}" --startup
'''
            
            batch_path = os.path.join(os.path.dirname(script_path), "VR_Integrated_Service.bat")
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VR_Integrated_Manager", 0, winreg.REG_SZ, batch_path)
            winreg.CloseKey(key)
            
            logging.info("✅ Windows起動時の自動実行を設定しました")
            return True
            
        except Exception as e:
            logging.error(f"自動実行設定エラー: {e}")
            return False
    
    def uninstall_startup_service(self):
        """Windows起動時の自動実行を解除"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            try:
                winreg.DeleteValue(key, "VR_Integrated_Manager")
                logging.info("✅ Windows起動時の自動実行を解除しました")
            except FileNotFoundError:
                logging.info("自動実行設定は既に解除されています")
            
            winreg.CloseKey(key)
            
            batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VR_Integrated_Service.bat")
            if os.path.exists(batch_path):
                os.remove(batch_path)
            
            return True
            
        except Exception as e:
            logging.error(f"自動実行解除エラー: {e}")
            return False
    
    def check_startup_status(self):
        """自動実行設定の状態を確認"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            
            try:
                value, _ = winreg.QueryValueEx(key, "VR_Integrated_Manager")
                winreg.CloseKey(key)
                return True, value
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False, None
                
        except Exception as e:
            logging.error(f"自動実行状態確認エラー: {e}")
            return False, None
    
    def get_vr_processes_status(self):
        """VR関連プロセスの状態を取得"""
        processes = {
            'VRChat': self.is_process_running('VRChat'),
            'VirtualDesktop.Streamer': self.is_process_running('VirtualDesktop.Streamer'),
            'SteamVR': self.is_process_running('vrserver'),
            'Steam': self.is_process_running('Steam'),
            'OculusClient': self.is_process_running('OculusClient')
        }
        return processes
    
    def restart_application(self, app_name):
        """アプリケーションを再起動"""
        if app_name not in self.found_paths:
            logging.error(f"{app_name}のパスが見つかりません")
            return False
        
        try:
            path = self.found_paths[app_name]
            logging.info(f"{app_name}を再起動中: {path}")
            
            if app_name == 'VirtualDesktop':
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'VirtualDesktop.Streamer' in proc.info['name']:
                        proc.terminate()
                        proc.wait(timeout=10)
                time.sleep(2)
            
            if app_name == 'Steam':
                subprocess.Popen([path, '-silent'], shell=True)
            elif app_name == 'VRChat':
                if self.is_process_running('vrserver'):
                    logging.info("SteamVRが起動中です。VRChatをVRモードで復旧します")
                    subprocess.Popen([path], shell=True)
                else:
                    logging.warning("SteamVRが起動していないため、VRChatの復旧をスキップします")
                    return False
            else:
                subprocess.Popen([path], shell=True)
            
            logging.info(f"{app_name}を再起動しました")
            return True
            
        except Exception as e:
            logging.error(f"{app_name}再起動エラー: {e}")
            return False
    
    def should_attempt_recovery(self, process_name):
        """復旧を試行すべきかチェック"""
        current_time = time.time()
        
        if process_name not in self.recovery_attempts:
            self.recovery_attempts[process_name] = {
                'count': 0,
                'last_attempt': 0
            }
        
        attempt_info = self.recovery_attempts[process_name]
        
        if current_time - attempt_info['last_attempt'] < self.recovery_cooldown:
            return False
        
        if attempt_info['count'] >= self.max_recovery_attempts:
            if current_time - attempt_info['last_attempt'] > 3600:
                attempt_info['count'] = 0
            else:
                return False
        
        return True
    
    def record_recovery_attempt(self, process_name):
        """復旧試行を記録"""
        current_time = time.time()
        
        if process_name not in self.recovery_attempts:
            self.recovery_attempts[process_name] = {
                'count': 0,
                'last_attempt': 0
            }
        
        self.recovery_attempts[process_name]['count'] += 1
        self.recovery_attempts[process_name]['last_attempt'] = current_time
    
    def check_and_recover_vr_environment(self):
        """VR環境全体の監視と復旧"""
        processes = self.get_vr_processes_status()
        recovery_performed = False
        
        # Virtual Desktop監視
        if not processes['VirtualDesktop.Streamer'] and 'VirtualDesktop' in self.found_paths:
            if self.should_attempt_recovery('VirtualDesktop.Streamer'):
                logging.warning("Virtual Desktop Streamerが停止しています。復旧を試行中...")
                
                if self.restart_application('VirtualDesktop'):
                    logging.info("✅ Virtual Desktop Streamerの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ Virtual Desktop Streamerの復旧に失敗しました")
                
                self.record_recovery_attempt('VirtualDesktop.Streamer')
        
        # SteamVR監視
        if not processes['SteamVR'] and 'SteamVR' in self.found_paths:
            if self.should_attempt_recovery('SteamVR'):
                logging.warning("SteamVRが停止しています。復旧を試行中...")
                
                if not self.is_process_running('Steam'):
                    if self.restart_application('Steam'):
                        time.sleep(10)
                
                if self.restart_application('SteamVR'):
                    logging.info("✅ SteamVRの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ SteamVRの復旧に失敗しました")
                
                self.record_recovery_attempt('SteamVR')
        
        # Steam監視
        if not processes['Steam'] and 'Steam' in self.found_paths and 'SteamVR' in self.found_paths:
            if self.should_attempt_recovery('Steam'):
                logging.warning("Steamが停止しています。復旧を試行中...")
                
                if self.restart_application('Steam'):
                    logging.info("✅ Steamの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ Steamの復旧に失敗しました")
                
                self.record_recovery_attempt('Steam')
        
        # VRChat監視（SteamVRが起動している場合のみ）
        if 'VRChat' in self.found_paths and processes['SteamVR']:
            if not processes['VRChat']:
                if self.should_attempt_recovery('VRChat'):
                    logging.warning("VRChatが停止しています。復旧を試行中...")
                    
                    if self.restart_application('VRChat'):
                        logging.info("✅ VRChatの復旧に成功しました")
                        recovery_performed = True
                    else:
                        logging.error("❌ VRChatの復旧に失敗しました")
                    
                    self.record_recovery_attempt('VRChat')
        
        return recovery_performed
    
    def monitor_and_recover(self):
        """監視と自動復旧のメインループ"""
        logging.info("VR自動復旧サービスを開始しました")
        logging.info(f"監視対象アプリケーション: {list(self.found_paths.keys())}")
        
        self.monitoring_active = True
        
        try:
            while self.monitoring_active:
                processes = self.get_vr_processes_status()
                
                recovery_performed = self.check_and_recover_vr_environment()
                
                running_processes = [name for name, status in processes.items() if status]
                if running_processes:
                    logging.info(f"実行中のVRプロセス: {', '.join(running_processes)}")
                else:
                    logging.warning("実行中のVRプロセスがありません")
                
                if recovery_performed:
                    logging.info("復旧処理が実行されました。10秒後に再チェックします...")
                    time.sleep(10)
                    continue
                
                for i in tqdm(range(self.check_interval), desc="次回チェックまで", leave=False):
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("VR自動復旧サービスを停止しました")
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")
        finally:
            self.monitoring_active = False
    
    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring_active = False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='VR環境統合管理ツール')
    parser.add_argument('--startup', action='store_true', help='起動シーケンス実行（Windows起動時用）')
    parser.add_argument('--install', action='store_true', help='自動実行を設定')
    parser.add_argument('--uninstall', action='store_true', help='自動実行を解除')
    parser.add_argument('--status', action='store_true', help='自動実行設定状態を確認')
    parser.add_argument('--test', action='store_true', help='起動シーケンステスト')
    parser.add_argument('--monitor', action='store_true', help='自動復旧監視開始')
    
    args = parser.parse_args()
    
    manager = VRIntegratedManager()
    
    if args.startup:
        print("🥽 VR環境自動起動サービス")
        print("=" * 50)
        manager.startup_sequence()
        
    elif args.install:
        print("🔧 VR環境自動起動設定")
        print("=" * 50)
        if manager.install_startup_service():
            print("✅ Windows起動時の自動実行を設定しました")
        else:
            print("❌ 自動実行設定に失敗しました")
    
    elif args.uninstall:
        print("🗑️ VR環境自動起動解除")
        print("=" * 50)
        if manager.uninstall_startup_service():
            print("✅ Windows起動時の自動実行を解除しました")
        else:
            print("❌ 自動実行解除に失敗しました")
    
    elif args.status:
        print("📊 VR環境自動起動状態確認")
        print("=" * 50)
        is_enabled, path = manager.check_startup_status()
        if is_enabled:
            print(f"✅ 自動実行が設定されています: {path}")
        else:
            print("❌ 自動実行は設定されていません")
    
    elif args.test:
        print("🧪 VR環境起動シーケンステスト")
        print("=" * 50)
        manager.startup_sequence()
    
    elif args.monitor:
        print("🥽 VR環境自動復旧監視サービス")
        print("=" * 50)
        print("以下のアプリケーションを監視・自動復旧します:")
        print("- Virtual Desktop Streamer")
        print("- SteamVR")
        print("- Steam（SteamVR用）")
        print("- VRChat（SteamVR起動時のみ）")
        print("停止するには Ctrl+C を押してください")
        print("=" * 50)
        
        if not manager.found_paths:
            print("❌ 監視対象のVRアプリケーションが見つかりません")
            return
        
        manager.monitor_and_recover()
    
    else:
        print("🥽 VR環境統合管理ツール")
        print("=" * 50)
        print("1. VR環境を今すぐ起動")
        print("2. Windows起動時の自動実行を設定")
        print("3. Windows起動時の自動実行を解除")
        print("4. 自動実行設定状態を確認")
        print("5. 自動復旧監視を開始")
        print("6. 検出されたアプリケーション一覧")
        print("0. 終了")
        print("=" * 50)
        
        while True:
            try:
                choice = input("選択してください (0-6): ").strip()
                
                if choice == '1':
                    print("\n🚀 VR環境起動中...")
                    manager.startup_sequence()
                    break
                    
                elif choice == '2':
                    print("\n🔧 自動実行設定中...")
                    if manager.install_startup_service():
                        print("✅ 設定完了")
                    else:
                        print("❌ 設定失敗")
                    break
                    
                elif choice == '3':
                    print("\n🗑️ 自動実行解除中...")
                    if manager.uninstall_startup_service():
                        print("✅ 解除完了")
                    else:
                        print("❌ 解除失敗")
                    break
                    
                elif choice == '4':
                    print("\n📊 設定状態確認中...")
                    is_enabled, path = manager.check_startup_status()
                    if is_enabled:
                        print(f"✅ 自動実行設定済み: {path}")
                    else:
                        print("❌ 自動実行未設定")
                    break
                    
                elif choice == '5':
                    print("\n🔍 自動復旧監視開始...")
                    print("停止するには Ctrl+C を押してください")
                    manager.monitor_and_recover()
                    break
                    
                elif choice == '6':
                    print("\n📋 検出されたアプリケーション:")
                    for app_name, path in manager.found_paths.items():
                        print(f"  {app_name}: {path}")
                    if not manager.found_paths:
                        print("  検出されたアプリケーションはありません")
                    break
                    
                elif choice == '0':
                    print("終了します")
                    break
                    
                else:
                    print("無効な選択です。0-6の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n終了します")
                break

if __name__ == "__main__":
    main() 