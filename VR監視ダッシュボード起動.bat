@echo off
chcp 65001 > nul
echo ===============================================
echo    VR環境システム監視ダッシュボード起動
echo ===============================================
echo.

echo 🔧 Python依存関係をインストール中...
py -3 -m pip install -r requirements.txt

echo.
echo 🥽 VR環境システム監視ダッシュボードを起動中...
echo.
echo ブラウザで以下のURLにアクセスしてください:
echo http://localhost:8501
echo.
echo ダッシュボードを停止するには Ctrl+C を押してください
echo.

py -3 -m streamlit run vr_system_monitor.py --server.port 8501

pause 