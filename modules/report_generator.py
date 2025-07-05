import os
import json
import subprocess
from typing import Dict, List
from datetime import datetime
import tempfile


class ReportGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
    def generate_report(self, responses: Dict, points_details: List[Dict], 
                       total_points: int, level_info: Dict) -> str:
        prompt = self._create_gemini_prompt(responses, points_details, total_points, level_info)
        
        # 使用gemini-cli生成报告内容
        report_content = self._call_gemini(prompt)
        
        # 生成PDF报告
        report_path = self._generate_pdf(report_content, responses["date"])
        
        return report_path
    
    def _create_gemini_prompt(self, responses: Dict, points_details: List[Dict], 
                             total_points: int, level_info: Dict) -> str:
        # 获取历史数据用于分析趋势
        historical_data = self.data_manager.get_recent_responses(7)
        
        prompt = f"""你是ZZW的考公学习助手。请根据今天的学习情况生成一份鼓励性的每日总结报告。

# 今日学习数据

日期：{responses['date']}

## 学习情况
- 学习计划完成情况：{responses.get('study_completed', {}).get('display', '未知')}
- 学习时长：{responses.get('study_duration', {}).get('display', '未知')}
- 完成练习题：{responses.get('problems_completed', {}).get('display', '未知')}
- 专注程度：{responses.get('focus_level', {}).get('display', '未知')}
- 复习情况：{responses.get('review_completed', {}).get('display', '未知')}
- 笔记情况：{responses.get('notes_taken', {}).get('display', '未知')}

## 身心状态
- 情绪状态：{responses.get('emotional_state', {}).get('display', '未知')}
- 身体状态：{responses.get('physical_condition', {}).get('display', '未知')}
- 睡眠质量：{responses.get('sleep_quality', {}).get('display', '未知')}
- 饮食情况：{responses.get('diet_quality', {}).get('display', '未知')}
- 休息情况：{responses.get('breaks_taken', {}).get('display', '未知')}

## 今日积分详情
"""
        
        # 添加积分明细
        for detail in points_details:
            prompt += f"- [{detail['category']}] {detail['item']}: {'+' if detail['points'] > 0 else ''}{detail['points']}分\n"
        
        daily_points = sum(d['points'] for d in points_details)
        prompt += f"\n**今日得分：{daily_points}分**\n"
        prompt += f"**总积分：{total_points}分**\n"
        prompt += f"\n## 等级信息\n"
        prompt += f"当前等级：{level_info['current']['emoji']} {level_info['current']['name']} ({level_info['current']['min_points']}分)\n"
        
        if level_info['next']:
            prompt += f"下一等级：{level_info['next']['emoji']} {level_info['next']['name']} (还需{level_info['needed']}分)\n"
        
        # 添加特别成就和明天计划
        if responses.get('special_achievement'):
            prompt += f"\n## 今日特别成就\n{responses['special_achievement']}\n"
        
        if responses.get('tomorrow_plan'):
            prompt += f"\n## 明天计划\n{responses['tomorrow_plan']}\n"
        
        # 添加历史趋势分析
        if historical_data:
            prompt += "\n## 近期学习趋势\n"
            recent_points = []
            for record in historical_data[-7:]:
                if 'daily_points' in record:
                    recent_points.append(record['daily_points'])
            
            if recent_points:
                avg_points = sum(recent_points) / len(recent_points)
                prompt += f"- 最近{len(recent_points)}天平均得分：{avg_points:.1f}分\n"
                prompt += f"- 趋势：{'上升' if daily_points > avg_points else '下降' if daily_points < avg_points else '持平'}\n"
        
        prompt += """
# 生成要求

请生成一份富有情感价值的每日总结报告，要求：

1. **整体基调**：积极向上、温暖鼓励
2. **内容结构**：
   - 开头：温暖的问候和今日总评
   - 数据分析：用生动的语言分析今天的学习和生活状态
   - 积分说明：解释得分情况，重点表扬做得好的地方
   - 改进建议：温和地提出1-2个明天可以改进的小目标
   - 结尾：充满正能量的鼓励话语

3. **视觉元素**：
   - 大量使用emoji让报告生动有趣
   - 用Markdown格式让内容层次分明
   - 可以加入一些励志名言或小贴士

4. **特别注意**：
   - 即使今天表现不理想，也要找出亮点给予肯定
   - 建议要具体可行，不要给太大压力
   - 语气要像朋友一样亲切自然

请用Markdown格式生成报告内容。"""
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> str:
        try:
            # 将prompt写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # 调用gemini-cli
            result = subprocess.run(
                ['gemini', '-f', prompt_file],
                capture_output=True,
                text=True
            )
            
            # 删除临时文件
            os.unlink(prompt_file)
            
            if result.returncode == 0:
                return result.stdout
            else:
                # 如果gemini-cli调用失败，使用备用模板
                return self._generate_fallback_report(prompt)
                
        except Exception as e:
            print(f"调用gemini-cli失败: {e}")
            return self._generate_fallback_report(prompt)
    
    def _generate_fallback_report(self, prompt: str) -> str:
        # 备用报告模板
        return """# 📚 每日学习总结报告

## 🌟 今日表现

亲爱的ZZW，今天又是充实的一天！

根据你今天的学习记录，我为你整理了以下内容：

### 📊 学习数据
- 你今天完成了学习任务
- 积累了宝贵的学习经验
- 在考公路上又前进了一步

### 💪 值得肯定的地方
- 坚持打卡，保持学习节奏
- 认真对待每一道练习题
- 保持积极的学习态度

### 🎯 明日小目标
1. 继续保持学习习惯
2. 适当增加练习题数量
3. 注意劳逸结合

## 💝 温馨寄语

考公之路虽然漫长，但每一天的坚持都在让你变得更强大。相信自己，你一定能够实现目标！

> "不积跬步，无以至千里。" 

继续加油！明天会更好！🌈

---
*Generated with ❤️ for ZZW*"""
    
    def _generate_pdf(self, content: str, date: str) -> str:
        # 确保报告目录存在
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"daily_report_{date}.md"
        filepath = os.path.join(report_dir, filename)
        
        # 保存Markdown文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 尝试使用pandoc转换为PDF（如果可用）
        pdf_path = filepath.replace('.md', '.pdf')
        try:
            result = subprocess.run(
                ['pandoc', filepath, '-o', pdf_path, '--pdf-engine=xelatex', 
                 '-V', 'CJKmainfont=Noto Sans CJK SC'],
                capture_output=True
            )
            if result.returncode == 0:
                return pdf_path
        except Exception:
            pass
        
        # 如果PDF生成失败，返回Markdown路径
        return filepath
    
    def generate_weekly_summary(self) -> str:
        # 获取最近7天的数据
        recent_data = self.data_manager.get_recent_responses(7)
        
        if not recent_data:
            return None
        
        prompt = self._create_weekly_summary_prompt(recent_data)
        content = self._call_gemini(prompt)
        
        # 生成周报文件
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"weekly_summary_{date_str}.md"
        filepath = os.path.join("reports", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _create_weekly_summary_prompt(self, recent_data: List[Dict]) -> str:
        prompt = """请生成一份考公学习周报，包含：

# 本周学习数据

"""
        
        total_study_time = 0
        total_problems = 0
        total_points = 0
        study_days = 0
        
        for record in recent_data:
            if record.get('study_duration', {}).get('value', 0) > 0:
                study_days += 1
                total_study_time += record['study_duration']['value']
            
            total_problems += record.get('problems_completed', {}).get('value', 0)
            total_points += record.get('daily_points', 0)
        
        prompt += f"""
- 学习天数：{study_days}/7天
- 总学习时长：{total_study_time}分钟
- 完成题目数：{total_problems}道
- 本周总积分：{total_points}分
- 平均每日积分：{total_points/7:.1f}分

请生成一份鼓励性的周报，包括：
1. 本周亮点总结
2. 进步分析
3. 下周建议
4. 励志寄语

使用温暖鼓励的语气，多用emoji。
"""
        
        return prompt