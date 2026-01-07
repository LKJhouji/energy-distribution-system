@echo off
REM Windows 应用打包脚本

REM 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

REM 清理旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM 构建 Windows 应用
echo 构建 Windows 应用...
pyinstaller --onedir ^
    --windowed ^
    --name "精力管理系统" ^
    --add-data "data;data" ^
    --add-data "gui_pyqt5;gui_pyqt5" ^
    --add-data "core;core" ^
    main_pyqt5.py

echo ✅ Windows 应用构建完成！
echo 应用位置: dist\精力管理系统
pause
