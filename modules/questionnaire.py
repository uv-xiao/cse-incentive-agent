from datetime import datetime
from typing import Dict, List, Tuple
import json


class DailyQuestionnaire:
    def __init__(self):
        self.questions = self._init_questions()
    
    def _init_questions(self) -> List[Dict]:
        return [
            {
                "id": "date",
                "question": "今天的日期",
                "type": "auto",
                "value": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "id": "study_completed",
                "question": "今天是否完成了学习计划？",
                "type": "choice",
                "options": ["✅ 完成", "📝 部分完成", "❌ 未完成"],
                "values": ["completed", "partial", "none"]
            },
            {
                "id": "study_duration",
                "question": "今天学习了多长时间？",
                "type": "choice",
                "options": [
                    "🚫 没有学习",
                    "⏱️ 30分钟以下",
                    "⏱️ 30-60分钟",
                    "⏱️ 60-120分钟",
                    "⏱️ 120-180分钟",
                    "🔥 180-240分钟",
                    "💪 240-360分钟",
                    "🚀 360-480分钟",
                    "👑 480分钟以上"
                ],
                "values": [0, 15, 45, 90, 150, 210, 300, 420, 540]
            },
            {
                "id": "problems_completed",
                "question": "今天完成了多少道练习题？",
                "type": "choice",
                "options": [
                    "🚫 没有做题",
                    "📝 1-10题",
                    "📝 11-30题", 
                    "📝 31-50题",
                    "🔥 51-80题",
                    "💪 81-120题",
                    "🚀 121-180题",
                    "👑 180题以上"
                ],
                "values": [0, 5, 20, 40, 65, 100, 150, 200]
            },
            {
                "id": "focus_level",
                "question": "今天学习时的专注程度如何？（1-10分）",
                "type": "choice",
                "options": [
                    "😵 1-2分（非常差）",
                    "😔 3-4分（较差）",
                    "😐 5-6分（一般）",
                    "😊 7-8分（良好）",
                    "🎯 9-10分（优秀）"
                ],
                "values": [1.5, 3.5, 5.5, 7.5, 9.5]
            },
            {
                "id": "emotional_state",
                "question": "今天的情绪状态如何？",
                "type": "choice",
                "options": [
                    "😣 焦虑不安",
                    "😔 有些低落",
                    "😐 平静正常",
                    "😊 积极乐观",
                    "🌟 充满斗志"
                ],
                "values": ["anxious", "low", "normal", "positive", "motivated"]
            },
            {
                "id": "physical_condition",
                "question": "今天的身体状态如何？",
                "type": "choice",
                "options": [
                    "😷 身体不适",
                    "😴 疲惫困倦",
                    "😐 状态一般",
                    "💪 精力充沛",
                    "🚀 状态极佳"
                ],
                "values": ["sick", "tired", "normal", "energetic", "excellent"]
            },
            {
                "id": "sleep_quality",
                "question": "昨晚的睡眠质量如何？",
                "type": "choice",
                "options": [
                    "😵 失眠（少于4小时）",
                    "😔 较差（4-6小时）",
                    "😐 一般（6-7小时）",
                    "😊 良好（7-8小时）",
                    "😴 充足（8小时以上）"
                ],
                "values": ["insomnia", "poor", "fair", "good", "excellent"]
            },
            {
                "id": "diet_quality",
                "question": "今天的饮食情况如何？",
                "type": "choice",
                "options": [
                    "🍔 不规律/垃圾食品",
                    "🍜 基本正常",
                    "🥗 健康均衡",
                    "🥑 非常注意营养"
                ],
                "values": ["poor", "normal", "healthy", "excellent"]
            },
            {
                "id": "breaks_taken",
                "question": "学习过程中是否合理休息？",
                "type": "choice",
                "options": [
                    "❌ 连续学习未休息",
                    "⏱️ 偶尔休息",
                    "✅ 定时休息",
                    "🧘 劳逸结合很好"
                ],
                "values": ["none", "occasional", "regular", "excellent"]
            },
            {
                "id": "review_completed",
                "question": "是否完成了复习任务？",
                "type": "choice",
                "options": [
                    "❌ 未复习",
                    "📝 复习了部分内容",
                    "✅ 完成复习计划",
                    "🌟 超额完成复习"
                ],
                "values": ["none", "partial", "completed", "exceeded"]
            },
            {
                "id": "notes_taken",
                "question": "今天的笔记和资料学习情况如何？",
                "type": "choice",
                "options": [
                    "❌ 没有做笔记/看资料",
                    "📚 使用已有资料学习",
                    "📝 简单记录",
                    "📓 详细笔记",
                    "🎨 整理归纳笔记"
                ],
                "values": ["none", "existing", "simple", "detailed", "organized"]
            },
            {
                "id": "thesis_writing",
                "question": "今天完成了多少字的论文撰写？",
                "type": "choice",
                "options": [
                    "❌ 没有写论文",
                    "📝 1-500字",
                    "📝 501-1000字",
                    "📝 1001-2000字",
                    "🔥 2001-3000字",
                    "💪 3001-5000字",
                    "🚀 5000字以上"
                ],
                "values": [0, 250, 750, 1500, 2500, 4000, 6000]
            },
            {
                "id": "memorization_time",
                "question": "今天花了多少时间背诵知识点（法律、常识、申论素材等）？",
                "type": "choice",
                "options": [
                    "❌ 没有背诵",
                    "📖 15分钟以下",
                    "📖 15-30分钟",
                    "📖 30-60分钟",
                    "🔥 60-90分钟",
                    "💪 90-120分钟",
                    "🚀 120分钟以上"
                ],
                "values": [0, 10, 22, 45, 75, 105, 150]
            },
            {
                "id": "online_course_time",
                "question": "今天观看网课学习了多长时间？",
                "type": "choice",
                "options": [
                    "❌ 没有看网课",
                    "✅ 已完成所有网课",
                    "🔄 复习已看过的内容",
                    "💻 30分钟以下",
                    "💻 30-60分钟",
                    "💻 60-90分钟",
                    "🔥 90-120分钟",
                    "💪 120-180分钟",
                    "🚀 180分钟以上"
                ],
                "values": [0, 0, 30, 15, 45, 75, 105, 150, 210]
            },
            {
                "id": "accuracy_rate",
                "question": "今天做题的正确率是多少？（请输入0-100的数字）",
                "type": "text",
                "placeholder": "例如：85 表示85%的正确率"
            },
            {
                "id": "special_achievement",
                "question": "今天有什么特别的学习成就吗？",
                "type": "text",
                "placeholder": "例如：攻克了难题、完成了某个章节、理解了难点等"
            },
            {
                "id": "tomorrow_plan",
                "question": "明天的学习计划是什么？",
                "type": "text",
                "placeholder": "简单描述明天的学习目标"
            }
        ]
    
    def generate_questionnaire(self) -> List[Dict]:
        return self.questions
    
    def validate_responses(self, responses: Dict) -> Tuple[bool, List[str]]:
        errors = []
        
        for question in self.questions:
            if question["type"] != "auto" and question["id"] not in responses:
                errors.append(f"缺少问题回答: {question['question']}")
        
        return len(errors) == 0, errors
    
    def process_responses(self, responses: Dict) -> Dict:
        processed = {}
        
        for question in self.questions:
            qid = question["id"]
            
            if question["type"] == "auto":
                # 如果响应中已经有这个字段（比如从Excel导入时设置的日期），使用响应中的值
                if qid in responses:
                    processed[qid] = responses[qid]
                else:
                    processed[qid] = question["value"]
            elif qid in responses:
                if question["type"] == "choice":
                    response_index = responses[qid]
                    if 0 <= response_index < len(question["values"]):
                        processed[qid] = {
                            "display": question["options"][response_index],
                            "value": question["values"][response_index]
                        }
                elif question["type"] == "text":
                    processed[qid] = responses[qid]
        
        processed["timestamp"] = datetime.now().isoformat()
        
        return processed
    
    def format_for_display(self) -> str:
        output = []
        output.append("=" * 50)
        output.append("📋 每日学习问卷")
        output.append("=" * 50)
        output.append("")
        
        for i, question in enumerate(self.questions):
            if question["type"] == "auto":
                continue
                
            output.append(f"问题 {i}: {question['question']}")
            
            if question["type"] == "choice":
                for j, option in enumerate(question["options"]):
                    output.append(f"  {j}. {option}")
            elif question["type"] == "text":
                output.append(f"  请输入: {question.get('placeholder', '')}")
            
            output.append("")
        
        return "\n".join(output)