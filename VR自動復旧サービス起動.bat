@echo off
chcp 65001 > nul
echo ===============================================
echo      VR環境自動復旧サービス起動
echo ===============================================
echo.

echo 🔧 Python依存関係をインストール中...
py -3 -m pip install -r requirements.txt

echo.
echo 🥽 VR環境自動復旧サービスを開始中...
echo.
echo このサービスは以下の機能を提供します:
echo - Virtual Desktop Streamerの自動監視
echo - プロセス停止時の自動復旧
echo - 復旧試行回数制限とクールダウン
echo.
echo サービスを停止するには Ctrl+C を押してください
echo ログファイル: vr_auto_recovery.log
echo.

py -3 vr_auto_recovery_service.py

pause 