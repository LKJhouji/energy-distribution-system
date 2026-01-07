# -*- coding: utf-8 -*-
"""
图表生成器 - 固定饼图尺寸，动态扩展高度
"""

import matplotlib
matplotlib.use('Agg')

from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm


def get_chinese_font():
    """获取可用的中文字体"""
    font_list = [
        'Heiti TC',
        'PingFang SC', 
        'STHeiti',
        'Hiragino Sans GB',
        'Arial Unicode MS',
    ]
    
    available_fonts = set(f.name for f in fm.fontManager.ttflist)
    
    for font in font_list:
        if font in available_fonts:
            return font
    
    return 'sans-serif'


CHINESE_FONT = get_chinese_font()
matplotlib.rcParams['font.family'] = [CHINESE_FONT, 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartGenerator:
    def __init__(self):
        self.font_family = CHINESE_FONT
    
    def create_pie_chart(self, data_dict, title="精力分配"):
        """创建饼图 - 固定饼图尺寸，根据图例数量动态调整总高度"""
        if not data_dict:
            return None

        labels = list(data_dict.keys())
        sizes = list(data_dict.values())
        total = sum(sizes)
        
        if total == 0:
            return None

        num_items = len(labels)
        
        # ========== 固定尺寸参数（单位：英寸） ==========
        FIG_WIDTH = 11.0          # 图表总宽度
        TITLE_HEIGHT = 0.7        # 标题区域高度
        PIE_SIZE = 4.5            # 饼图固定尺寸（宽=高）
        BOTTOM_MARGIN = 0.3       # 底部边距
        
        # 图例参数
        LEGEND_ITEM_HEIGHT = 0.42  # 每个图例项高度
        LEGEND_TITLE_HEIGHT = 0.6  # 图例标题高度
        LEGEND_PADDING = 0.4       # 图例上下内边距
        
        # ========== 计算所需高度 ==========
        # 左侧：饼图需要的高度
        left_content_height = PIE_SIZE
        
        # 右侧：图例需要的高度
        right_content_height = LEGEND_TITLE_HEIGHT + num_items * LEGEND_ITEM_HEIGHT + LEGEND_PADDING
        
        # 内容区取最大值
        content_height = max(left_content_height, right_content_height)
        
        # 总高度
        fig_height = TITLE_HEIGHT + content_height + BOTTOM_MARGIN
        
        # ========== 创建图表 ==========
        fig = Figure(figsize=(FIG_WIDTH, fig_height), dpi=100, facecolor='#FFFFFF')
        
        # ========== 饼图（使用绝对坐标，固定大小） ==========
        # 转换为相对坐标
        pie_left = 0.06
        pie_bottom = BOTTOM_MARGIN / fig_height
        pie_width = PIE_SIZE / FIG_WIDTH
        pie_height = PIE_SIZE / fig_height
        
        ax = fig.add_axes([pie_left, pie_bottom, pie_width, pie_height], facecolor='#FFFFFF')

        # 颜色配置
        colors = [
            '#3B82F6',  # 蓝色
            '#10B981',  # 翠绿
            '#F59E0B',  # 琥珀
            '#EF4444',  # 红色
            '#8B5CF6',  # 紫色
            '#06B6D4',  # 青色
            '#EC4899',  # 粉色
            '#6366F1',  # 靛蓝
            '#F97316',  # 橙色
            '#14B8A6',  # 蓝绿
            '#A855F7',  # 亮紫
            '#64748B',  # 灰色
            '#DC2626',  # 深红
            '#059669',  # 深绿
            '#7C3AED',  # 深紫
            '#0891B2',  # 深青
        ]
        
        while len(colors) < len(labels):
            colors.extend(colors)
        colors = colors[:len(labels)]

        # 绘制甜甜圈图
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
            startangle=90,
            pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
        )
        
        # 百分比文字样式
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
            autotext.set_color('#2D3748')

        # 中心文字
        ax.text(0, 0.06, f'{total:.1f}', fontsize=32, fontweight='bold',
                ha='center', va='center', color='#2D3748',
                fontfamily=self.font_family)
        ax.text(0, -0.18, '小时', fontsize=14,
                ha='center', va='center', color='#718096',
                fontfamily=self.font_family)

        # ========== 标题 ==========
        title_y = 1 - (TITLE_HEIGHT * 0.5 / fig_height)
        fig.text(0.30, title_y, title, fontsize=18, fontweight='bold',
                 ha='center', va='center', color='#2D3748',
                 fontfamily=self.font_family)

        # ========== 右侧图例 ==========
        legend_x = 0.54
        
        # 图例起始Y坐标（从标题下方开始）
        legend_top = 1 - (TITLE_HEIGHT / fig_height) - 0.02
        
        # 转换间距为相对坐标
        item_spacing = LEGEND_ITEM_HEIGHT / fig_height
        title_offset = LEGEND_TITLE_HEIGHT / fig_height
        
        # 图例标题位置
        legend_title_y = legend_top - 0.02
        
        # 图例项起始位置
        legend_items_start = legend_title_y - title_offset
        
        # ========== 图例背景框 ==========
        box_left = legend_x - 0.02
        box_top = legend_top + 0.02
        box_bottom = legend_items_start - num_items * item_spacing - 0.02
        box_width = 0.44
        box_height = box_top - box_bottom
        
        legend_box = FancyBboxPatch(
            (box_left, box_bottom),
            box_width, box_height,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor='#F8FAFC',
            edgecolor='#E2E8F0',
            linewidth=1.5,
            transform=fig.transFigure,
            zorder=0
        )
        fig.patches.append(legend_box)
        
        # 图例标题
        fig.text(legend_x + 0.20, legend_title_y, '分类详情', 
                 fontsize=14, fontweight='bold', color='#2D3748',
                 fontfamily=self.font_family, ha='center', va='top')
        
        # 绘制图例项
        for i, (label, size, color) in enumerate(zip(labels, sizes, colors)):
            y_pos = legend_items_start - i * item_spacing - item_spacing * 0.5
            
            # 颜色方块
            box_size = 0.018
            color_box = FancyBboxPatch(
                (legend_x, y_pos - box_size/2), box_size * 1.2, box_size,
                boxstyle="round,pad=0.002,rounding_size=0.005",
                facecolor=color,
                edgecolor='none',
                transform=fig.transFigure,
                zorder=1
            )
            fig.patches.append(color_box)
            
            # 分类名称
            fig.text(legend_x + 0.04, y_pos, label,
                    fontsize=13, color='#2D3748', va='center',
                    fontfamily=self.font_family)
            
            # 时长
            fig.text(legend_x + 0.40, y_pos, f'{size:.1f}h',
                    fontsize=13, fontweight='bold', color='#4A5568', 
                    va='center', ha='right',
                    fontfamily=self.font_family)

        return fig
