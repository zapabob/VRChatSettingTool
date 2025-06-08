@echo off
chcp 65001 > nul
title Windows起動時自動実行設定ツール

echo.
echo ============================================================
echo 🚀 Windows起動時自動実行設定ツール
echo ============================================================
echo VR低スペック最適化の自動実行設定を管理します
echo Microsoft公式スタートアップ設定方法準拠
echo ============================================================
echo.

echo 📋 設定オプション:
echo   1. 自動実行を有効化
echo   2. 自動実行を無効化
echo   3. 現在の設定状態確認
echo   4. 手動でスタートアップフォルダを開く
echo   5. 終了
echo.

:MENU
set /p choice="選択してください (1-5): "

if "%choice%"=="1" goto ENABLE_AUTORUN
if "%choice%"=="2" goto DISABLE_AUTORUN
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto OPEN_STARTUP_FOLDER
if "%choice%"=="5" goto EXIT
goto INVALID_CHOICE

:ENABLE_AUTORUN
echo.
echo 🚀 Windows起動時自動実行を有効化中...
echo.

echo 📋 依存関係の確認...
py -3 -m pip install psutil tqdm --quiet --user

if %errorlevel% neq 0 (
    echo ❌ 依存関係のインストールに失敗しました。
    echo 手動でインストールしてください: py -3 -m pip install psutil tqdm
    pause
    goto MENU
)

py -3 vr_lowspec_optimizer.py --enable-autorun

if %errorlevel% equ 0 (
    echo.
    echo ✅ 自動実行設定が完了しました！
    echo.
    echo 💡 設定詳細:
    echo   • レジストリ: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    echo   • スタートアップフォルダ: %%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup
    echo   • 次回Windows起動時から自動最適化が実行されます
    echo.
    echo 🔧 Windows設定での確認方法:
    echo   1. Windows設定を開く（Win + I）
    echo   2. [アプリ] → [スタートアップ] を選択
    echo   3. "VRLowSpecOptimizer" が有効になっていることを確認
    echo.
) else (
    echo ❌ 自動実行設定に失敗しました。
    echo 管理者権限で実行するか、手動設定をお試しください。
)
pause
goto MENU

:DISABLE_AUTORUN
echo.
echo ❌ Windows起動時自動実行を無効化中...
echo.

py -3 vr_lowspec_optimizer.py --disable-autorun

if %errorlevel% equ 0 (
    echo.
    echo ✅ 自動実行が無効化されました。
    echo 次回Windows起動時から自動最適化は実行されません。
    echo.
) else (
    echo ❌ 自動実行無効化に失敗しました。
)
pause
goto MENU

:CHECK_STATUS
echo.
echo 📋 現在の自動実行設定状態を確認中...
echo.

py -3 vr_lowspec_optimizer.py --check-autorun

echo.
echo 💡 設定変更方法:
echo   • 有効化: このメニューで "1" を選択
echo   • 無効化: このメニューで "2" を選択
echo   • Windows設定: Win + I → アプリ → スタートアップ
echo.
pause
goto MENU

:OPEN_STARTUP_FOLDER
echo.
echo 📁 スタートアップフォルダを開いています...
echo フォルダパス: %%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup
echo.

start "" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo ✅ スタートアップフォルダが開きました。
echo 手動でショートカットやバッチファイルを追加/削除できます。
echo.
pause
goto MENU

:INVALID_CHOICE
echo.
echo ❌ 無効な選択です。1-5の数字を入力してください。
echo.
goto MENU

:EXIT
echo.
echo 👋 Windows起動時自動実行設定ツールを終了します。
echo ご利用ありがとうございました。
echo.
pause
exit /b 0 