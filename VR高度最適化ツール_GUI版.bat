@echo off
chcp 65001 > nul
title VR環境高度最適化ツール（GUI版・管理者権限不要）

echo.
echo ============================================================
echo 🥽 VR環境高度最適化ツール（GUI版・管理者権限不要）
echo ============================================================
echo VirtualDesktop、SteamVR、VRChat用PC最適化
echo 高度な最適化機能とリアルタイム監視を提供します。
echo ============================================================
echo.

echo 📋 GUI版の特徴:
echo   • 直感的なタブ型インターフェース
echo   • リアルタイムシステム監視
echo   • 自動最適化機能
echo   • 詳細な設定管理
echo   • ログ表示・エクスポート機能
echo.

echo 🔧 依存関係の確認とインストール...
py -3 -m pip install psutil tqdm configparser --quiet --user

if %errorlevel% neq 0 (
    echo ❌ 依存関係のインストールに失敗しました。
    echo 手動でインストールしてください: py -3 -m pip install psutil tqdm configparser
    pause
    exit /b 1
)

echo ✅ 依存関係の確認が完了しました。
echo.

echo 🚀 VR環境高度最適化ツール（GUI版）を起動中...
echo 📱 GUIウィンドウが表示されるまでお待ちください...
py -3 vr_advanced_optimizer_no_admin.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ GUI版ツールの実行中にエラーが発生しました。
    echo.
    echo 💡 トラブルシューティング:
    echo   1. Pythonが正しくインストールされているか確認
    echo   2. tkinterライブラリが利用可能か確認
    echo   3. 必要な権限があるか確認
    echo   4. ウイルス対策ソフトがブロックしていないか確認
    echo.
    echo 🔄 代替案: コマンドライン版を使用してください
    echo   実行: VR最適化_管理者権限不要.bat
    echo.
) else (
    echo.
    echo ✅ GUI版ツールが正常に終了しました！
    echo.
    echo 💡 次のステップ:
    echo   1. VRアプリケーションを再起動してください
    echo   2. パフォーマンスの改善を確認してください
    echo   3. 定期的な監視・最適化を推奨します
    echo.
)

echo.
echo 📄 ログファイルと設定ファイルが生成されました。
echo 問題が発生した場合は、これらのファイルを確認してください。
echo.

pause 