@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo ==============================================
echo Ready to upload latest changes to GitHub...
echo ==============================================
echo.
git push -u origin main -f
echo.
echo ==============================================
if %errorlevel% equ 0 (
    echo Upload successful! Render will automatically sync (takes 2-3 mins).
) else (
    echo Upload failed! Please check if your GitHub login window popped up behind other windows.
)
echo ==============================================
pause
