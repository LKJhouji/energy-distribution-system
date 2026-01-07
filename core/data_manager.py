# -*- coding: utf-8 -*-
"""
数据管理器 - JSON 格式
"""

import os
import json
import uuid
from datetime import datetime, timedelta


class DataManager:
    def __init__(self, data_file='data/energy_data.json'):
        self.data_file = data_file
        self._ensure_data_file()

    def _ensure_data_file(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    # ==================== 精力数据管理 ====================

    def save_day_data(self, date_str, data_dict):
        """保存某天的数据

        Args:
            date_str: 日期字符串 '2026.01.07' 或 '2024-01-04'
            data_dict: {'晚觉': 480, '工作': 540, ...}
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            all_data[date_str] = data_dict

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存数据出错: {e}")
            return False

    def get_day_data(self, date_str):
        """获取某天的数据

        Returns:
            dict: {'晚觉': 480, '工作': 540, ...} 或 None
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            return all_data.get(date_str, None)
        except Exception as e:
            print(f"读取数据出错: {e}")
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
        except Exception as e:
            print(f"删除数据出错: {e}")
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
        except Exception as e:
            print(f"读取数据出错: {e}")
            return {}

    # ==================== 分类管理 ====================

    def load_categories(self):
        """加载分类列表"""
        try:
            config_file = 'data/categories_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
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
            os.makedirs('data', exist_ok=True)
            with open('data/categories_config.json', 'w', encoding='utf-8') as f:
                json.dump({'categories': categories}, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存分类出错: {e}")
            return False

    # ==================== 四象限任务管理 ====================

    def _load_quadrant_tasks(self):
        """加载四象限任务"""
        try:
            config_file = 'data/quadrant_tasks.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'tasks': []}
        except Exception as e:
            print(f"加载任务出错: {e}")
            return {'tasks': []}

    def _save_quadrant_tasks(self, data):
        """保存四象限任务"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/quadrant_tasks.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存任务出错: {e}")
            return False

    def add_task(self, text, quadrant):
        """添加任务

        Args:
            text: 任务文本
            quadrant: 象限 ID ('Q1', 'Q2', 'Q3', 'Q4')

        Returns:
            task_id 或 None
        """
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

            print(f"[DataManager] 添加任务: {task}")
            data['tasks'].append(task)
            self._save_quadrant_tasks(data)

            print(f"[DataManager] 任务已保存，ID: {task_id}")
            return task_id
        except Exception as e:
            print(f"添加任务出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_tasks(self, quadrant):
        """获取象限任务

        Args:
            quadrant: 象限 ID ('Q1', 'Q2', 'Q3', 'Q4')

        Returns:
            任务列表
        """
        try:
            data = self._load_quadrant_tasks()

            # 过滤出指定象限的任务
            tasks = [t for t in data['tasks'] if t.get('quadrant') == quadrant]

            print(f"[DataManager] get_tasks({quadrant}) 返回 {len(tasks)} 个任务")
            return tasks
        except Exception as e:
            print(f"[DataManager] get_tasks 出错: {e}")
            return []

    def delete_task(self, task_id):
        """删除任务"""
        try:
            data = self._load_quadrant_tasks()
            data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
            self._save_quadrant_tasks(data)
            print(f"[DataManager] 任务已删除: {task_id}")
            return True
        except Exception as e:
            print(f"删除任务出错: {e}")
            return False

    def move_task(self, task_id, new_quadrant):
        """移动任务到其他象限"""
        try:
            data = self._load_quadrant_tasks()
            for task in data['tasks']:
                if task['id'] == task_id:
                    task['quadrant'] = new_quadrant
                    print(f"[DataManager] 任务已移动: {task_id} -> {new_quadrant}")
                    break
            self._save_quadrant_tasks(data)
            return True
        except Exception as e:
            print(f"移动任务出错: {e}")
            return False

    def toggle_task_completed(self, task_id):
        """切换任务完成状态"""
        try:
            data = self._load_quadrant_tasks()

            for task in data['tasks']:
                if task['id'] == task_id:
                    task['completed'] = not task.get('completed', False)
                    print(f"[DataManager] 任务状态切换: {task_id} -> completed={task['completed']}")
                    break

            self._save_quadrant_tasks(data)
            return True
        except Exception as e:
            print(f"切换任务状态出错: {e}")
            return False
