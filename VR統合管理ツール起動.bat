@echo off
chcp 65001 > nul
echo ===============================================
echo        VR環境統合管理ツール
echo ===============================================
echo.

echo 🔧 Python依存関係をインストール中...
py -3 -m pip install -r requirements.txt

echo.
echo 🥽 VR環境統合管理ツールを起動中...
echo.
echo このツールは以下の機能を統合提供します:
echo - VR環境の自動起動（Steam、SteamVR、Virtual Desktop、VRChat）
echo - Windows起動時の自動実行設定
echo - VRアプリケーションの自動復旧監視
echo - 電源断からの完全自動復旧
echo - 統合された管理インターフェース
echo.

py -3 vr_integrated_manager.py

pause 