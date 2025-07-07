import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, List
from .intelligent_answer_processor import IntelligentAnswerProcessor


class ExcelHandler:
    def __init__(self):
        self.questionnaire_dir = "questionnaires"
        os.makedirs(self.questionnaire_dir, exist_ok=True)
        self.intelligent_processor = IntelligentAnswerProcessor()
    
    def export_questionnaire(self, questions: List[Dict]) -> str:
        """导出问卷到Excel文件"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_questionnaire_{today}.xlsx"
        filepath = os.path.join(self.questionnaire_dir, filename)
        
        # 准备导出数据
        export_data = []
        
        for i, question in enumerate(questions):
            if question["type"] == "auto":
                # 自动填充的问题
                export_data.append({
                    "序号": i + 1,
                    "问题": question["question"],
                    "答案类型": "自动填充",
                    "选项": "",
                    "答案": question["value"]
                })
            elif question["type"] == "choice":
                # 选择题
                options_str = "\n".join([f"{j}. {opt}" for j, opt in enumerate(question["options"])])
                export_data.append({
                    "序号": i + 1,
                    "问题": question["question"],
                    "答案类型": "选择题",
                    "选项": options_str,
                    "答案": ""  # 待填写
                })
            elif question["type"] == "text":
                # 文本题
                export_data.append({
                    "序号": i + 1,
                    "问题": question["question"],
                    "答案类型": "文本",
                    "选项": question.get("placeholder", ""),
                    "答案": ""  # 待填写
                })
        
        # 创建DataFrame
        df = pd.DataFrame(export_data)
        
        # 导出到Excel，设置格式
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='每日问卷', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['每日问卷']
            
            # 设置列宽
            worksheet.column_dimensions['A'].width = 8   # 序号
            worksheet.column_dimensions['B'].width = 40  # 问题
            worksheet.column_dimensions['C'].width = 12  # 答案类型
            worksheet.column_dimensions['D'].width = 50  # 选项
            worksheet.column_dimensions['E'].width = 30  # 答案
            
            # 设置行高（选项较多的行）
            for row in range(2, len(export_data) + 2):
                if "\n" in str(df.iloc[row-2]['选项']):
                    worksheet.row_dimensions[row].height = 100
        
        # 创建答题说明文件
        instructions = self._create_instructions()
        instructions_path = os.path.join(self.questionnaire_dir, f"填写说明_{today}.txt")
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        return filepath
    
    def _create_instructions(self) -> str:
        return """ZZW考公学习日记 - 每日问卷填写说明

📝 填写说明：

1. 选择题填写方式：
   - 请在"答案"列填写选项编号（0, 1, 2等）
   - 例如：如果选择"1. 📝 部分完成"，请填写数字 1

2. 文本题填写方式：
   - 直接在"答案"列填写文字内容
   - 可以写详细一些，没有字数限制

3. 自动填充题：
   - 这些题目已经自动填好，无需修改

4. 填写示例：
   问题：今天学习了多长时间？
   选项：
   0. 🚫 没有学习
   1. ⏱️ 30分钟以下
   2. ⏱️ 30-60分钟
   答案：2  （表示选择了30-60分钟）

5. 保存文件：
   - 填写完成后，请保存文件
   - 文件名不要修改，保持原名称

祝学习顺利！💪
"""
    
    def import_answers(self, filepath: str, questions: List[Dict]) -> Dict:
        """从Excel文件导入答案"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文件: {filepath}")
        
        # 读取Excel文件
        df = pd.read_excel(filepath, sheet_name='每日问卷')
        
        # 提取问卷的原始日期（从文件名或Excel内容中）
        questionnaire_date = self._extract_questionnaire_date(filepath, df)
        print(f"📅 问卷原始日期: {questionnaire_date}")
        
        # 提取答案
        responses = {}
        
        for i, row in df.iterrows():
            # 跳过自动填充的问题
            if row['答案类型'] == '自动填充':
                # 对于日期问题，使用问卷的原始日期而不是当前日期
                if row['问题'] == '今天的日期':
                    responses['date'] = questionnaire_date
                continue
            
            # 找到对应的问题
            question = None
            for q in questions:
                if q['question'] == row['问题']:
                    question = q
                    break
            
            if not question:
                continue
            
            answer = row['答案']
            
            # 处理不同类型的答案
            if question['type'] == 'choice':
                # 保存原始答案，后续使用智能处理
                responses[question['id']] = answer
            
            elif question['type'] == 'text':
                # 文本答案
                if pd.notna(answer) and str(answer).strip():
                    responses[question['id']] = str(answer).strip()
        
        # 确保日期字段被正确设置
        if 'date' not in responses:
            responses['date'] = questionnaire_date
        
        # 使用智能处理器处理所有答案
        processed_responses, warnings = self.intelligent_processor.batch_process_answers(
            responses, questions
        )
        
        # 打印警告信息
        if warnings:
            print("\n📋 智能答案识别结果:")
            print("-" * 50)
            for warning in warnings:
                print(f"  • {warning}")
            print("-" * 50)
        
        # 检查是否有用户反馈
        user_feedback = self.intelligent_processor.get_user_feedback()
        if user_feedback:
            print("\n💡 用户反馈（问题修改建议）:")
            print("-" * 50)
            for feedback in user_feedback:
                print(f"  📝 {feedback['question']}")
                print(f"     {feedback['feedback']}")
            print("-" * 50)
            
            # 保存反馈到文件
            feedback_file = os.path.join(self.questionnaire_dir, "user_feedback.json")
            existing_feedback = []
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    existing_feedback = json.load(f)
            
            # 添加时间戳
            for fb in user_feedback:
                fb['timestamp'] = datetime.now().isoformat()
            
            existing_feedback.extend(user_feedback)
            
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(existing_feedback, f, ensure_ascii=False, indent=2)
            
            print("\n是否要根据这些反馈修改问卷问题？")
            print("（反馈已保存到 questionnaires/user_feedback.json）")
            
            # 清空反馈
            self.intelligent_processor.clear_feedback()
        
        return processed_responses
    
    def validate_excel_file(self, filepath: str) -> bool:
        """验证Excel文件格式是否正确"""
        try:
            df = pd.read_excel(filepath, sheet_name='每日问卷')
            required_columns = ['序号', '问题', '答案类型', '选项', '答案']
            
            # 检查必需的列
            for col in required_columns:
                if col not in df.columns:
                    print(f"错误：缺少必需的列 '{col}'")
                    return False
            
            # 检查是否有答案
            answered_count = df[df['答案类型'] != '自动填充']['答案'].notna().sum()
            if answered_count == 0:
                print("警告：没有找到任何已填写的答案")
                return False
            
            return True
            
        except Exception as e:
            print(f"读取Excel文件时出错: {e}")
            return False
    
    def get_latest_questionnaire(self) -> str:
        """获取最新的问卷文件路径"""
        files = [f for f in os.listdir(self.questionnaire_dir) 
                if f.startswith('daily_questionnaire_') and f.endswith('.xlsx')]
        
        if not files:
            return None
        
        # 按日期排序，获取最新的
        files.sort(reverse=True)
        return os.path.join(self.questionnaire_dir, files[0])
    
    def get_answered_questionnaires(self) -> List[str]:
        """获取所有已回答的问卷文件"""
        answered_dir = os.path.join(self.questionnaire_dir, "answered")
        if not os.path.exists(answered_dir):
            return []
        
        files = [f for f in os.listdir(answered_dir) 
                if f.startswith('daily_questionnaire_') and f.endswith('.xlsx')]
        
        return [os.path.join(answered_dir, f) for f in sorted(files, reverse=True)]
    
    def _extract_questionnaire_date(self, filepath: str, df: pd.DataFrame) -> str:
        """提取问卷的原始日期"""
        # 方法1：从文件名提取日期
        filename = os.path.basename(filepath)
        # 文件名格式：daily_questionnaire_YYYY-MM-DD.xlsx
        import re
        date_match = re.search(r'daily_questionnaire_(\d{4}-\d{2}-\d{2})\.xlsx', filename)
        if date_match:
            return date_match.group(1)
        
        # 方法2：从Excel内容中的日期字段提取
        for i, row in df.iterrows():
            if row['问题'] == '今天的日期' and row['答案类型'] == '自动填充':
                date_value = row['答案']
                if pd.notna(date_value):
                    # 处理可能的日期格式
                    date_str = str(date_value)
                    # 如果是标准格式 YYYY-MM-DD，直接返回
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        return date_str
                    # 如果是其他日期格式，尝试解析
                    try:
                        from datetime import datetime
                        parsed_date = pd.to_datetime(date_str)
                        return parsed_date.strftime("%Y-%m-%d")
                    except:
                        pass
        
        # 方法3：如果都失败了，使用当前日期（回退方案）
        return datetime.now().strftime("%Y-%m-%d")