import os
import sys
import subprocess
import time
import logging
import winreg
import psutil
from pathlib import Path
from tqdm import tqdm

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vr_startup_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VRStartupManager:
    def __init__(self):
        self.startup_delay = 30  # 起動後30秒待機
        self.retry_attempts = 3
        self.retry_delay = 10
        
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
                # Oculus版VRChat
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
            
            # アプリケーションを起動
            if app_name == 'Steam':
                # Steamは最小化で起動
                subprocess.Popen([path, '-silent'], shell=True)
            elif app_name == 'VRChat':
                # VRChatをVRモードで起動（SteamVRが起動していることを確認）
                if self.is_process_running('vrserver'):
                    logging.info("SteamVRが起動中です。VRChatをVRモードで起動します")
                    # VRChatはSteamVRが起動していれば自動的にVRモードで起動
                    subprocess.Popen([path], shell=True)
                else:
                    logging.warning("SteamVRが起動していません。VRChatの起動をスキップします")
                    return False
            else:
                subprocess.Popen([path], shell=True)
            
            # プロセス起動を待機
            if wait_for_process:
                for i in range(30):  # 30秒まで待機
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
        
        # 起動遅延
        logging.info(f"システム安定化のため{self.startup_delay}秒待機中...")
        for i in tqdm(range(self.startup_delay), desc="起動待機", leave=False):
            time.sleep(1)
        
        success_count = 0
        total_apps = len(self.found_paths)
        
        # 1. Steamを最初に起動（SteamVRの前提条件）
        if 'Steam' in self.found_paths:
            if not self.is_process_running('Steam'):
                for attempt in range(self.retry_attempts):
                    if self.start_application('Steam', self.found_paths['Steam'], 'Steam'):
                        success_count += 1
                        time.sleep(5)  # Steam起動後少し待機
                        break
                    else:
                        logging.warning(f"Steam起動試行 {attempt + 1}/{self.retry_attempts} 失敗")
                        time.sleep(self.retry_delay)
            else:
                logging.info("Steamは既に実行中です")
                success_count += 1
        
        # 2. Virtual Desktop Streamerを起動
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
        
        # 3. SteamVRを起動
        if 'SteamVR' in self.found_paths:
            if not self.is_process_running('vrserver'):
                # Steamが起動していることを確認
                if self.is_process_running('Steam'):
                    time.sleep(5)  # Steam完全起動を待機
                    
                    for attempt in range(self.retry_attempts):
                        if self.start_application('SteamVR', self.found_paths['SteamVR'], 'vrserver'):
                            success_count += 1
                            # SteamVR起動後、VR環境が安定するまで待機
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
        
        # 4. VRChatを起動（SteamVRが起動している場合のみ）
        if 'VRChat' in self.found_paths:
            if not self.is_process_running('VRChat'):
                # SteamVRが起動していることを再確認
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
        
        # 結果報告
        logging.info(f"VR環境起動シーケンス完了: {success_count}/{total_apps} 成功")
        
        if success_count == total_apps:
            logging.info("✅ すべてのVRアプリケーションが正常に起動しました")
        else:
            logging.warning(f"⚠️ 一部のアプリケーション起動に失敗しました ({total_apps - success_count}個)")
        
        return success_count == total_apps
    
    def install_startup_service(self):
        """Windows起動時の自動実行を設定"""
        try:
            # 現在のスクリプトパス
            script_path = os.path.abspath(__file__)
            python_path = sys.executable
            
            # バッチファイルを作成
            batch_content = f'''@echo off
cd /d "{os.path.dirname(script_path)}"
"{python_path}" "{script_path}" --startup
'''
            
            batch_path = os.path.join(os.path.dirname(script_path), "VR_Startup_Service.bat")
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            # レジストリに登録
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VR_Startup_Manager", 0, winreg.REG_SZ, batch_path)
            winreg.CloseKey(key)
            
            logging.info("✅ Windows起動時の自動実行を設定しました")
            logging.info(f"バッチファイル: {batch_path}")
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
                winreg.DeleteValue(key, "VR_Startup_Manager")
                logging.info("✅ Windows起動時の自動実行を解除しました")
            except FileNotFoundError:
                logging.info("自動実行設定は既に解除されています")
            
            winreg.CloseKey(key)
            
            # バッチファイルも削除
            batch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VR_Startup_Service.bat")
            if os.path.exists(batch_path):
                os.remove(batch_path)
                logging.info(f"バッチファイルを削除しました: {batch_path}")
            
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
                value, _ = winreg.QueryValueEx(key, "VR_Startup_Manager")
                winreg.CloseKey(key)
                return True, value
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False, None
                
        except Exception as e:
            logging.error(f"自動実行状態確認エラー: {e}")
            return False, None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='VR環境スタートアップマネージャー')
    parser.add_argument('--startup', action='store_true', help='起動シーケンス実行（Windows起動時用）')
    parser.add_argument('--install', action='store_true', help='自動実行を設定')
    parser.add_argument('--uninstall', action='store_true', help='自動実行を解除')
    parser.add_argument('--status', action='store_true', help='自動実行設定状態を確認')
    parser.add_argument('--test', action='store_true', help='起動シーケンステスト')
    
    args = parser.parse_args()
    
    manager = VRStartupManager()
    
    if args.startup:
        # Windows起動時の自動実行
        print("🥽 VR環境自動起動サービス")
        print("=" * 50)
        manager.startup_sequence()
        
    elif args.install:
        # 自動実行設定
        print("🔧 VR環境自動起動設定")
        print("=" * 50)
        if manager.install_startup_service():
            print("✅ Windows起動時の自動実行を設定しました")
        else:
            print("❌ 自動実行設定に失敗しました")
    
    elif args.uninstall:
        # 自動実行解除
        print("🗑️ VR環境自動起動解除")
        print("=" * 50)
        if manager.uninstall_startup_service():
            print("✅ Windows起動時の自動実行を解除しました")
        else:
            print("❌ 自動実行解除に失敗しました")
    
    elif args.status:
        # 状態確認
        print("📊 VR環境自動起動状態確認")
        print("=" * 50)
        is_enabled, path = manager.check_startup_status()
        if is_enabled:
            print(f"✅ 自動実行が設定されています: {path}")
        else:
            print("❌ 自動実行は設定されていません")
    
    elif args.test:
        # テスト実行
        print("🧪 VR環境起動シーケンステスト")
        print("=" * 50)
        manager.startup_sequence()
    
    else:
        # インタラクティブメニュー
        print("🥽 VR環境スタートアップマネージャー")
        print("=" * 50)
        print("1. VR環境を今すぐ起動")
        print("2. Windows起動時の自動実行を設定")
        print("3. Windows起動時の自動実行を解除")
        print("4. 自動実行設定状態を確認")
        print("5. 検出されたアプリケーション一覧")
        print("0. 終了")
        print("=" * 50)
        
        while True:
            try:
                choice = input("選択してください (0-5): ").strip()
                
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
                    print("無効な選択です。0-5の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n終了します")
                break

if __name__ == "__main__":
    main() 