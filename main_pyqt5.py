# -*- coding: utf-8 -*-
"""
精力管理系统 - PyQt5 版本
主应用入口 - 下拉菜单导航
"""

import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QStackedWidget, QPushButton, QMenu,
                             QLabel, QGraphicsDropShadowEffect, QFrame)
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt

from core.data_manager import DataManager
from core.chart_generator import ChartGenerator
from gui_pyqt5.detail_view_qt import DetailViewQt
from gui_pyqt5.quadrant_view_qt import QuadrantViewQt
from gui_pyqt5.styles import LIGHT_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("精力管理系统")
        self.setGeometry(50, 50, 1500, 950)
        self.setMinimumSize(1300, 850)

        # 初始化管理器
        self.data_manager = DataManager()
        self.chart_generator = ChartGenerator()

        # 缩放相关
        self.scale_factor = 1.0
        self.min_scale = 0.7
        self.max_scale = 1.5
        self.scale_step = 0.1

        # 页面配置
        self.pages = [
            {"id": "energy", "name": "精力分配统计", "icon": "📅"},
            {"id": "quadrant", "name": "四象限管理", "icon": "📊"},
        ]
        self.current_page_index = 0

        # 创建中央 widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F0F4F8;")
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部导航栏
        self.nav_bar = self.create_nav_bar()
        main_layout.addWidget(self.nav_bar)

        # 页面容器
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # 创建视图
        self.detail_view = DetailViewQt(self.data_manager, self.chart_generator)
        self.quadrant_view = QuadrantViewQt(self.data_manager)

        # 添加到堆栈
        self.stack.addWidget(self.detail_view)
        self.stack.addWidget(self.quadrant_view)

        # 启用鼠标事件
        self.setFocusPolicy(Qt.StrongFocus)

    def create_nav_bar(self):
        """创建顶部导航栏"""
        nav_bar = QFrame()
        nav_bar.setFixedHeight(52)
        nav_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #667EEA, stop:1 #764BA2);
                border: none;
            }
        """)
        
        layout = QHBoxLayout(nav_bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        # 左侧：下拉菜单按钮
        self.nav_button = QPushButton()
        self.update_nav_button_text()
        self.nav_button.setFixedHeight(36)
        self.nav_button.setMinimumWidth(180)
        self.nav_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.nav_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton::menu-indicator {
                image: none;
                width: 0px;
            }
        """)
        
        # 创建下拉菜单
        self.nav_menu = QMenu(self)
        self.nav_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                color: #2D3748;
                min-width: 160px;
            }
            QMenu::item:selected {
                background-color: #EDF2F7;
                color: #667EEA;
            }
            QMenu::item:checked {
                background-color: #667EEA;
                color: white;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E2E8F0;
                margin: 6px 12px;
            }
        """)
        
        # 添加菜单项
        for i, page in enumerate(self.pages):
            action = self.nav_menu.addAction(f"{page['icon']}  {page['name']}")
            action.setCheckable(True)
            if i == 0:
                action.setChecked(True)
            action.triggered.connect(lambda checked, idx=i: self.switch_page(idx))
        
        self.nav_button.setMenu(self.nav_menu)
        layout.addWidget(self.nav_button)

        # 中间弹性空间
        layout.addStretch()

        # 右侧：应用标题
        title_label = QLabel("⚡ 精力管理系统")
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(title_label)

        return nav_bar

    def update_nav_button_text(self):
        """更新导航按钮文字"""
        page = self.pages[self.current_page_index]
        self.nav_button.setText(f"{page['icon']}  {page['name']}  ▾")

    def switch_page(self, index):
        """切换页面"""
        self.current_page_index = index
        self.stack.setCurrentIndex(index)
        self.update_nav_button_text()

        # 更新菜单选中状态
        for i, action in enumerate(self.nav_menu.actions()):
            action.setChecked(i == index)

    def wheelEvent(self, event):
        """处理鼠标滚轮事件 - Ctrl+滚轮缩放"""
        if event.modifiers() == Qt.ControlModifier:
            # 获取滚轮方向
            delta = event.angleDelta().y()

            if delta > 0:  # 向上滚动 - 放大
                new_scale = self.scale_factor + self.scale_step
            else:  # 向下滚动 - 缩小
                new_scale = self.scale_factor - self.scale_step

            # 限制缩放范围
            new_scale = max(self.min_scale, min(self.max_scale, new_scale))

            # 只有当缩放因子改变时才更新
            if new_scale != self.scale_factor:
                self.scale_factor = new_scale
                self.apply_scale()

            event.accept()
        else:
            super().wheelEvent(event)

    def apply_scale(self):
        """应用缩放 - 只调整全局字体大小"""
        app = QApplication.instance()
        if app:
            # 计算新的字体大小
            base_size = 11  # 原始全局字体大小
            new_size = max(8, int(base_size * self.scale_factor))

            # 创建新字体并应用到应用
            font = QFont()
            font.setPointSize(new_size)
            app.setFont(font)


def main():
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyleSheet(LIGHT_STYLE)

    # 设置全局字体 - 根据平台选择
    import platform
    system = platform.system()

    if system == "Windows":
        # Windows 平台字体
        font_candidates = ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "SimSun"]
    elif system == "Darwin":
        # macOS 平台字体
        font_candidates = ["Heiti TC", "PingFang SC", "STHeiti", "Hiragino Sans GB"]
    else:
        # Linux 平台字体
        font_candidates = ["Noto Sans CJK SC", "WenQuanYi Micro Hei", "Droid Sans Fallback"]

    for font_name in font_candidates:
        font = QFont(font_name, 11)
        if font.exactMatch():
            app.setFont(font)
            break
    else:
        # 使用系统默认字体,显式指定family避免MS Sans Serif问题
        if system == "Windows":
            app.setFont(QFont("Microsoft YaHei", 11))
        else:
            app.setFont(QFont("Sans Serif", 11))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
