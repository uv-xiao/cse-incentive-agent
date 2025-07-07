import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd


class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.responses_file = os.path.join(data_dir, "responses.json")
        self.points_file = os.path.join(data_dir, "points.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化数据文件
        self._init_data_files()
        
        # 设置中文字体
        self._setup_chinese_font()
    
    def _init_data_files(self):
        if not os.path.exists(self.responses_file):
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        
        if not os.path.exists(self.points_file):
            with open(self.points_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_points": 0,
                    "history": []
                }, f, ensure_ascii=False)
    
    def _setup_chinese_font(self):
        # 尝试找到系统中的中文字体
        try:
            # 常见的中文字体路径
            font_paths = [
                '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                'C:\\Windows\\Fonts\\msyh.ttc'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    plt.rcParams['font.sans-serif'] = [fm.FontProperties(fname=font_path).get_name()]
                    plt.rcParams['axes.unicode_minus'] = False
                    break
        except Exception:
            # 如果找不到中文字体，使用默认设置
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    def save_response(self, response: Dict):
        responses = self._load_responses()
        
        # 检查是否已存在当天的记录
        date = response['date']
        existing_index = None
        for i, r in enumerate(responses):
            if r.get('date') == date:
                existing_index = i
                break
        
        if existing_index is not None:
            responses[existing_index] = response
        else:
            responses.append(response)
        
        # 按日期排序
        responses.sort(key=lambda x: x['date'])
        
        with open(self.responses_file, 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)
    
    def _load_responses(self) -> List[Dict]:
        with open(self.responses_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_response_by_date(self, date: str) -> Optional[Dict]:
        responses = self._load_responses()
        for response in responses:
            if response.get('date') == date:
                return response
        return None
    
    def get_recent_responses(self, days: int) -> List[Dict]:
        responses = self._load_responses()
        if not responses:
            return []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        recent_responses = []
        for response in responses:
            response_date = datetime.strptime(response['date'], '%Y-%m-%d')
            if start_date <= response_date <= end_date:
                recent_responses.append(response)
        
        return recent_responses
    
    def update_points(self, date: str, daily_points: int, point_details: List[Dict]):
        points_data = self._load_points()
        
        # 更新总积分
        points_data['total_points'] += daily_points
        
        # 更新历史记录
        history = points_data['history']
        
        # 检查是否已有当天记录
        existing_index = None
        for i, record in enumerate(history):
            if record['date'] == date:
                existing_index = i
                break
        
        new_record = {
            'date': date,
            'daily_points': daily_points,
            'total_points': points_data['total_points'],
            'details': point_details,
            'timestamp': datetime.now().isoformat()
        }
        
        if existing_index is not None:
            # 如果已存在，先减去旧的分数
            old_points = history[existing_index]['daily_points']
            points_data['total_points'] = points_data['total_points'] - old_points + daily_points
            new_record['total_points'] = points_data['total_points']
            history[existing_index] = new_record
        else:
            history.append(new_record)
        
        # 按日期排序
        history.sort(key=lambda x: x['date'])
        
        with open(self.points_file, 'w', encoding='utf-8') as f:
            json.dump(points_data, f, ensure_ascii=False, indent=2)
    
    def _load_points(self) -> Dict:
        with open(self.points_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_total_points(self) -> int:
        points_data = self._load_points()
        return points_data['total_points']
    
    def get_points_history(self, days: Optional[int] = None) -> List[Dict]:
        points_data = self._load_points()
        history = points_data['history']
        
        if days:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            filtered_history = []
            for record in history:
                record_date = datetime.strptime(record['date'], '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    filtered_history.append(record)
            
            return filtered_history
        
        return history
    
    def visualize_points_trend(self, days: int = 30) -> str:
        history = self.get_points_history(days)
        
        if not history:
            return None
        
        # 准备数据
        dates = [record['date'] for record in history]
        daily_points = [record['daily_points'] for record in history]
        total_points = [record['total_points'] for record in history]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 每日积分曲线
        ax1.plot(dates, daily_points, marker='o', linewidth=2, markersize=6)
        ax1.fill_between(range(len(dates)), daily_points, alpha=0.3)
        ax1.set_title('每日积分趋势', fontsize=16, fontweight='bold')
        ax1.set_ylabel('积分', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 添加平均线
        avg_points = sum(daily_points) / len(daily_points) if daily_points else 0
        ax1.axhline(y=avg_points, color='r', linestyle='--', alpha=0.7, 
                   label=f'平均: {avg_points:.1f}分')
        ax1.legend()
        
        # 累计积分曲线
        ax2.plot(dates, total_points, marker='s', linewidth=2, markersize=6, color='green')
        ax2.fill_between(range(len(dates)), total_points, alpha=0.3, color='green')
        ax2.set_title('累计积分趋势', fontsize=16, fontweight='bold')
        ax2.set_ylabel('总积分', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 设置x轴标签
        if len(dates) > 10:
            # 如果日期太多，只显示部分标签
            step = len(dates) // 10
            ax1.set_xticks(range(0, len(dates), step))
            ax1.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)
            ax2.set_xticks(range(0, len(dates), step))
            ax2.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)
        else:
            ax1.set_xticklabels(dates, rotation=45)
            ax2.set_xticklabels(dates, rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(self.data_dir, f'points_trend_{datetime.now().strftime("%Y%m%d")}.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_points_table(self) -> str:
        history = self.get_points_history()
        
        if not history:
            return "暂无积分记录"
        
        # 创建表格数据
        table_data = []
        for record in history[-10:]:  # 只显示最近10条
            table_data.append({
                '日期': record['date'],
                '每日积分': f"{record['daily_points']:+d}",
                '总积分': record['total_points'],
                '主要得分': ', '.join([d['item'] for d in record['details'] if d['points'] > 0][:2])
            })
        
        # 创建DataFrame
        df = pd.DataFrame(table_data)
        
        # 生成表格字符串
        table_str = df.to_string(index=False)
        
        return table_str
    
    def export_data(self, export_type: str = 'json') -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_type == 'json':
            export_data = {
                'responses': self._load_responses(),
                'points': self._load_points(),
                'export_time': datetime.now().isoformat()
            }
            
            export_path = os.path.join(self.data_dir, f'export_{timestamp}.json')
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        elif export_type == 'csv':
            # 导出积分历史为CSV
            history = self.get_points_history()
            df = pd.DataFrame(history)
            export_path = os.path.join(self.data_dir, f'points_history_{timestamp}.csv')
            df.to_csv(export_path, index=False, encoding='utf-8-sig')
        
        return export_path
    
    def get_statistics(self) -> Dict:
        responses = self._load_responses()
        points_data = self._load_points()
        
        if not responses:
            return {
                'total_days': 0,
                'total_points': 0,
                'avg_daily_points': 0,
                'total_study_time': 0,
                'total_problems': 0
            }
        
        total_study_time = sum(r.get('study_duration', {}).get('value', 0) for r in responses)
        total_problems = sum(r.get('problems_completed', {}).get('value', 0) for r in responses)
        
        history = points_data['history']
        avg_daily_points = sum(r['daily_points'] for r in history) / len(history) if history else 0
        
        return {
            'total_days': len(responses),
            'total_points': points_data['total_points'],
            'avg_daily_points': round(avg_daily_points, 1),
            'total_study_time': total_study_time,
            'total_problems': total_problems,
            'study_days': len([r for r in responses if r.get('study_duration', {}).get('value', 0) > 0])
        }
    
    def rollback_day(self, date: str) -> Dict:
        """
        回档指定日期的数据（删除问卷响应和积分记录）
        返回操作结果
        """
        result = {
            'success': False,
            'message': '',
            'deleted_response': None,
            'deleted_points': None,
            'points_adjusted': 0
        }
        
        # 1. 删除问卷响应
        responses = self._load_responses()
        original_count = len(responses)
        responses_to_keep = []
        deleted_response = None
        
        for response in responses:
            if response.get('date') == date:
                deleted_response = response
            else:
                responses_to_keep.append(response)
        
        if deleted_response:
            with open(self.responses_file, 'w', encoding='utf-8') as f:
                json.dump(responses_to_keep, f, ensure_ascii=False, indent=2)
            result['deleted_response'] = deleted_response
        
        # 2. 删除积分记录并重新计算总积分
        points_data = self._load_points()
        history = points_data['history']
        history_to_keep = []
        deleted_points = None
        
        for record in history:
            if record['date'] == date:
                deleted_points = record
            else:
                history_to_keep.append(record)
        
        if deleted_points:
            # 重新计算总积分
            points_data['history'] = history_to_keep
            
            # 从头开始重新计算总积分
            total = 0
            for i, record in enumerate(history_to_keep):
                total += record['daily_points']
                record['total_points'] = total
            
            points_data['total_points'] = total
            
            # 保存更新后的积分数据
            with open(self.points_file, 'w', encoding='utf-8') as f:
                json.dump(points_data, f, ensure_ascii=False, indent=2)
            
            result['deleted_points'] = deleted_points
            result['points_adjusted'] = deleted_points['daily_points']
        
        # 3. 设置结果
        if deleted_response or deleted_points:
            result['success'] = True
            if deleted_response and deleted_points:
                result['message'] = f"成功回档 {date} 的数据！删除了问卷记录和 {deleted_points['daily_points']} 积分。"
            elif deleted_response:
                result['message'] = f"成功删除 {date} 的问卷记录，但未找到对应的积分记录。"
            else:
                result['message'] = f"成功删除 {date} 的积分记录（{deleted_points['daily_points']}分），但未找到对应的问卷记录。"
        else:
            result['message'] = f"未找到 {date} 的任何记录。"
        
        return result
    
    def get_available_dates_for_rollback(self) -> List[str]:
        """
        获取所有可以回档的日期列表
        """
        responses = self._load_responses()
        dates = sorted([r['date'] for r in responses if 'date' in r], reverse=True)
        return dates