@echo off
chcp 65001 >nul
echo ========================================
echo VRChat VR環境最適化ツール（通常実行版）
powershell.exe -ExecutionPolicy Bypass -File "VRChat_VR_Optimizer_NoAdmin.ps1"
pause
