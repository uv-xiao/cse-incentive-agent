from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import re


class ScoringSystem:
    def __init__(self):
        self.scoring_rules = self._init_scoring_rules()
        self.streak_tracker = {}
        
    def _init_scoring_rules(self) -> Dict:
        return {
            "daily_checkin": {
                "name": "每日签到",
                "points": 2,
                "condition": lambda r: True
            },
            "study_duration": {
                "30": {"name": "学习30分钟", "points": 2},
                "60": {"name": "学习60分钟", "points": 4},
                "120": {"name": "学习120分钟", "points": 6},
                "180": {"name": "学习180分钟", "points": 8},
                "240": {"name": "学习240分钟", "points": 10},
                "360": {"name": "学习360分钟", "points": 12},
                "480": {"name": "学习480分钟", "points": 15}
            },
            "problems_solved": {
                "10": {"name": "完成10道题", "points": 2},
                "30": {"name": "完成30道题", "points": 4},
                "50": {"name": "完成50道题", "points": 6},
                "80": {"name": "完成80道题", "points": 8},
                "120": {"name": "完成120道题", "points": 10},
                "180": {"name": "完成180道题", "points": 12}
            },
            "sleep_quality": {
                "good": {"name": "睡眠充足(7-8小时)", "points": 1},
                "excellent": {"name": "睡眠充足(8小时以上)", "points": 2}
            },
            "diet_quality": {
                "healthy": {"name": "健康饮食", "points": 1},
                "excellent": {"name": "营养均衡", "points": 2}
            },
            "review_tasks": {
                "completed": {"name": "完成复习任务", "points": 2},
                "exceeded": {"name": "超额完成复习", "points": 4}
            },
            "note_taking": {
                "detailed": {"name": "详细笔记", "points": 2},
                "organized": {"name": "整理归纳笔记", "points": 3}
            },
            "breaks": {
                "regular": {"name": "合理休息", "points": 1},
                "excellent": {"name": "劳逸结合", "points": 2}
            },
            "weekly_perfect": {
                "name": "完美一周(7天全勤)",
                "points": 10
            },
            "monthly_perfect": {
                "name": "完美一月(30天全勤)",
                "points": 50
            },
            "penalties": {
                "no_study": {"name": "未学习", "points": -6},
                "no_checkin": {"name": "未签到", "points": -3},
                "unhealthy_diet": {"name": "不健康饮食", "points": -3},
                "poor_sleep": {"name": "睡眠不足6小时", "points": -5},
                "no_breaks": {"name": "连续学习未休息", "points": -5},
                "anxiety": {"name": "焦虑情绪", "points": -3},
                "no_thesis": {"name": "未进行论文写作", "points": -4},
                "no_memorization": {"name": "未进行背诵", "points": -3},
                "no_online_course": {"name": "未学习网课", "points": -3}
            },
            "thesis_writing": {
                "500": {"name": "论文写作500字", "points": 2},
                "1000": {"name": "论文写作1000字", "points": 4},
                "2000": {"name": "论文写作2000字", "points": 6},
                "3000": {"name": "论文写作3000字", "points": 8},
                "5000": {"name": "论文写作5000字", "points": 10}
            },
            "memorization": {
                "15": {"name": "背诵15分钟", "points": 1},
                "30": {"name": "背诵30分钟", "points": 2},
                "60": {"name": "背诵60分钟", "points": 4},
                "90": {"name": "背诵90分钟", "points": 5},
                "120": {"name": "背诵120分钟", "points": 6}
            },
            "online_course": {
                "30": {"name": "网课学习30分钟", "points": 2},
                "60": {"name": "网课学习60分钟", "points": 3},
                "90": {"name": "网课学习90分钟", "points": 4},
                "120": {"name": "网课学习120分钟", "points": 5},
                "180": {"name": "网课学习180分钟", "points": 6}
            },
            "accuracy_rate": {
                "95": {"name": "正确率95%以上", "points": 8},
                "90": {"name": "正确率90-94%", "points": 6},
                "85": {"name": "正确率85-89%", "points": 5},
                "80": {"name": "正确率80-84%", "points": 4},
                "75": {"name": "正确率75-79%", "points": 3},
                "70": {"name": "正确率70-74%", "points": 2},
                "60": {"name": "正确率60-69%", "points": 1},
                "50": {"name": "正确率50-59%", "points": 0},
                "40": {"name": "正确率40-49%", "points": -2},
                "30": {"name": "正确率30-39%", "points": -3},
                "0": {"name": "正确率低于30%", "points": -5}
            },
            "special_rewards": {
                "breakthrough": {"name": "攻克难题", "points": 5},
                "chapter_complete": {"name": "完成章节", "points": 3},
                "mock_exam_excellent": {"name": "模拟考试优秀", "points": 10},
                "help_others": {"name": "帮助他人学习", "points": 2}
            }
        }
    
    def calculate_points(self, responses: Dict, historical_data: List[Dict] = None) -> Tuple[int, List[Dict]]:
        points = 0
        point_details = []
        
        # 每日签到
        points += self.scoring_rules["daily_checkin"]["points"]
        point_details.append({
            "category": "签到",
            "item": self.scoring_rules["daily_checkin"]["name"],
            "points": self.scoring_rules["daily_checkin"]["points"]
        })
        
        # 学习时长积分
        study_duration = responses.get("study_duration", {}).get("value", 0)
        if study_duration > 0:
            for threshold, rule in sorted(self.scoring_rules["study_duration"].items(), key=lambda x: int(x[0])):
                if study_duration >= int(threshold):
                    earned_points = rule["points"]
            if study_duration >= 30:
                point_details.append({
                    "category": "学习时长",
                    "item": f"学习{study_duration}分钟",
                    "points": earned_points
                })
                points += earned_points
        else:
            # 未学习惩罚
            penalty = self.scoring_rules["penalties"]["no_study"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["no_study"]["name"],
                "points": penalty
            })
        
        # 做题积分
        problems_count = responses.get("problems_completed", {}).get("value", 0)
        if problems_count > 0:
            for threshold, rule in sorted(self.scoring_rules["problems_solved"].items(), key=lambda x: int(x[0])):
                if problems_count >= int(threshold):
                    earned_points = rule["points"]
            if problems_count >= 10:
                point_details.append({
                    "category": "练习题",
                    "item": f"完成{problems_count}道题",
                    "points": earned_points
                })
                points += earned_points
        
        # 睡眠质量积分
        sleep_quality = responses.get("sleep_quality", {}).get("value", "")
        if sleep_quality in ["good", "excellent"]:
            sleep_points = self.scoring_rules["sleep_quality"][sleep_quality]["points"]
            points += sleep_points
            point_details.append({
                "category": "生活习惯",
                "item": self.scoring_rules["sleep_quality"][sleep_quality]["name"],
                "points": sleep_points
            })
        elif sleep_quality in ["insomnia", "poor"]:
            penalty = self.scoring_rules["penalties"]["poor_sleep"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["poor_sleep"]["name"],
                "points": penalty
            })
        
        # 饮食质量积分
        diet_quality = responses.get("diet_quality", {}).get("value", "")
        if diet_quality in ["healthy", "excellent"]:
            diet_points = self.scoring_rules["diet_quality"][diet_quality]["points"]
            points += diet_points
            point_details.append({
                "category": "生活习惯",
                "item": self.scoring_rules["diet_quality"][diet_quality]["name"],
                "points": diet_points
            })
        elif diet_quality == "poor":
            penalty = self.scoring_rules["penalties"]["unhealthy_diet"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["unhealthy_diet"]["name"],
                "points": penalty
            })
        
        # 复习任务积分
        review_status = responses.get("review_completed", {}).get("value", "")
        if review_status in ["completed", "exceeded"]:
            review_points = self.scoring_rules["review_tasks"][review_status]["points"]
            points += review_points
            point_details.append({
                "category": "复习",
                "item": self.scoring_rules["review_tasks"][review_status]["name"],
                "points": review_points
            })
        
        # 笔记积分
        notes_status = responses.get("notes_taken", {}).get("value", "")
        if notes_status in ["detailed", "organized"]:
            notes_points = self.scoring_rules["note_taking"][notes_status]["points"]
            points += notes_points
            point_details.append({
                "category": "笔记",
                "item": self.scoring_rules["note_taking"][notes_status]["name"],
                "points": notes_points
            })
        
        # 休息积分/惩罚
        breaks_status = responses.get("breaks_taken", {}).get("value", "")
        if breaks_status in ["regular", "excellent"]:
            breaks_points = self.scoring_rules["breaks"][breaks_status]["points"]
            points += breaks_points
            point_details.append({
                "category": "休息",
                "item": self.scoring_rules["breaks"][breaks_status]["name"],
                "points": breaks_points
            })
        elif breaks_status == "none":
            penalty = self.scoring_rules["penalties"]["no_breaks"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["no_breaks"]["name"],
                "points": penalty
            })
        
        # 情绪状态惩罚
        emotional_state = responses.get("emotional_state", {}).get("value", "")
        if emotional_state == "anxious":
            penalty = self.scoring_rules["penalties"]["anxiety"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["anxiety"]["name"],
                "points": penalty
            })
        
        # 论文写作积分
        thesis_words = responses.get("thesis_writing", {}).get("value", 0)
        if thesis_words > 0:
            for threshold, rule in sorted(self.scoring_rules["thesis_writing"].items(), key=lambda x: int(x[0])):
                if thesis_words >= int(threshold):
                    earned_points = rule["points"]
            if thesis_words >= 500:
                point_details.append({
                    "category": "论文写作",
                    "item": f"论文写作{thesis_words}字",
                    "points": earned_points
                })
                points += earned_points
        else:
            # 未进行论文写作惩罚
            penalty = self.scoring_rules["penalties"]["no_thesis"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["no_thesis"]["name"],
                "points": penalty
            })
        
        # 背诵积分
        memorization_time = responses.get("memorization_time", {}).get("value", 0)
        if memorization_time > 0:
            for threshold, rule in sorted(self.scoring_rules["memorization"].items(), key=lambda x: int(x[0])):
                if memorization_time >= int(threshold):
                    earned_points = rule["points"]
            if memorization_time >= 15:
                point_details.append({
                    "category": "背诵",
                    "item": f"背诵{memorization_time}分钟",
                    "points": earned_points
                })
                points += earned_points
        else:
            # 未进行背诵惩罚
            penalty = self.scoring_rules["penalties"]["no_memorization"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["no_memorization"]["name"],
                "points": penalty
            })
        
        # 网课学习积分
        online_course_time = responses.get("online_course_time", {}).get("value", 0)
        if online_course_time > 0:
            for threshold, rule in sorted(self.scoring_rules["online_course"].items(), key=lambda x: int(x[0])):
                if online_course_time >= int(threshold):
                    earned_points = rule["points"]
            if online_course_time >= 30:
                point_details.append({
                    "category": "网课学习",
                    "item": f"网课学习{online_course_time}分钟",
                    "points": earned_points
                })
                points += earned_points
        else:
            # 未学习网课惩罚
            penalty = self.scoring_rules["penalties"]["no_online_course"]["points"]
            points += penalty
            point_details.append({
                "category": "惩罚",
                "item": self.scoring_rules["penalties"]["no_online_course"]["name"],
                "points": penalty
            })
        
        # 做题正确率积分/惩罚
        accuracy_rate_str = responses.get("accuracy_rate", "")
        if accuracy_rate_str:
            try:
                # 提取数字，支持多种格式：85, 85%, 85.5
                accuracy_match = re.search(r'(\d+\.?\d*)', str(accuracy_rate_str))
                if accuracy_match:
                    accuracy_rate = float(accuracy_match.group(1))
                    
                    # 只有在做了题的情况下才计算正确率积分
                    problems_count = responses.get("problems_completed", {}).get("value", 0)
                    if problems_count > 0 and 0 <= accuracy_rate <= 100:
                        # 根据正确率范围确定积分
                        accuracy_points = 0
                        accuracy_desc = ""
                        
                        if accuracy_rate >= 95:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["95"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["95"]["name"]
                        elif accuracy_rate >= 90:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["90"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["90"]["name"]
                        elif accuracy_rate >= 85:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["85"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["85"]["name"]
                        elif accuracy_rate >= 80:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["80"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["80"]["name"]
                        elif accuracy_rate >= 75:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["75"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["75"]["name"]
                        elif accuracy_rate >= 70:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["70"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["70"]["name"]
                        elif accuracy_rate >= 60:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["60"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["60"]["name"]
                        elif accuracy_rate >= 50:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["50"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["50"]["name"]
                        elif accuracy_rate >= 40:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["40"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["40"]["name"]
                        elif accuracy_rate >= 30:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["30"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["30"]["name"]
                        else:
                            accuracy_points = self.scoring_rules["accuracy_rate"]["0"]["points"]
                            accuracy_desc = self.scoring_rules["accuracy_rate"]["0"]["name"]
                        
                        points += accuracy_points
                        point_details.append({
                            "category": "做题正确率" if accuracy_points >= 0 else "惩罚",
                            "item": f"{accuracy_desc} (实际: {accuracy_rate:.1f}%)",
                            "points": accuracy_points
                        })
            except:
                pass  # 如果解析失败，忽略正确率积分
        
        # 计算连续学习奖励
        if historical_data:
            streak_bonus = self._calculate_streak_bonus(responses, historical_data)
            if streak_bonus:
                points += streak_bonus["points"]
                point_details.append(streak_bonus)
        
        return points, point_details
    
    def _calculate_streak_bonus(self, current_response: Dict, historical_data: List[Dict]) -> Dict:
        if not historical_data:
            return None
            
        # 获取最近7天和30天的数据
        current_date = datetime.strptime(current_response["date"], "%Y-%m-%d")
        week_start = current_date - timedelta(days=6)
        month_start = current_date - timedelta(days=29)
        
        week_count = 0
        month_count = 0
        
        for record in historical_data:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            if record_date >= week_start and record_date <= current_date:
                if record.get("study_duration", {}).get("value", 0) > 0:
                    week_count += 1
            if record_date >= month_start and record_date <= current_date:
                if record.get("study_duration", {}).get("value", 0) > 0:
                    month_count += 1
        
        # 检查是否有完美记录
        if week_count == 7:
            return {
                "category": "连续学习",
                "item": self.scoring_rules["weekly_perfect"]["name"],
                "points": self.scoring_rules["weekly_perfect"]["points"]
            }
        elif month_count == 30:
            return {
                "category": "连续学习",
                "item": self.scoring_rules["monthly_perfect"]["name"],
                "points": self.scoring_rules["monthly_perfect"]["points"]
            }
        
        return None
    
    def add_special_achievement(self, achievement_type: str) -> Tuple[int, Dict]:
        if achievement_type in self.scoring_rules["special_rewards"]:
            reward = self.scoring_rules["special_rewards"][achievement_type]
            return reward["points"], {
                "category": "特别成就",
                "item": reward["name"],
                "points": reward["points"]
            }
        return 0, None
    
    def get_encouragement_message(self, total_points: int, daily_points: int) -> str:
        if daily_points >= 15:
            return "🌟 太棒了！今天表现优异，继续保持这种学习劲头！"
        elif daily_points >= 10:
            return "💪 很不错！今天的学习很充实，明天继续加油！"
        elif daily_points >= 5:
            return "😊 今天有进步！坚持就是胜利，明天争取更好！"
        elif daily_points >= -5:
            return "🤗 今天有些不足，但没关系。找出问题，明天改进！"
        elif daily_points >= -10:
            return "💝 虽然今天扣分较多，但每一天都是新的开始，加油！"
        else:
            return "⚠️ 今天的惩罚分数较高，需要认真反思并制定改进计划。记住，坚持最重要！"
    
    def get_level_info(self, total_points: int) -> Dict:
        levels = [
            {"name": "初学者", "min_points": 0, "emoji": "🌱"},
            {"name": "勤奋者", "min_points": 100, "emoji": "📚"},
            {"name": "坚持者", "min_points": 300, "emoji": "💪"},
            {"name": "优秀者", "min_points": 600, "emoji": "⭐"},
            {"name": "学霸", "min_points": 1000, "emoji": "🎓"},
            {"name": "考神", "min_points": 2000, "emoji": "👑"}
        ]
        
        current_level = levels[0]
        next_level = levels[1]
        
        for i, level in enumerate(levels):
            if total_points >= level["min_points"]:
                current_level = level
                if i + 1 < len(levels):
                    next_level = levels[i + 1]
                else:
                    next_level = None
        
        return {
            "current": current_level,
            "next": next_level,
            "progress": total_points - current_level["min_points"] if next_level else 0,
            "needed": next_level["min_points"] - total_points if next_level else 0
        }