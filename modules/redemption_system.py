import json
import os
from typing import Dict, List, Tuple
from datetime import datetime


class RedemptionSystem:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.rewards_file = os.path.join("data", "rewards.json")
        self.redemption_history_file = os.path.join("data", "redemption_history.json")
        self._init_rewards()
    
    def _init_rewards(self):
        """初始化奖励列表"""
        if not os.path.exists(self.rewards_file):
            default_rewards = self._get_default_rewards()
            self.save_rewards(default_rewards)
    
    def _get_default_rewards(self) -> List[Dict]:
        """获取默认奖励列表（基于red_black_list.jpg和网上资源）"""
        return [
            # 小额奖励 (10-50分)
            {
                "id": "rest_10min",
                "name": "休息10分钟",
                "description": "获得10分钟的自由休息时间",
                "points": 10,
                "category": "rest",
                "emoji": "☕"
            },
            {
                "id": "water_reminder",
                "name": "补充水分",
                "description": "喝一瓶水，保持水分充足",
                "points": 10,
                "category": "health",
                "emoji": "💧"
            },
            {
                "id": "snack_healthy",
                "name": "健康小零食",
                "description": "享用一份健康的小零食",
                "points": 20,
                "category": "food",
                "emoji": "🥜"
            },
            {
                "id": "stretch_5min",
                "name": "拉伸运动",
                "description": "5分钟拉伸运动，缓解疲劳",
                "points": 20,
                "category": "health",
                "emoji": "🧘"
            },
            {
                "id": "music_break",
                "name": "音乐放松",
                "description": "听2-3首喜欢的歌曲",
                "points": 30,
                "category": "entertainment",
                "emoji": "🎵"
            },
            {
                "id": "chat_friend",
                "name": "朋友聊天",
                "description": "和朋友聊天5分钟",
                "points": 40,
                "category": "social",
                "emoji": "💬"
            },
            
            # 中等奖励 (60-200分)
            {
                "id": "meal_favorite",
                "name": "最爱的一餐",
                "description": "吃一顿自己喜欢的美食",
                "points": 60,
                "category": "food",
                "emoji": "🍜"
            },
            {
                "id": "episode_show",
                "name": "看一集剧",
                "description": "看一集喜欢的电视剧或动漫",
                "points": 80,
                "category": "entertainment",
                "emoji": "📺"
            },
            {
                "id": "game_30min",
                "name": "游戏时间",
                "description": "玩30分钟喜欢的游戏",
                "points": 100,
                "category": "entertainment",
                "emoji": "🎮"
            },
            {
                "id": "walk_outside",
                "name": "户外散步",
                "description": "到户外散步30分钟",
                "points": 100,
                "category": "health",
                "emoji": "🚶"
            },
            {
                "id": "coffee_shop",
                "name": "咖啡店学习",
                "description": "去咖啡店学习一次",
                "points": 150,
                "category": "experience",
                "emoji": "☕"
            },
            {
                "id": "movie_ticket",
                "name": "电影票一张",
                "description": "看一场电影",
                "points": 200,
                "category": "entertainment",
                "emoji": "🎬"
            },
            
            # 大额奖励 (400-2000分)
            {
                "id": "dinner_friends",
                "name": "朋友聚餐",
                "description": "和朋友一起吃大餐",
                "points": 400,
                "category": "social",
                "emoji": "🍽️"
            },
            {
                "id": "spa_massage",
                "name": "按摩放松",
                "description": "享受一次专业按摩",
                "points": 600,
                "category": "health",
                "emoji": "💆"
            },
            {
                "id": "shopping_treat",
                "name": "购物奖励",
                "description": "买一件想要的东西（限额200元）",
                "points": 800,
                "category": "shopping",
                "emoji": "🛍️"
            },
            {
                "id": "weekend_trip",
                "name": "周末短途游",
                "description": "周末去附近城市游玩",
                "points": 1000,
                "category": "travel",
                "emoji": "🏖️"
            },
            {
                "id": "new_phone",
                "name": "换新手机",
                "description": "购买新手机（如red_black_list所示）",
                "points": 2000,
                "category": "tech",
                "emoji": "📱"
            },
            
            # 特殊奖励（配合考公主题）
            {
                "id": "study_materials",
                "name": "学习资料",
                "description": "购买新的学习资料或参考书",
                "points": 150,
                "category": "study",
                "emoji": "📚"
            },
            {
                "id": "online_course",
                "name": "在线课程",
                "description": "购买一门在线学习课程",
                "points": 300,
                "category": "study",
                "emoji": "💻"
            },
            {
                "id": "mock_exam",
                "name": "模拟考试",
                "description": "参加一次专业的模拟考试",
                "points": 200,
                "category": "study",
                "emoji": "📝"
            }
        ]
    
    def save_rewards(self, rewards: List[Dict]):
        """保存奖励列表"""
        with open(self.rewards_file, 'w', encoding='utf-8') as f:
            json.dump(rewards, f, ensure_ascii=False, indent=2)
    
    def load_rewards(self) -> List[Dict]:
        """加载奖励列表"""
        with open(self.rewards_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_reward(self, reward: Dict) -> bool:
        """添加新奖励"""
        rewards = self.load_rewards()
        
        # 检查ID是否已存在
        if any(r['id'] == reward['id'] for r in rewards):
            return False
        
        rewards.append(reward)
        self.save_rewards(rewards)
        return True
    
    def update_reward(self, reward_id: str, updated_reward: Dict) -> bool:
        """更新奖励"""
        rewards = self.load_rewards()
        
        for i, r in enumerate(rewards):
            if r['id'] == reward_id:
                rewards[i] = updated_reward
                self.save_rewards(rewards)
                return True
        
        return False
    
    def delete_reward(self, reward_id: str) -> bool:
        """删除奖励"""
        rewards = self.load_rewards()
        rewards = [r for r in rewards if r['id'] != reward_id]
        self.save_rewards(rewards)
        return True
    
    def get_available_rewards(self, current_points: int) -> List[Dict]:
        """获取当前积分可兑换的奖励"""
        rewards = self.load_rewards()
        available = [r for r in rewards if r['points'] <= current_points]
        return sorted(available, key=lambda x: x['points'])
    
    def get_rewards_by_category(self, category: str = None) -> List[Dict]:
        """按类别获取奖励"""
        rewards = self.load_rewards()
        if category:
            rewards = [r for r in rewards if r['category'] == category]
        return sorted(rewards, key=lambda x: x['points'])
    
    def redeem_reward(self, reward_id: str) -> Tuple[bool, str]:
        """兑换奖励"""
        rewards = self.load_rewards()
        reward = next((r for r in rewards if r['id'] == reward_id), None)
        
        if not reward:
            return False, "奖励不存在"
        
        current_points = self.data_manager.get_total_points()
        
        if current_points < reward['points']:
            return False, f"积分不足，需要{reward['points']}分，当前只有{current_points}分"
        
        # 扣除积分
        self._deduct_points(reward['points'], reward)
        
        # 记录兑换历史
        self._record_redemption(reward)
        
        return True, f"成功兑换：{reward['name']}！"
    
    def _deduct_points(self, points: int, reward: Dict):
        """扣除积分"""
        points_data = self.data_manager._load_points()
        points_data['total_points'] -= points
        
        # 添加扣除记录
        deduction_record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'daily_points': -points,
            'total_points': points_data['total_points'],
            'details': [{
                'category': '兑换奖励',
                'item': f"兑换：{reward['name']}",
                'points': -points
            }],
            'timestamp': datetime.now().isoformat()
        }
        
        points_data['history'].append(deduction_record)
        
        with open(self.data_manager.points_file, 'w', encoding='utf-8') as f:
            json.dump(points_data, f, ensure_ascii=False, indent=2)
    
    def _record_redemption(self, reward: Dict):
        """记录兑换历史"""
        if not os.path.exists(self.redemption_history_file):
            history = []
        else:
            with open(self.redemption_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        redemption = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'reward_id': reward['id'],
            'reward_name': reward['name'],
            'points_spent': reward['points'],
            'timestamp': datetime.now().isoformat()
        }
        
        history.append(redemption)
        
        with open(self.redemption_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_redemption_history(self, days: int = None) -> List[Dict]:
        """获取兑换历史"""
        if not os.path.exists(self.redemption_history_file):
            return []
        
        with open(self.redemption_history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            history = [h for h in history if h['date'] >= cutoff_date]
        
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)
    
    def get_redemption_stats(self) -> Dict:
        """获取兑换统计"""
        history = self.get_redemption_history()
        
        if not history:
            return {
                'total_redemptions': 0,
                'total_points_spent': 0,
                'most_popular': None,
                'categories': {}
            }
        
        # 统计信息
        total_points = sum(h['points_spent'] for h in history)
        
        # 最受欢迎的奖励
        reward_counts = {}
        for h in history:
            reward_id = h['reward_id']
            reward_counts[reward_id] = reward_counts.get(reward_id, 0) + 1
        
        most_popular_id = max(reward_counts, key=reward_counts.get)
        
        # 分类统计
        rewards = self.load_rewards()
        category_stats = {}
        
        for h in history:
            reward = next((r for r in rewards if r['id'] == h['reward_id']), None)
            if reward:
                category = reward['category']
                category_stats[category] = category_stats.get(category, 0) + 1
        
        return {
            'total_redemptions': len(history),
            'total_points_spent': total_points,
            'most_popular': most_popular_id,
            'categories': category_stats
        }
    
    def format_rewards_display(self, rewards: List[Dict] = None) -> str:
        """格式化显示奖励列表"""
        if rewards is None:
            rewards = self.load_rewards()
        
        if not rewards:
            return "暂无可用奖励"
        
        # 按类别分组
        categories = {}
        for reward in rewards:
            cat = reward['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(reward)
        
        # 类别中文名称
        category_names = {
            'rest': '休息放松',
            'health': '健康养生',
            'food': '美食享受',
            'entertainment': '娱乐活动',
            'social': '社交活动',
            'experience': '体验活动',
            'shopping': '购物奖励',
            'travel': '旅行度假',
            'tech': '科技产品',
            'study': '学习进步'
        }
        
        output = []
        output.append("🎁 积分兑换商城")
        output.append("=" * 50)
        
        for cat, items in sorted(categories.items()):
            cat_name = category_names.get(cat, cat)
            output.append(f"\n📂 {cat_name}")
            output.append("-" * 30)
            
            for item in sorted(items, key=lambda x: x['points']):
                output.append(f"{item['emoji']} {item['name']} - {item['points']}分")
                output.append(f"   {item['description']}")
                output.append("")
        
        return "\n".join(output)