# -*- coding: utf-8 -*-
"""
UI 样式定义 - 优化版（下拉菜单导航）
"""

LIGHT_STYLE = """
    /* 全局背景 */
    QWidget {
        background-color: #F0F4F8;
        font-family: "Heiti TC", "PingFang SC", "STHeiti", "Hiragino Sans GB";
    }
    
    /* 主窗口 */
    QMainWindow {
        background-color: #F0F4F8;
    }
    
    /* 滚动条样式 */
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    
    QScrollBar:vertical {
        background-color: #F0F4F8;
        width: 10px;
        border-radius: 5px;
        margin: 4px 2px 4px 2px;
    }
    
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #CBD5E0, stop:1 #A0AEC0);
        border-radius: 5px;
        min-height: 40px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #A0AEC0, stop:1 #718096);
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #F0F4F8;
        height: 10px;
        border-radius: 5px;
        margin: 2px 4px 2px 4px;
    }
    
    QScrollBar::handle:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #CBD5E0, stop:1 #A0AEC0);
        border-radius: 5px;
        min-width: 40px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #A0AEC0, stop:1 #718096);
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }
    
    /* 工具提示 */
    QToolTip {
        background-color: #2D3748;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
    }
"""
