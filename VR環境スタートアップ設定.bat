@echo off
chcp 65001 > nul
echo ===============================================
echo      VR環境スタートアップマネージャー
echo ===============================================
echo.

echo 🔧 Python依存関係をインストール中...
py -3 -m pip install -r requirements.txt

echo.
echo 🥽 VR環境スタートアップマネージャーを起動中...
echo.
echo このツールは以下の機能を提供します:
echo - Windows起動時のVR環境自動起動設定
echo - Steam、SteamVR、Virtual Desktopの自動起動
echo - 電源断からの自動復旧
echo - 起動シーケンスのテスト実行
echo.

py -3 vr_startup_manager.py

pause 