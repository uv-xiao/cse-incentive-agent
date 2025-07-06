import pandas as pd
import os
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
        
        # 提取答案
        responses = {}
        
        for i, row in df.iterrows():
            # 跳过自动填充的问题
            if row['答案类型'] == '自动填充':
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