import psutil
import subprocess
import time
import os
import sys
import logging
from datetime import datetime
from tqdm import tqdm

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vr_auto_recovery.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VRAutoRecoveryService:
    def __init__(self):
        self.check_interval = 30  # 30秒間隔でチェック
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5分間のクールダウン
        
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

    def check_process_running(self, process_name):
        """指定されたプロセスが実行中かチェック"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            logging.error(f"プロセスチェックエラー: {e}")
            return False

    def get_vr_processes_status(self):
        """VR関連プロセスの状態を取得"""
        processes = {
            'VRChat': self.check_process_running('VRChat'),
            'VirtualDesktop.Streamer': self.check_process_running('VirtualDesktop.Streamer'),
            'VirtualDesktop.Service': self.check_process_running('VirtualDesktop.Service'),
            'SteamVR': self.check_process_running('vrserver') or self.check_process_running('SteamVR'),
            'Steam': self.check_process_running('Steam'),
            'OculusClient': self.check_process_running('OculusClient')
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
            
            # 既存のプロセスを終了（Virtual Desktopの場合のみ）
            if app_name == 'VirtualDesktop':
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'VirtualDesktop.Streamer' in proc.info['name']:
                        proc.terminate()
                        proc.wait(timeout=10)
                time.sleep(2)
            
            # アプリケーションを起動
            if app_name == 'Steam':
                subprocess.Popen([path, '-silent'], shell=True)
            elif app_name == 'VRChat':
                # VRChatはSteamVRが起動している場合のみ復旧
                if self.check_process_running('vrserver'):
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

    def restart_virtual_desktop(self):
        """Virtual Desktopを再起動（後方互換性のため）"""
        return self.restart_application('VirtualDesktop')

    def restart_steamvr(self):
        """SteamVRを再起動"""
        # SteamVRを起動する前にSteamが実行中か確認
        if not self.check_process_running('Steam'):
            logging.warning("SteamVR起動にはSteamが必要です。Steamを先に起動します...")
            if not self.restart_application('Steam'):
                logging.error("Steam起動に失敗しました")
                return False
            
            # Steam起動を待機
            time.sleep(10)
            
            if not self.check_process_running('Steam'):
                logging.error("Steam起動を確認できませんでした")
                return False
        
        return self.restart_application('SteamVR')

    def should_attempt_recovery(self, process_name):
        """復旧を試行すべきかチェック"""
        current_time = time.time()
        
        if process_name not in self.recovery_attempts:
            self.recovery_attempts[process_name] = {
                'count': 0,
                'last_attempt': 0
            }
        
        attempt_info = self.recovery_attempts[process_name]
        
        # クールダウン期間中かチェック
        if current_time - attempt_info['last_attempt'] < self.recovery_cooldown:
            return False
        
        # 最大試行回数に達していないかチェック
        if attempt_info['count'] >= self.max_recovery_attempts:
            # 1時間経過したらカウントをリセット
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
        
        # Virtual Desktop Streamerの監視と復旧
        if not processes['VirtualDesktop.Streamer'] and 'VirtualDesktop' in self.found_paths:
            if self.should_attempt_recovery('VirtualDesktop.Streamer'):
                logging.warning("Virtual Desktop Streamerが停止しています。復旧を試行中...")
                
                if self.restart_virtual_desktop():
                    logging.info("✅ Virtual Desktop Streamerの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ Virtual Desktop Streamerの復旧に失敗しました")
                
                self.record_recovery_attempt('VirtualDesktop.Streamer')
            else:
                logging.info("Virtual Desktop Streamer停止中（復旧クールダウン期間）")
        
        # SteamVRの監視と復旧
        if not processes['SteamVR'] and 'SteamVR' in self.found_paths:
            if self.should_attempt_recovery('SteamVR'):
                logging.warning("SteamVRが停止しています。復旧を試行中...")
                
                if self.restart_steamvr():
                    logging.info("✅ SteamVRの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ SteamVRの復旧に失敗しました")
                
                self.record_recovery_attempt('SteamVR')
            else:
                logging.info("SteamVR停止中（復旧クールダウン期間）")
        
        # Steamの監視と復旧（SteamVRが必要な場合）
        if not processes['Steam'] and 'Steam' in self.found_paths and 'SteamVR' in self.found_paths:
            if self.should_attempt_recovery('Steam'):
                logging.warning("Steamが停止しています。復旧を試行中...")
                
                if self.restart_application('Steam'):
                    logging.info("✅ Steamの復旧に成功しました")
                    recovery_performed = True
                else:
                    logging.error("❌ Steamの復旧に失敗しました")
                
                self.record_recovery_attempt('Steam')
            else:
                logging.info("Steam停止中（復旧クールダウン期間）")
        
        # VRChatの監視と復旧（SteamVRが起動している場合のみ）
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
                else:
                    logging.info("VRChat停止中（復旧クールダウン期間）")
        
        return recovery_performed

    def monitor_and_recover(self):
        """監視と自動復旧のメインループ"""
        logging.info("VR自動復旧サービスを開始しました")
        logging.info(f"監視対象アプリケーション: {list(self.found_paths.keys())}")
        
        try:
            while True:
                processes = self.get_vr_processes_status()
                
                # VR環境の監視と復旧
                recovery_performed = self.check_and_recover_vr_environment()
                
                # プロセス状態をログに記録
                running_processes = [name for name, status in processes.items() if status]
                if running_processes:
                    logging.info(f"実行中のVRプロセス: {', '.join(running_processes)}")
                else:
                    logging.warning("実行中のVRプロセスがありません")
                
                # 復旧が実行された場合は短い間隔で再チェック
                if recovery_performed:
                    logging.info("復旧処理が実行されました。10秒後に再チェックします...")
                    time.sleep(10)
                    continue
                
                # 進行状況表示
                for i in tqdm(range(self.check_interval), desc="次回チェックまで", leave=False):
                    time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("VR自動復旧サービスを停止しました")
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")

def main():
    print("🥽 VR環境自動復旧サービス（強化版）")
    print("=" * 50)
    print("以下のアプリケーションを監視・自動復旧します:")
    print("- Virtual Desktop Streamer")
    print("- SteamVR")
    print("- Steam（SteamVR用）")
    print("- VRChat（SteamVR起動時のみ）")
    print("停止するには Ctrl+C を押してください")
    print("=" * 50)
    
    service = VRAutoRecoveryService()
    
    if not service.found_paths:
        print("❌ 監視対象のVRアプリケーションが見つかりません")
        print("Steam、SteamVR、Virtual Desktopがインストールされているか確認してください")
        input("Enterキーを押して終了...")
        return
    
    print(f"検出されたアプリケーション: {list(service.found_paths.keys())}")
    print()
    
    service.monitor_and_recover()

if __name__ == "__main__":
    main() 