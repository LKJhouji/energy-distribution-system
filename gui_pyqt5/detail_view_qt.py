# -*- coding: utf-8 -*-
"""
PyQt5 版本 - 精力分配统计视图（完整优化版）
"""

import re
from datetime import datetime, timedelta
import calendar

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QGridLayout,
                             QMessageBox, QInputDialog, QCalendarWidget,
                             QSizePolicy, QButtonGroup, QRadioButton,
                             QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtCore import QDate, Qt, QLocale
from PyQt5.QtGui import QFont, QColor, QTextCharFormat
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class DetailViewQt(QWidget):
    """精力分配统计视图 - 完整优化版"""

    def __init__(self, data_manager, chart_generator):
        super().__init__()
        self.data_manager = data_manager
        self.chart_generator = chart_generator
        self.current_date = datetime.now().strftime('%Y.%m.%d')
        self.entries = {}
        self.stat_mode = "day"
        self.stat_date = datetime.now()
        self.init_ui()

    def add_shadow(self, widget, blur=20, offset=3, color=QColor(0, 0, 0, 40)):
        """为组件添加阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(offset)
        shadow.setYOffset(offset)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧日历面板（带滚动）
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
        """)
        
        left_panel = self.create_calendar_panel()
        left_scroll.setWidget(left_panel)
        left_scroll.setFixedWidth(340)
        main_layout.addWidget(left_scroll, 0)

        # ========== 右侧内容 - 整体滚动 ==========
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        right_scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #F0F4F8;
            }
            
            /* 紫蓝渐变垂直滚动条 */
            QScrollBar:vertical {
                background-color: #E8ECF0;
                width: 14px;
                border-radius: 7px;
                margin: 6px 3px 6px 3px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #667EEA, stop:0.5 #764BA2, stop:1 #667EEA);
                border-radius: 6px;
                min-height: 60px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5A67D8, stop:0.5 #6B46C1, stop:1 #5A67D8);
            }
            
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4C51BF, stop:0.5 #553C9A, stop:1 #4C51BF);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        right_panel = self.create_data_panel()
        right_scroll.setWidget(right_panel)
        main_layout.addWidget(right_scroll, 1)

        # 加载数据
        self.load_data()


    def create_calendar_panel(self):
        """创建左侧日历面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-right: 1px solid #E1E8ED; 
            }
        """)
        panel.setMinimumWidth(320)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(18)

        # 标题
        title = QLabel("📅 选择日期")
        title.setFont(QFont("Heiti TC", 18, QFont.Bold))
        title.setStyleSheet("color: #1A202C; border: none;")
        layout.addWidget(title)

        # 日历容器
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border: 1px solid #E2E8F0; 
                border-radius: 12px; 
            }
        """)
        self.add_shadow(calendar_frame, blur=15, offset=2, color=QColor(0, 0, 0, 25))
        
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(12, 12, 12, 12)

        # 日历 - 优化星期显示
        self.calendar = QCalendarWidget()
        
        # 设置中文locale，使用简短的星期格式
        self.calendar.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        
        # 自定义星期标题格式 - 使用单字
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: none;
            }
            
            /* 导航栏 */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #F7FAFC;
                border-bottom: 1px solid #E2E8F0;
                padding: 8px;
            }
            
            /* 月份年份按钮 - 统一样式 */
            QCalendarWidget QToolButton {
                color: #2D3748;
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #EDF2F7;
            }
            QCalendarWidget QToolButton:pressed {
                background-color: #E2E8F0;
            }
            
            /* 🔧 关键修复：隐藏月份按钮的下拉箭头 */
            QCalendarWidget QToolButton#qt_calendar_monthbutton {
                padding-right: 18px;
            }
            QCalendarWidget QToolButton#qt_calendar_monthbutton::menu-indicator {
                image: none;
                width: 0px;
                height: 0px;
            }
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
                width: 0px;
            }
            
            /* 左右箭头按钮 */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                font-size: 16px;
                font-weight: bold;
                min-width: 32px;
                qproperty-icon: none;
            }
            
            /* 下拉菜单样式 */
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px;
            }
            QCalendarWidget QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QCalendarWidget QMenu::item:selected {
                background-color: #EDF2F7;
                color: #3182CE;
            }
            
            /* 年份选择器 */
            QCalendarWidget QSpinBox {
                font-size: 14px;
                font-weight: 600;
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 8px;
                selection-background-color: #3182CE;
            }
            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }
            QCalendarWidget QSpinBox::up-button:hover,
            QCalendarWidget QSpinBox::down-button:hover {
                background-color: #EDF2F7;
            }
            
            /* 日期表格 */
            QCalendarWidget QAbstractItemView {
                outline: none;
                selection-background-color: transparent;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                color: #2D3748;
                background-color: white;
                font-size: 13px;
                selection-background-color: #3182CE;
                selection-color: white;
            }
            
            QCalendarWidget QAbstractItemView:disabled {
                color: #A0AEC0;
            }
        """)

        
        self.calendar.setMinimumHeight(240)
        self.calendar.setGridVisible(False)
        self.calendar.clicked.connect(self.on_calendar_date_selected)
        calendar_layout.addWidget(self.calendar)

        layout.addWidget(calendar_frame)

        # 当前日期显示
        date_frame = QFrame()
        date_frame.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #667EEA, stop:1 #764BA2);
                border-radius: 12px; 
            }
        """)
        self.add_shadow(date_frame, blur=15, offset=2, color=QColor(102, 126, 234, 80))
        
        date_layout = QVBoxLayout(date_frame)
        date_layout.setContentsMargins(20, 18, 20, 18)
        date_layout.setSpacing(6)

        date_title = QLabel("当前选择")
        date_title.setFont(QFont("Heiti TC", 12))
        date_title.setStyleSheet("color: rgba(255,255,255,0.8); border: none;")
        date_title.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(date_title)

        self.selected_date_label = QLabel(self.current_date)
        self.selected_date_label.setFont(QFont("Heiti TC", 24, QFont.Bold))
        self.selected_date_label.setStyleSheet("color: white; border: none;")
        self.selected_date_label.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(self.selected_date_label)

        layout.addWidget(date_frame)

        # 导航按钮
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(12)

        prev_btn = self.create_nav_button("◀ 上一天", "#4299E1", "#3182CE")
        prev_btn.clicked.connect(self.prev_day)
        nav_layout.addWidget(prev_btn)

        today_btn = self.create_nav_button("今天", "#48BB78", "#38A169")
        today_btn.clicked.connect(self.today)
        nav_layout.addWidget(today_btn)

        next_btn = self.create_nav_button("下一天 ▶", "#4299E1", "#3182CE")
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(next_btn)

        layout.addLayout(nav_layout)

        # ========== 统计模式选择 ==========
        stat_frame = QFrame()
        stat_frame.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border: 1px solid #E2E8F0; 
                border-radius: 12px; 
            }
        """)
        self.add_shadow(stat_frame, blur=15, offset=2, color=QColor(0, 0, 0, 25))
        
        stat_layout = QVBoxLayout(stat_frame)
        stat_layout.setSpacing(14)
        stat_layout.setContentsMargins(18, 18, 18, 18)

        stat_title = QLabel("📊 统计模式")
        stat_title.setFont(QFont("Heiti TC", 14, QFont.Bold))
        stat_title.setStyleSheet("color: #2D3748; border: none;")
        stat_layout.addWidget(stat_title)

        # 统计类型按钮组
        self.stat_btn_group = QButtonGroup(self)
        
        stat_btn_layout = QGridLayout()
        stat_btn_layout.setSpacing(12)
        stat_btn_layout.setContentsMargins(0, 0, 0, 0)

        stat_options = [("day", "📅 当天"), ("week", "📆 本周"), ("month", "🗓 本月"), ("year", "📊 本年")]
        for i, (mode, label) in enumerate(stat_options):
            radio = QRadioButton(label)
            radio.setFont(QFont("Heiti TC", 13))
            radio.setMinimumHeight(36)
            radio.setStyleSheet("""
                QRadioButton { 
                    color: #4A5568; 
                    padding: 8px 4px;
                    border: none;
                }
                QRadioButton::indicator { 
                    width: 20px; 
                    height: 20px; 
                }
                QRadioButton::indicator:checked {
                    background-color: #4299E1;
                    border: 2px solid #4299E1;
                    border-radius: 10px;
                }
                QRadioButton::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #CBD5E0;
                    border-radius: 10px;
                }
                QRadioButton::indicator:unchecked:hover {
                    border: 2px solid #4299E1;
                }
            """)
            if mode == "day":
                radio.setChecked(True)
            self.stat_btn_group.addButton(radio)
            radio.clicked.connect(lambda checked, m=mode: self.on_stat_mode_changed(m))
            stat_btn_layout.addWidget(radio, i // 2, i % 2)

        stat_layout.addLayout(stat_btn_layout)

        # 周/月/年导航按钮
        self.stat_nav_widget = QWidget()
        self.stat_nav_layout = QHBoxLayout(self.stat_nav_widget)
        self.stat_nav_layout.setSpacing(10)
        self.stat_nav_layout.setContentsMargins(0, 8, 0, 0)

        self.stat_prev_btn = QPushButton("◀")
        self.stat_prev_btn.setFixedSize(44, 38)
        self.stat_prev_btn.setFont(QFont("Heiti TC", 14))
        self.stat_prev_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #805AD5, stop:1 #6B46C1);
                color: white; 
                border: none; 
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6B46C1, stop:1 #553C9A);
            }
        """)
        self.stat_prev_btn.clicked.connect(self.stat_prev_period)
        self.stat_nav_layout.addWidget(self.stat_prev_btn)

        self.stat_period_label = QLabel("")
        self.stat_period_label.setFont(QFont("Heiti TC", 13, QFont.Bold))
        self.stat_period_label.setStyleSheet("color: #6B46C1; border: none;")
        self.stat_period_label.setAlignment(Qt.AlignCenter)
        self.stat_nav_layout.addWidget(self.stat_period_label, 1)

        self.stat_next_btn = QPushButton("▶")
        self.stat_next_btn.setFixedSize(44, 38)
        self.stat_next_btn.setFont(QFont("Heiti TC", 14))
        self.stat_next_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #805AD5, stop:1 #6B46C1);
                color: white; 
                border: none; 
                border-radius: 8px; 
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #6B46C1, stop:1 #553C9A);
            }
        """)
        self.stat_next_btn.clicked.connect(self.stat_next_period)
        self.stat_nav_layout.addWidget(self.stat_next_btn)

        self.stat_nav_widget.hide()
        stat_layout.addWidget(self.stat_nav_widget)

        layout.addWidget(stat_frame)
        layout.addStretch()

        return panel

    def create_nav_button(self, text, color1, color2):
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setFont(QFont("Heiti TC", 12, QFont.Bold))
        btn.setMinimumHeight(44)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color1}, stop:1 {color2});
                color: white; 
                border: none; 
                border-radius: 10px; 
                padding: 10px 16px;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color2}, stop:1 {color1});
            }}
            QPushButton:pressed {{
                padding: 11px 15px 9px 17px;
            }}
        """)
        return btn

    def create_data_panel(self):
        """创建右侧数据面板 - 带滚动条"""
        # 外层容器
        panel = QWidget()
        panel.setStyleSheet("background-color: #F0F4F8;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # ========== 滚动区域 ==========
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F0F4F8;
            }
            QScrollBar:vertical {
                background: #E2E8F0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #94A3B8;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # ========== 滚动内容 ==========
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #F0F4F8;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(20)

        # 输入卡片
        self.input_card = self.create_input_card()
        content_layout.addWidget(self.input_card)

        # 图表卡片
        self.chart_card = self.create_chart_card()
        content_layout.addWidget(self.chart_card)
        
        # 底部弹性空间
        content_layout.addStretch()
        
        # ========== 组装 ==========
        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

        return panel


    def create_input_card(self):
        """创建输入卡片 - 无内部滚动"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border: 1px solid #E2E8F0; 
                border-radius: 16px; 
            }
        """)
        self.add_shadow(card, blur=20, offset=3, color=QColor(0, 0, 0, 30))
        
        layout = QVBoxLayout(card)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 22, 24, 22)

        # 标题行
        title_layout = QHBoxLayout()
        title_layout.setSpacing(16)
        
        self.title_label = QLabel(f"⚡ 精力分配 - {self.current_date}")
        self.title_label.setFont(QFont("Heiti TC", 17, QFont.Bold))
        self.title_label.setStyleSheet("color: #1A202C; border: none;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        add_btn = self.create_action_button("+ 添加分类", "#4299E1", "#3182CE")
        add_btn.clicked.connect(self.add_category)
        title_layout.addWidget(add_btn)

        del_btn = self.create_action_button("- 删除分类", "#E53E3E", "#C53030")
        del_btn.clicked.connect(self.remove_category)
        title_layout.addWidget(del_btn)

        layout.addLayout(title_layout)

        # ========== 分类输入区域 - 直接使用 Grid，不滚动 ==========
        self.input_grid_widget = QWidget()
        self.input_grid_widget.setStyleSheet("background-color: transparent;")
        self.input_grid_layout = QGridLayout(self.input_grid_widget)
        self.input_grid_layout.setSpacing(14)
        self.input_grid_layout.setContentsMargins(2, 2, 2, 2)
        
        layout.addWidget(self.input_grid_widget)

        # 初始化分类输入
        self.refresh_category_inputs()

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        save_btn = self.create_main_button("💾 保存", "#48BB78", "#38A169")
        save_btn.clicked.connect(self.save_data)
        btn_layout.addWidget(save_btn)

        delete_btn = self.create_main_button("🗑️ 删除", "#E53E3E", "#C53030")
        delete_btn.clicked.connect(self.delete_data)
        btn_layout.addWidget(delete_btn)

        refresh_btn = self.create_main_button("🔄 刷新", "#718096", "#4A5568")
        refresh_btn.clicked.connect(self.refresh_all)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card


    def create_action_button(self, text, color1, color2):
        """创建操作按钮（小型）"""
        btn = QPushButton(text)
        btn.setFont(QFont("Heiti TC", 12, QFont.Bold))
        btn.setMinimumHeight(38)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color1}, stop:1 {color2});
                color: white; 
                border: none; 
                border-radius: 8px; 
                padding: 8px 18px;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color2}, stop:1 {color1});
            }}
        """)
        return btn

    def create_main_button(self, text, color1, color2):
        """创建主操作按钮"""
        btn = QPushButton(text)
        btn.setFont(QFont("Heiti TC", 13, QFont.Bold))
        btn.setMinimumWidth(110)
        btn.setMinimumHeight(46)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color1}, stop:1 {color2});
                color: white; 
                border: none; 
                border-radius: 10px; 
                padding: 12px 24px;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color2}, stop:1 {color1});
            }}
            QPushButton:pressed {{
                padding: 13px 23px 11px 25px;
            }}
        """)
        return btn

    def refresh_category_inputs(self):
        """刷新分类输入框"""
        # 清空旧的输入框
        while self.input_grid_layout.count():
            item = self.input_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.entries.clear()

        # 重新加载分类
        categories = self.data_manager.load_categories()
        
        col, row = 0, 0
        for category in categories:
            # 分类容器
            item_widget = QWidget()
            item_widget.setStyleSheet("background-color: transparent;")
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)
            
            # 分类标签
            label = QLabel(category)
            label.setFont(QFont("Heiti TC", 13, QFont.Bold))
            label.setStyleSheet("color: #2D3748; border: none; background: transparent;")
            label.setMinimumWidth(80)
            label.setMaximumWidth(100)
            item_layout.addWidget(label)

            # 输入框
            entry = QLineEdit()
            entry.setText("0")
            entry.setFont(QFont("Heiti TC", 13))
            entry.setMinimumHeight(40)
            entry.setMinimumWidth(100)
            entry.setMaximumWidth(140)
            entry.setStyleSheet("""
                QLineEdit { 
                    background-color: #F7FAFC; 
                    border: 2px solid #E2E8F0; 
                    border-radius: 8px; 
                    padding: 8px 12px;
                    color: #2D3748;
                }
                QLineEdit:focus { 
                    border: 2px solid #4299E1; 
                    background-color: white; 
                }
            """)
            item_layout.addWidget(entry)
            
            self.input_grid_layout.addWidget(item_widget, row, col)
            self.entries[category] = entry

            col += 1
            if col >= 4:
                col = 0
                row += 1

    def create_chart_card(self):
        """创建图表卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame { 
                background-color: #FFFFFF; 
                border: 1px solid #E2E8F0; 
                border-radius: 16px; 
            }
        """)
        # ✅ 只设最小高度，不要 setFixedHeight
        card.setMinimumHeight(800)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.add_shadow(card, blur=20, offset=3, color=QColor(0, 0, 0, 30))
        
        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(16, 16, 16, 16)

        self.chart_container = QWidget()
        self.chart_container.setStyleSheet("background-color: #FFFFFF;")
        self.chart_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.chart_container)

        return card


    # ========== 日期导航 ==========
    def on_calendar_date_selected(self, date):
        self.current_date = date.toString("yyyy.MM.dd")
        self.selected_date_label.setText(self.current_date)
        self.stat_date = datetime.strptime(self.current_date, '%Y.%m.%d')
        
        self.stat_mode = "day"
        for btn in self.stat_btn_group.buttons():
            if "当天" in btn.text():
                btn.setChecked(True)
                break
        
        self.update_stat_nav_visibility()
        self.load_data()

    def prev_day(self):
        current = QDate.fromString(self.current_date, "yyyy.MM.dd")
        prev_date = current.addDays(-1)
        self.calendar.setSelectedDate(prev_date)
        self.on_calendar_date_selected(prev_date)

    def next_day(self):
        current = QDate.fromString(self.current_date, "yyyy.MM.dd")
        next_date = current.addDays(1)
        self.calendar.setSelectedDate(next_date)
        self.on_calendar_date_selected(next_date)

    def today(self):
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.on_calendar_date_selected(today)

    # ========== 统计模式 ==========
    def on_stat_mode_changed(self, mode):
        self.stat_mode = mode
        self.stat_date = datetime.strptime(self.current_date, '%Y.%m.%d')
        self.update_stat_nav_visibility()
        self.update_chart()

    def update_stat_nav_visibility(self):
        if self.stat_mode == "day":
            self.stat_nav_widget.hide()
        else:
            self.stat_nav_widget.show()
            self.update_stat_period_label()

    def update_stat_period_label(self):
        _, _, period_str = self.get_stat_period_range()
        self.stat_period_label.setText(period_str)

    def stat_prev_period(self):
        if self.stat_mode == "week":
            self.stat_date -= timedelta(weeks=1)
        elif self.stat_mode == "month":
            if self.stat_date.month == 1:
                self.stat_date = self.stat_date.replace(year=self.stat_date.year - 1, month=12)
            else:
                self.stat_date = self.stat_date.replace(month=self.stat_date.month - 1)
        elif self.stat_mode == "year":
            self.stat_date = self.stat_date.replace(year=self.stat_date.year - 1)
        
        self.update_stat_period_label()
        self.update_chart()

    def stat_next_period(self):
        if self.stat_mode == "week":
            self.stat_date += timedelta(weeks=1)
        elif self.stat_mode == "month":
            if self.stat_date.month == 12:
                self.stat_date = self.stat_date.replace(year=self.stat_date.year + 1, month=1)
            else:
                self.stat_date = self.stat_date.replace(month=self.stat_date.month + 1)
        elif self.stat_mode == "year":
            self.stat_date = self.stat_date.replace(year=self.stat_date.year + 1)
        
        self.update_stat_period_label()
        self.update_chart()

    def get_stat_period_range(self):
        if self.stat_mode == "week":
            monday = self.stat_date - timedelta(days=self.stat_date.weekday())
            sunday = monday + timedelta(days=6)
            return monday, sunday, f"{monday.strftime('%m.%d')} ~ {sunday.strftime('%m.%d')}"
        elif self.stat_mode == "month":
            first_day = self.stat_date.replace(day=1)
            last_day = self.stat_date.replace(day=calendar.monthrange(self.stat_date.year, self.stat_date.month)[1])
            return first_day, last_day, self.stat_date.strftime('%Y年%m月')
        elif self.stat_mode == "year":
            first_day = self.stat_date.replace(month=1, day=1)
            last_day = self.stat_date.replace(month=12, day=31)
            return first_day, last_day, self.stat_date.strftime('%Y年')
        else:
            date = datetime.strptime(self.current_date, '%Y.%m.%d')
            return date, date, self.current_date

    # ========== 数据操作 ==========
    def load_data(self):
        """加载当天数据到输入框"""
        self.title_label.setText(f"⚡ 精力分配 - {self.current_date}")
        data_dict = self.data_manager.get_day_data(self.current_date)

        if data_dict:
            for category, minutes in data_dict.items():
                if category in self.entries:
                    hours = minutes / 60
                    if minutes % 60 == 0:
                        self.entries[category].setText(str(int(hours)))
                    else:
                        h, m = int(minutes // 60), int(minutes % 60)
                        self.entries[category].setText(f"{h}h{m}m" if h > 0 else f"{m}m")
        else:
            for entry in self.entries.values():
                entry.setText("0")

        self.update_chart()

    def update_chart(self, data_dict=None, title=None):
        """更新图表显示"""
        # 获取统计数据
        if self.stat_mode == "day":
            raw_data = self.data_manager.get_day_data(self.current_date)
            if raw_data:
                data_dict = {k: v / 60 for k, v in raw_data.items()}
            else:
                data_dict = {}
            title = f"{self.current_date} 精力分配"
        else:
            start_date, end_date, period_str = self.get_stat_period_range()
            raw_data = self.aggregate_data(start_date, end_date)
            if raw_data:
                data_dict = {k: v / 60 for k, v in raw_data.items()}
            else:
                data_dict = {}
            title = f"{period_str} 精力分配"
        
        # 清除旧图表
        for i in reversed(range(self.chart_layout.count())):
            child = self.chart_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                child.deleteLater()

        if not data_dict or sum(data_dict.values()) == 0:
            self.display_empty_chart()
            return

        # 创建图表
        fig = self.chart_generator.create_pie_chart(data_dict, title)
        if fig:
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background-color: #FFFFFF;")
            
            # ✅ 根据 figure 尺寸设置 canvas 大小
            fig_width, fig_height = fig.get_size_inches()
            dpi = fig.get_dpi()
            canvas.setFixedSize(int(fig_width * dpi), int(fig_height * dpi))
            
            self.chart_layout.addWidget(canvas)


    def aggregate_data(self, start_date, end_date):
        """汇总日期范围内的数据"""
        aggregated_data = {}
        current = start_date
        
        while current <= end_date:
            date_str = current.strftime('%Y.%m.%d')
            day_data = self.data_manager.get_day_data(date_str)
            
            if day_data:
                for category, minutes in day_data.items():
                    aggregated_data[category] = aggregated_data.get(category, 0) + minutes
            
            current += timedelta(days=1)
        
        return aggregated_data

    def save_data(self):
        data_dict = {}
        for category, entry in self.entries.items():
            value = entry.text().strip()
            if value and value != "0":
                minutes = self.parse_time(value)
                if minutes > 0:
                    data_dict[category] = minutes

        if self.data_manager.save_day_data(self.current_date, data_dict):
            QMessageBox.information(self, "成功", "✅ 数据已保存")
            self.load_data()
        else:
            QMessageBox.warning(self, "错误", "❌ 保存失败")

    def delete_data(self):
        reply = QMessageBox.question(self, "确认删除", "确定要删除这一天的数据吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_day_data(self.current_date):
                QMessageBox.information(self, "成功", "✅ 数据已删除")
                for entry in self.entries.values():
                    entry.setText("0")
                self.display_empty_chart()

    def refresh_all(self):
        """刷新所有"""
        self.refresh_category_inputs()
        self.load_data()

    def parse_time(self, time_str):
        time_str = time_str.strip()
        if 'h' in time_str or 'm' in time_str:
            hours, minutes = 0, 0
            matches = re.findall(r'(\d+\.?\d*)([hm])', time_str, re.IGNORECASE)
            for value, unit in matches:
                if unit.lower() == 'h':
                    hours = float(value)
                elif unit.lower() == 'm':
                    minutes = float(value)
            return int(hours * 60 + minutes)
        try:
            return int(float(time_str) * 60)
        except:
            return 0

    def display_chart(self, data_dict, title):
        """显示图表"""
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            fig = self.chart_generator.create_pie_chart(data_dict, title)
            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.chart_layout.addWidget(canvas, alignment=Qt.AlignCenter)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成图表失败: {e}")

    def display_empty_chart(self):
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 空数据提示
        empty_widget = QWidget()
        empty_widget.setStyleSheet("background: transparent;")
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(16)

        icon_label = QLabel("📊")
        icon_label.setFont(QFont("Heiti TC", 56))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("border: none; background: transparent;")
        empty_layout.addWidget(icon_label)

        text_label = QLabel("暂无数据")
        text_label.setFont(QFont("Heiti TC", 20, QFont.Bold))
        text_label.setStyleSheet("color: #A0AEC0; border: none; background: transparent;")
        text_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(text_label)

        hint_label = QLabel("请在上方输入框中填写各分类的时间")
        hint_label.setFont(QFont("Heiti TC", 13))
        hint_label.setStyleSheet("color: #CBD5E0; border: none; background: transparent;")
        hint_label.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(hint_label)

        self.chart_layout.addWidget(empty_widget, alignment=Qt.AlignCenter)

    def add_category(self):
        text, ok = QInputDialog.getText(self, "添加分类", "请输入新分类名称:")
        if ok and text:
            text = text.strip()
            categories = self.data_manager.load_categories()
            if text not in categories:
                categories.append(text)
                self.data_manager.save_categories(categories)
                self.refresh_category_inputs()
                self.load_data()
                QMessageBox.information(self, "成功", f"✅ 分类 '{text}' 已添加")
            else:
                QMessageBox.warning(self, "提示", "⚠️ 该分类已存在")

    def remove_category(self):
        categories = self.data_manager.load_categories()
        if not categories:
            QMessageBox.warning(self, "提示", "没有可删除的分类")
            return
            
        text, ok = QInputDialog.getItem(self, "删除分类", "选择要删除的分类:", categories, 0, False)
        if ok and text:
            categories.remove(text)
            self.data_manager.save_categories(categories)
            self.refresh_category_inputs()
            self.load_data()
            QMessageBox.information(self, "成功", f"✅ 分类 '{text}' 已删除")

