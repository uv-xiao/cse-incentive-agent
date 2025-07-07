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
- 学习时长：{responses.get('study_duration', {}).get('display', '未知')} (实际值: {responses.get('study_duration', {}).get('value', 0)}分钟)
- 完成练习题：{responses.get('problems_completed', {}).get('display', '未知')} (实际值: {responses.get('problems_completed', {}).get('value', 0)}道)
- 做题正确率：{responses.get('accuracy_rate', '未知')}
- 专注程度：{responses.get('focus_level', {}).get('display', '未知')}
- 复习情况：{responses.get('review_completed', {}).get('display', '未知')}
- 笔记情况：{responses.get('notes_taken', {}).get('display', '未知')}

## 扩展学习项目
- 论文写作：{responses.get('thesis_writing', {}).get('display', '未知')} (实际值: {responses.get('thesis_writing', {}).get('value', 0)}字)
- 背诵时间：{responses.get('memorization_time', {}).get('display', '未知')} (实际值: {responses.get('memorization_time', {}).get('value', 0)}分钟)
- 网课学习：{responses.get('online_course_time', {}).get('display', '未知')} (实际值: {responses.get('online_course_time', {}).get('value', 0)}分钟)

## 身心状态
- 情绪状态：{responses.get('emotional_state', {}).get('display', '未知')}
- 身体状态：{responses.get('physical_condition', {}).get('display', '未知')}
- 睡眠质量：{responses.get('sleep_quality', {}).get('display', '未知')}
- 饮食情况：{responses.get('diet_quality', {}).get('display', '未知')}
- 休息情况：{responses.get('breaks_taken', {}).get('display', '未知')}

## 今日积分详情
"""
        
        # 按类别组织积分明细
        categories = {}
        for detail in points_details:
            category = detail['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(detail)
        
        # 按类别输出积分明细
        for category, items in categories.items():
            prompt += f"\n### {category}\n"
            for item in items:
                prompt += f"- {item['item']}: {'+' if item['points'] > 0 else ''}{item['points']}分\n"
        
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
        
        # 添加积分规则说明
        prompt += """

## 积分规则详解

### 🎯 奖励积分规则
1. **基础积分**：
   - 每日签到：+2分（每天登录就能获得）
   
2. **学习时长积分**（累进制）：
   - 30-59分钟：+2分
   - 60-119分钟：+4分
   - 120-179分钟：+6分
   - 180-239分钟：+8分
   - 240-359分钟：+10分
   - 360-479分钟：+12分
   - 480分钟以上：+15分
   
3. **练习题积分**（累进制）：
   - 10-29道：+2分
   - 30-49道：+4分
   - 50-79道：+6分
   - 80-119道：+8分
   - 120-179道：+10分
   - 180道以上：+12分
   
4. **做题正确率积分**（仅在完成练习题时计算）：
   - 95%以上：+8分（优秀）
   - 90-94%：+6分（很好）
   - 85-89%：+5分（良好）
   - 80-84%：+4分（不错）
   - 75-79%：+3分（及格）
   - 70-74%：+2分（需加强）
   - 60-69%：+1分（警告）
   - 50-59%：0分（较差）
   
5. **生活习惯积分**：
   - 睡眠7-8小时：+1分
   - 睡眠8小时以上：+2分
   - 健康饮食：+1分
   - 营养均衡：+2分
   - 合理休息：+1分
   - 劳逸结合：+2分
   
6. **学习质量积分**：
   - 完成复习任务：+2分
   - 超额完成复习：+4分
   - 详细笔记：+2分
   - 整理归纳笔记：+3分
   
7. **扩展项目积分**：
   - 论文写作500-999字：+2分
   - 论文写作1000-1999字：+4分
   - 论文写作2000-2999字：+6分
   - 论文写作3000-4999字：+8分
   - 论文写作5000字以上：+10分
   - 背诵15-29分钟：+1分
   - 背诵30-59分钟：+2分
   - 背诵60-89分钟：+4分
   - 背诵90-119分钟：+5分
   - 背诵120分钟以上：+6分
   - 网课30-59分钟：+2分
   - 网课60-89分钟：+3分
   - 网课90-119分钟：+4分
   - 网课120-179分钟：+5分
   - 网课180分钟以上：+6分
   
8. **连续学习奖励**：
   - 完美一周（7天全勤）：+10分
   - 完美一月（30天全勤）：+50分

### ⚠️ 惩罚积分规则（强化版）
1. **学习相关**：
   - 未学习：-6分
   - 未签到：-3分
   - 做题正确率40-49%：-2分
   - 做题正确率30-39%：-3分
   - 做题正确率低于30%：-5分
   
2. **生活习惯**：
   - 睡眠不足6小时：-5分
   - 不健康饮食：-3分
   - 连续学习未休息：-5分
   - 焦虑情绪：-3分
   
3. **扩展项目**：
   - 未进行论文写作：-4分
   - 未进行背诵：-3分
   - 未学习网课：-3分

"""
        
        prompt += """
# 生成要求

请生成一份富有情感价值的每日总结报告，要求：

1. **整体基调**：积极向上、温暖鼓励
2. **内容结构**：
   - 开头：温暖的问候和今日总评
   - 数据分析：用生动的语言分析今天的学习和生活状态
   - **积分分析**：
     * 详细解释今天获得的每一项积分，说明为什么能获得这些分数
     * 分析哪些方面做得好（获得高分的项目）
     * 温和地指出扣分项，并说明改进方法
     * 对比积分规则，分析还有哪些提升空间
   - 改进建议：基于积分分析，提出1-2个明天可以改进的具体小目标
   - 结尾：充满正能量的鼓励话语

3. **积分分析要求**：
   - 不要只列出积分，要解释每项积分背后的意义
   - 对于学习时长和做题数量，要分析是否达到了较高的积分档位
   - 对于扣分项，要温和地分析原因并给出改进建议
   - 总结今天的积分构成，哪个类别贡献最多，哪个类别还有提升空间

4. **视觉元素**：
   - 大量使用emoji让报告生动有趣
   - 用Markdown格式让内容层次分明
   - 可以加入一些励志名言或小贴士

5. **特别注意**：
   - 即使今天表现不理想，也要找出亮点给予肯定
   - 建议要具体可行，不要给太大压力
   - 语气要像朋友一样亲切自然
   - 积分分析要详细但不枯燥，用生动的语言描述

请用Markdown格式生成报告内容。"""
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> str:
        try:
            # 为了避免prompt太长，提取关键信息创建简短的prompt
            # 提取今日学习数据部分
            data_start = prompt.find('# 今日学习数据')
            data_end = prompt.find('# 生成要求')
            
            if data_start != -1 and data_end != -1:
                learning_data = prompt[data_start:data_end]
            else:
                learning_data = prompt[:1000]  # 如果找不到标记，取前1000字符
            
            # 创建精简的prompt，确保不会太长
            short_prompt = f"""请为ZZW生成一份温暖鼓励的考公学习日报。

{learning_data}

报告要求：
1. 用温暖友好的语气，像朋友一样亲切
2. 详细分析今日积分（解释每项积分的意义）
3. 找出学习亮点并给予肯定
4. 提供1-2个具体可行的改进建议
5. 结尾用充满正能量的鼓励话语

格式要求：
- 使用Markdown格式
- 多用emoji让报告生动有趣
- 包含"今日表现"、"积分分析"、"明日建议"、"温馨寄语"等部分

请生成完整的学习总结报告。"""
            
            # 使用-p参数直接调用gemini-cli
            result = subprocess.run(
                ['gemini', '-p', short_prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=150
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            else:
                # 如果失败了，再尝试一次更短的版本
                print("⚠️ 第一次尝试失败，使用更精简的prompt...")
                
                mini_prompt = f"""为ZZW生成今日考公学习总结报告。

今日数据：{learning_data[:500]}...

要求：温暖鼓励、分析积分、提出建议、使用emoji和Markdown格式。"""
                
                result2 = subprocess.run(
                    ['gemini', '-p', mini_prompt],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=60
                )
                
                if result2.returncode == 0 and result2.stdout.strip():
                    return result2.stdout
                
                # 两种方式都失败了
                print(f"⚠️ Gemini-cli返回错误代码: {result.returncode}")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                return self._generate_fallback_report(prompt)
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ Gemini-cli处理超时")
            return self._generate_fallback_report(prompt)
        except Exception as e:
            print(f"调用gemini-cli失败: {e}")
            return self._generate_fallback_report(prompt)
    
    def _generate_fallback_report(self, prompt: str) -> str:
        # 备用报告模板（增强版）
        return """# 📚 每日学习总结报告

## 🌟 今日表现

亲爱的ZZW，今天又是充实的一天！让我们一起回顾今天的学习历程。

### 📊 学习数据总览
今天你坚持完成了学习任务，这本身就是一个值得庆祝的成就！每一天的积累都在为你的成功打下坚实基础。

### 🎯 积分分析
根据你今天的学习记录：

**获得积分项目**：
- ✅ 每日签到奖励：恭喜你保持了学习的连续性！
- 📚 学习时长积分：坚持就是胜利，每一分钟的学习都有价值
- ✏️ 练习题完成：实践是检验真理的唯一标准
- 💤 生活习惯加分：良好的作息是高效学习的保障

**需要关注的地方**：
- 如果有扣分项，请记住这只是提醒你需要调整的信号
- 每个人都有状态不佳的时候，重要的是及时调整

### 💪 今日亮点
1. **坚持的力量**：无论今天学习了多长时间，你都在坚持，这种毅力值得赞赏！
2. **进步的轨迹**：每一道题、每一页笔记都是你进步的见证
3. **自律的品质**：能够坚持学习计划，说明你具备了成功的关键品质

### 🎯 明日优化建议
基于今天的表现，明天可以考虑：
1. **时间管理**：如果今天学习时间较短，明天可以尝试增加30分钟
2. **练习强化**：适当增加练习题数量，巩固知识点
3. **作息调整**：保证充足睡眠，让大脑得到充分休息
4. **心态调节**：保持积极乐观，相信自己的能力

### 📈 积分提升小贴士
- 学习180分钟以上可获得更高积分奖励
- 完成50道以上练习题有额外加分
- 保持7天连续学习可获得完美周奖励
- 注意劳逸结合，避免疲劳作战导致扣分

## 💝 温馨寄语

考公之路确实充满挑战，但请记住：
- 你不是一个人在战斗，有系统陪伴你的每一天
- 今天的努力，是明天成功的基石
- 保持节奏，稳步前进，终将到达目标

> "志之所趋，无远弗届；志之所向，无坚不摧。"

相信自己，你一定能够实现梦想！明天继续加油！🌈

---
*Generated with ❤️ for ZZW - 考公路上的忠实伙伴*"""
    
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