#!/bin/bash

echo "🚀 开始打包精力管理系统..."

# ===== 1. 清理构建文件 =====
echo "🧹 清理旧的构建文件..."
rm -rf build dist *.spec

# ===== 2. 彻底清理旧应用 =====
echo "🗑️  清理所有旧应用..."
rm -rf /Applications/精力管理系统*.app
rm -rf ~/Desktop/精力管理系统*.app

# ===== 3. 重置 Launchpad 缓存 =====
echo "🔄 重置 Launchpad..."
defaults write com.apple.dock ResetLaunchPad -bool true
killall Dock
sleep 2

# ===== 4. 打包应用 =====
echo "📦 开始打包..."
pyinstaller \
    --name="精力管理系统" \
    --windowed \
    --onefile \
    --osx-bundle-identifier=com.energy.manager \
    --add-data="core:core" \
    --add-data="gui_pyqt5:gui_pyqt5" \
    --hidden-import=PyQt5 \
    --hidden-import=matplotlib \
    --hidden-import=matplotlib.backends.backend_qt5agg \
    --collect-all matplotlib \
    main_pyqt5.py

# ===== 5. 创建数据目录并复制配置文件 =====
if [ -d "dist/精力管理系统.app" ]; then
    echo "📂 创建应用内数据目录..."
    
    # 在 .app/Contents/ 下创建 Data 目录
    DATA_DIR="dist/精力管理系统.app/Contents/Data"
    mkdir -p "$DATA_DIR"
    
    # 复制配置文件
    if [ -d "data" ]; then
        echo "📋 复制配置文件到应用内部..."
        cp data/*.json "$DATA_DIR/" 2>/dev/null || true
        echo "✅ 配置文件已复制"
    fi
    
    # 显示数据目录内容
    echo "📁 应用数据目录："
    ls -lh "$DATA_DIR/"
    
    # ===== 6. 移除安全限制并安装 =====
    echo "🔓 移除安全限制..."
    sudo xattr -cr "dist/精力管理系统.app"
    
    echo "📂 安装到应用程序..."
    cp -r "dist/精力管理系统.app" /Applications/
    
    echo ""
    echo "✅ 打包完成！"
    echo "📍 应用位置: /Applications/精力管理系统.app"
    echo "📍 数据位置: /Applications/精力管理系统.app/Contents/Data/"
else
    echo "❌ 打包失败"
    exit 1
fi
