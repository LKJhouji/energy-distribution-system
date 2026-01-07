#!/bin/bash
# Mac 应用打包脚本

# 检查 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "安装 PyInstaller..."
    pip install pyinstaller
fi

# 清理旧的构建文件
rm -rf build dist *.spec

# 构建 Mac 应用
echo "构建 macOS 应用..."
pyinstaller --onedir \
    --windowed \
    --name "精力管理系统" \
    --add-data "data:data" \
    --add-data "gui_pyqt5:gui_pyqt5" \
    --add-data "core:core" \
    main_pyqt5.py

echo "✅ macOS 应用构建完成！"
echo "应用位置: dist/精力管理系统.app"
