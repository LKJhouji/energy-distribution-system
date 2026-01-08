# -*- coding: utf-8 -*-
"""
PyQt5 版本 - 四象限任务管理视图（完整优化版）
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QListWidget,
                             QListWidgetItem, QMenu, QGridLayout,
                             QSizePolicy, QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class TaskItemWidget(QWidget):
    """自定义任务项组件，包含任务文本和操作按钮"""

    task_clicked = pyqtSignal(str)      # task_id
    delete_clicked = pyqtSignal(str)    # task_id
    move_up_clicked = pyqtSignal(str)   # task_id
    move_down_clicked = pyqtSignal(str) # task_id

    def __init__(self, task_id, task_text, is_completed, color, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.task_text = task_text
        self.is_completed = is_completed
        self.color = color

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setMinimumHeight(40)
        self.setStyleSheet("background-color: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignVCenter)

        # 任务文本标签
        self.task_label = QLabel()
        self.update_label()
        self.task_label.setCursor(Qt.PointingHandCursor)
        self.task_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.task_label, 1)

        # 上移按钮
        up_btn = QPushButton("↑")
        up_btn.setFixedSize(32, 32)
        up_btn.setFont(QFont("Heiti TC", 14, QFont.Bold))
        up_btn.setCursor(Qt.PointingHandCursor)
        up_btn.setToolTip("上移")
        up_btn.clicked.connect(lambda: self.move_up_clicked.emit(self.task_id))
        up_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.color};
                color: white;
                border: none;
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
        """)
        layout.addWidget(up_btn)

        # 下移按钮
        down_btn = QPushButton("↓")
        down_btn.setFixedSize(32, 32)
        down_btn.setFont(QFont("Heiti TC", 14, QFont.Bold))
        down_btn.setCursor(Qt.PointingHandCursor)
        down_btn.setToolTip("下移")
        down_btn.clicked.connect(lambda: self.move_down_clicked.emit(self.task_id))
        down_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.color};
                color: white;
                border: none;
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
        """)
        layout.addWidget(down_btn)

        # 删除按钮
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(32, 32)
        del_btn.setFont(QFont("Heiti TC", 14, QFont.Bold))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("删除")
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self.task_id))
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.color};
                color: white;
                border: none;
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
        """)
        layout.addWidget(del_btn)

        # 连接任务文本点击事件
        self.task_label.mousePressEvent = self.on_task_text_clicked

    def update_label(self):
        """更新任务文本标签"""
        if self.is_completed:
            text = f"✅ {self.task_text}"
            color = '#A0AEC0'
            font = QFont("Heiti TC", 13)
            font.setItalic(True)
        else:
            text = f"⬜ {self.task_text}"
            color = self.color
            font = QFont("Heiti TC", 13)

        self.task_label.setText(text)
        self.task_label.setFont(font)
        self.task_label.setStyleSheet(f"color: {color}; background-color: transparent; border: none;")

    def on_task_text_clicked(self, event):
        """处理任务文本点击事件"""
        self.task_clicked.emit(self.task_id)

    def set_completed(self, is_completed):
        """更新完成状态"""
        self.is_completed = is_completed
        self.update_label()



class QuadrantViewQt(QWidget):
    """四象限任务管理视图 - 完整优化版"""

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.quadrants = {
            'Q1': {'name': '重要且紧急', 'color': '#E53E3E', 'bg': '#FFF5F5', 'icon': '🔥', 'desc': '立即处理'},
            'Q2': {'name': '重要不紧急', 'color': '#38A169', 'bg': '#F0FFF4', 'icon': '🎯', 'desc': '计划执行'},
            'Q3': {'name': '紧急不重要', 'color': '#D69E2E', 'bg': '#FFFFF0', 'icon': '⚡', 'desc': '委托他人'},
            'Q4': {'name': '不重要不紧急', 'color': '#718096', 'bg': '#F7FAFC', 'icon': '💤', 'desc': '尽量避免'}
        }
        self.task_lists = {}
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
        # 主滚动区域
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: #F0F4F8;
            }
        """)

        # 内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #F0F4F8;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(24, 24, 24, 24)

        # 四象限网格布局 - 2x2
        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.create_quadrant_card('Q1'), 0, 0)
        grid.addWidget(self.create_quadrant_card('Q2'), 0, 1)
        grid.addWidget(self.create_quadrant_card('Q3'), 1, 0)
        grid.addWidget(self.create_quadrant_card('Q4'), 1, 1)

        content_layout.addLayout(grid, 1)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def create_quadrant_card(self, quadrant_id):
        """创建象限卡片"""
        info = self.quadrants[quadrant_id]
        color = info['color']
        bg = info['bg']
        name = info['name']
        icon = info['icon']
        desc = info['desc']

        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card.setMinimumSize(400, 300)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: none;
                border-radius: 16px;
            }}
        """)
        self.add_shadow(card, blur=25, offset=4, color=QColor(0, 0, 0, 35))

        layout = QVBoxLayout(card)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 18, 20, 18)

        # 标题行 - 带背景色
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{ 
                background-color: {bg}; 
                border-radius: 10px;
            }}
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel(f"{icon} {quadrant_id}: {name}")
        title.setFont(QFont("Heiti TC", 15, QFont.Bold))
        title.setStyleSheet(f"color: {color}; border: none;")
        title_layout.addWidget(title)

        title_layout.addStretch()

        desc_label = QLabel(desc)
        desc_label.setFont(QFont("Heiti TC", 12))
        desc_label.setStyleSheet(f"color: {color}; opacity: 0.8; border: none;")
        title_layout.addWidget(desc_label)

        layout.addWidget(title_frame)

        # 输入框和添加按钮
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        input_field = QLineEdit()
        input_field.setPlaceholderText("输入新任务按回车添加...")
        input_field.setFont(QFont("Heiti TC", 13))
        input_field.setMinimumHeight(46)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 10px 16px;
                color: #2D3748;
            }}
            QLineEdit:focus {{
                border: 2px solid {color};
                background-color: white;
            }}
            QLineEdit::placeholder {{
                color: #A0AEC0;
            }}
        """)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(46, 46)
        add_btn.setFont(QFont("Heiti TC", 22, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color}, stop:1 {self.darken_color(color)});
                color: white;
                border: none;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {self.darken_color(color)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                padding-top: 2px;
            }}
        """)

        input_layout.addWidget(input_field, 1)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        # 任务列表
        task_list = QListWidget()
        task_list.setMinimumHeight(200)
        task_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #FAFBFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 0px 12px 12px 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 4px 0px;
                margin: 0px 0px;
                background-color: transparent;
                border: none;
            }}
            QListWidget::item:selected {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: transparent;
                border: none;
            }}

            /* 复选框样式 */
            QListWidget::indicator {{
                width: 18px;
                height: 18px;
            }}
            QListWidget::indicator:unchecked {{
                border: 2px solid {color};
                border-radius: 3px;
                background-color: white;
            }}
            QListWidget::indicator:checked {{
                border: 2px solid {color};
                border-radius: 3px;
                background-color: {color};
            }}

            /* 滚动条 - 主题渐变色 */
            QScrollBar:vertical {{
                background-color: #F0F4F8;
                width: 10px;
                border-radius: 5px;
                margin: 4px 2px 4px 2px;
            }}

            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {color}, stop:1 {self.darken_color(color)});
                border-radius: 5px;
                min-height: 40px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {self.darken_color(color)}, stop:1 {color});
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        layout.addWidget(task_list, 1)

        # 存储引用
        self.task_lists[quadrant_id] = task_list

        # ========== 添加任务功能 ==========
        def add_task():
            """添加任务（本地函数）"""
            text = input_field.text().strip()

            if text:
                task_id = self.data_manager.add_task(text, quadrant_id)

                if task_id:
                    input_field.clear()
                    self.refresh_task_list(quadrant_id)

        add_btn.clicked.connect(add_task)
        input_field.returnPressed.connect(add_task)

        # 加载任务
        self.refresh_task_list(quadrant_id)

        return card

    def darken_color(self, hex_color):
        """将颜色变暗"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.82))
        g = max(0, int(g * 0.82))
        b = max(0, int(b * 0.82))
        return f'#{r:02x}{g:02x}{b:02x}'

    def refresh_task_list(self, quadrant_id):
        """刷新任务列表"""
        task_list = self.task_lists.get(quadrant_id)

        if task_list is None:
            return

        task_list.clear()

        tasks = self.data_manager.get_tasks(quadrant_id)

        # 获取象限颜色信息
        quadrant_info = self.quadrants.get(quadrant_id, {})
        color = quadrant_info.get('color', '#667EEA')

        for task in tasks:
            # 创建自定义任务项组件
            task_widget = TaskItemWidget(
                task['id'],
                task['text'],
                task.get('completed', False),
                color
            )

            # 连接信号
            task_widget.task_clicked.connect(
                lambda task_id: self.on_task_completed_toggled(task_id, quadrant_id)
            )
            task_widget.delete_clicked.connect(
                lambda task_id: self.on_task_deleted(task_id, quadrant_id)
            )
            task_widget.move_up_clicked.connect(
                lambda task_id: self.on_task_moved_up(task_id, quadrant_id)
            )
            task_widget.move_down_clicked.connect(
                lambda task_id: self.on_task_moved_down(task_id, quadrant_id)
            )

            # 创建列表项并设置自定义组件
            item = QListWidgetItem(task_list)
            item.setData(Qt.UserRole, task['id'])
            item.setSizeHint(task_widget.sizeHint())
            task_list.setItemWidget(item, task_widget)


    def on_task_completed_toggled(self, task_id, quadrant_id):
        """处理任务完成状态切换"""
        self.data_manager.toggle_task_completed(task_id)
        self.refresh_task_list(quadrant_id)

    def on_task_deleted(self, task_id, quadrant_id):
        """处理任务删除"""
        self.data_manager.delete_task(task_id)
        self.refresh_task_list(quadrant_id)

    def on_task_moved_up(self, task_id, quadrant_id):
        """处理任务上移"""
        tasks = self.data_manager.get_tasks(quadrant_id)
        current_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)

        if current_index is not None and current_index > 0:
            # 交换位置
            tasks[current_index], tasks[current_index - 1] = tasks[current_index - 1], tasks[current_index]

            # 保存重新排序后的任务列表
            data = self.data_manager._load_quadrant_tasks()
            quadrant_task_indices = [i for i, t in enumerate(data['tasks']) if t.get('quadrant') == quadrant_id]

            for new_idx, task in enumerate(tasks):
                old_idx = quadrant_task_indices[new_idx]
                data['tasks'][old_idx] = task

            self.data_manager._save_quadrant_tasks(data)
            self.refresh_task_list(quadrant_id)

    def on_task_moved_down(self, task_id, quadrant_id):
        """处理任务下移"""
        tasks = self.data_manager.get_tasks(quadrant_id)
        current_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)

        if current_index is not None and current_index < len(tasks) - 1:
            # 交换位置
            tasks[current_index], tasks[current_index + 1] = tasks[current_index + 1], tasks[current_index]

            # 保存重新排序后的任务列表
            data = self.data_manager._load_quadrant_tasks()
            quadrant_task_indices = [i for i, t in enumerate(data['tasks']) if t.get('quadrant') == quadrant_id]

            for new_idx, task in enumerate(tasks):
                old_idx = quadrant_task_indices[new_idx]
                data['tasks'][old_idx] = task

            self.data_manager._save_quadrant_tasks(data)
            self.refresh_task_list(quadrant_id)



    def show_context_menu(self, position, quadrant_id, task_list):
        """显示右键菜单"""
        item = task_list.itemAt(position)
        if not item:
            return

        task_id = item.data(Qt.UserRole)
        tasks = self.data_manager.get_tasks(quadrant_id)
        task = next((t for t in tasks if t['id'] == task_id), None)

        if not task:
            return

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 12px 28px;
                border-radius: 8px;
                font-size: 14px;
                color: #2D3748;
            }
            QMenu::item:selected {
                background-color: #EDF2F7;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E2E8F0;
                margin: 6px 14px;
            }
        """)

        # 完成/未完成
        if task.get('completed', False):
            toggle_action = menu.addAction("⬜ 标记未完成")
        else:
            toggle_action = menu.addAction("✅ 标记完成")

        menu.addSeparator()

        # 移动到其他象限
        move_menu = menu.addMenu("📦 移动到...")
        move_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                padding: 10px 24px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #EDF2F7;
            }
        """)

        for qid, info in self.quadrants.items():
            if qid != quadrant_id:
                move_action = move_menu.addAction(f"{info['icon']} {qid}: {info['name']}")
                move_action.setData(qid)

        menu.addSeparator()

        # 删除
        delete_action = menu.addAction("🗑️ 删除任务")

        # 执行菜单
        action = menu.exec_(task_list.mapToGlobal(position))

        if action == toggle_action:
            self.data_manager.toggle_task_completed(task_id)
            self.refresh_task_list(quadrant_id)
        elif action == delete_action:
            self.data_manager.delete_task(task_id)
            self.refresh_task_list(quadrant_id)
        elif action and action.data():
            new_quadrant = action.data()
            self.data_manager.move_task(task_id, new_quadrant)
            self.refresh_task_list(quadrant_id)
            self.refresh_task_list(new_quadrant)
