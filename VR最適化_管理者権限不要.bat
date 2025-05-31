@echo off
chcp 65001 > nul
title VR環境最適化ツール（管理者権限不要版）

echo.
echo ============================================================
echo 🥽 VR環境最適化ツール（管理者権限不要版）
echo ============================================================
echo VirtualDesktop、SteamVR、VRChat用PC最適化
echo 管理者権限なしで実行可能な最適化を提供します。
echo ============================================================
echo.

echo 📋 実行前の確認事項:
echo   • Pythonがインストールされていることを確認してください
echo   • 必要な依存関係がインストールされていることを確認してください
echo   • VRアプリケーションが起動している場合、より効果的です
echo.

echo 🔧 依存関係の確認とインストール...
py -3 -m pip install psutil tqdm --quiet --user

if %errorlevel% neq 0 (
    echo ❌ 依存関係のインストールに失敗しました。
    echo 手動でインストールしてください: py -3 -m pip install psutil tqdm
    pause
    exit /b 1
)

echo ✅ 依存関係の確認が完了しました。
echo.

echo 🚀 VR環境最適化ツールを起動中...
py -3 vr_optimizer_no_admin.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 最適化ツールの実行中にエラーが発生しました。
    echo.
    echo 💡 トラブルシューティング:
    echo   1. Pythonが正しくインストールされているか確認
    echo   2. 必要な権限があるか確認
    echo   3. ウイルス対策ソフトがブロックしていないか確認
    echo.
) else (
    echo.
    echo ✅ 最適化が完了しました！
    echo.
    echo 💡 次のステップ:
    echo   1. VRアプリケーションを再起動してください
    echo   2. パフォーマンスの改善を確認してください
    echo   3. 問題がある場合は、PC再起動を試してください
    echo.
)

echo.
echo 📄 ログファイルと詳細レポートが生成されました。
echo 問題が発生した場合は、これらのファイルを確認してください。
echo.

pause 