# -*- coding: utf-8 -*-
"""
数据管理器 - JSON 格式（数据存放在应用内部）
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta


def get_app_data_dir():
    """获取应用数据目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后：数据存放在 .app/Contents/Data/
        executable_dir = os.path.dirname(sys.executable)  # Contents/MacOS/
        contents_dir = os.path.dirname(executable_dir)    # Contents/
        app_data = os.path.join(contents_dir, 'Data')
    else:
        # 开发环境：使用项目下的 data 目录
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(current_file))
        app_data = os.path.join(project_root, 'data')
    
    os.makedirs(app_data, exist_ok=True)
    return app_data


class DataManager:
    def __init__(self, data_file=None):
        if data_file is None:
            data_dir = get_app_data_dir()
            data_file = os.path.join(data_dir, 'energy_data.json')
        
        self.data_file = data_file
        self._ensure_data_file()
        
        # 配置文件路径
        self.config_dir = get_app_data_dir()
        self.categories_file = os.path.join(self.config_dir, 'categories_config.json')
        self.quadrant_file = os.path.join(self.config_dir, 'quadrant_tasks.json')
        
        # 初始化配置文件（如果不存在）
        self._ensure_config_files()

    def _ensure_data_file(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _ensure_config_files(self):
        """确保配置文件存在（首次运行自动创建）"""
        # 1. 确保 categories_config.json 存在
        if not os.path.exists(self.categories_file):
            default_categories = {
                'categories': [
                    "晚觉", "午觉", "生活日常", "通勤",
                    "无聊刷视频", "玩游戏", "Token", "吃饭休息",
                    "健身", "工作", "副业", "思考规划"
                ]
            }
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_categories, f, ensure_ascii=False, indent=2)
        
        # 2. 确保 quadrant_tasks.json 存在
        if not os.path.exists(self.quadrant_file):
            default_tasks = {'tasks': []}
            with open(self.quadrant_file, 'w', encoding='utf-8') as f:
                json.dump(default_tasks, f, ensure_ascii=False, indent=2)

    # ==================== 精力数据管理 ====================

    def save_day_data(self, date_str, data_dict):
        """保存某天的数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            all_data[date_str] = data_dict

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception:
            return False

    def get_day_data(self, date_str):
        """获取某天的数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            return all_data.get(date_str, None)
        except Exception:
            return None

    def delete_day_data(self, date_str):
        """删除某天的数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            if date_str in all_data:
                del all_data[date_str]

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception:
            return False

    def get_date_range_data(self, start_date, end_date):
        """获取日期范围内的数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            result = {}
            for date_key in all_data:
                result[date_key] = all_data[date_key]
            return result
        except Exception:
            return {}

    # ==================== 分类管理 ====================

    def load_categories(self):
        """加载分类列表"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('categories', self._default_categories())
            return self._default_categories()
        except:
            return self._default_categories()

    def _default_categories(self):
        """默认分类列表"""
        return [
            "晚觉", "午觉", "生活日常", "通勤",
            "无聊刷视频", "玩游戏", "Token", "吃饭休息",
            "健身", "工作", "副业", "思考规划"
        ]

    def save_categories(self, categories):
        """保存分类配置"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump({'categories': categories}, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    # ==================== 四象限任务管理 ====================

    def _load_quadrant_tasks(self):
        """加载四象限任务"""
        try:
            if os.path.exists(self.quadrant_file):
                with open(self.quadrant_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'tasks': []}
        except Exception:
            return {'tasks': []}

    def _save_quadrant_tasks(self, data):
        """保存四象限任务"""
        try:
            with open(self.quadrant_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def add_task(self, text, quadrant):
        """添加任务"""
        try:
            data = self._load_quadrant_tasks()

            task_id = str(uuid.uuid4())

            task = {
                'id': task_id,
                'text': text,
                'quadrant': quadrant,
                'completed': False,
                'created_at': datetime.now().isoformat()
            }

            data['tasks'].append(task)
            self._save_quadrant_tasks(data)

            return task_id
        except Exception:
            return None

    def get_tasks(self, quadrant):
        """获取象限任务"""
        try:
            data = self._load_quadrant_tasks()
            tasks = [t for t in data['tasks'] if t.get('quadrant') == quadrant]
            return tasks
        except Exception:
            return []

    def delete_task(self, task_id):
        """删除任务"""
        try:
            data = self._load_quadrant_tasks()
            data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
            self._save_quadrant_tasks(data)
            return True
        except Exception:
            return False

    def move_task(self, task_id, new_quadrant):
        """移动任务到其他象限"""
        try:
            data = self._load_quadrant_tasks()
            for task in data['tasks']:
                if task['id'] == task_id:
                    task['quadrant'] = new_quadrant
                    break
            self._save_quadrant_tasks(data)
            return True
        except Exception:
            return False

    def toggle_task_completed(self, task_id):
        """切换任务完成状态"""
        try:
            data = self._load_quadrant_tasks()

            for task in data['tasks']:
                if task['id'] == task_id:
                    task['completed'] = not task.get('completed', False)
                    break

            self._save_quadrant_tasks(data)
            return True
        except Exception:
            return False
