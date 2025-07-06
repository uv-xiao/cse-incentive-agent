import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple


class IntelligentAnswerProcessor:
    """使用gemini-cli智能处理自然语言答案"""
    
    def __init__(self):
        self.gemini_available = self._check_gemini_available()
    
    def _check_gemini_available(self) -> bool:
        """检查gemini-cli是否可用"""
        try:
            result = subprocess.run(['gemini', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def process_natural_language_answer(self, 
                                      answer: str, 
                                      question: str, 
                                      options: List[str]) -> Optional[int]:
        """
        使用AI处理自然语言答案，返回最匹配的选项索引
        
        Args:
            answer: 用户输入的自然语言答案
            question: 问题文本
            options: 选项列表
            
        Returns:
            匹配的选项索引，如果无法匹配返回None
        """
        if not self.gemini_available:
            return self._fallback_processing(answer, options)
        
        # 构建prompt
        options_text = "\n".join([f"{i}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""你是一个智能答案处理助手。用户在回答选择题时输入了自然语言而不是选项编号。

问题：{question}

可选选项：
{options_text}

用户的回答：{answer}

请分析用户的回答，判断最符合哪个选项。考虑以下因素：
1. 语义相似度
2. 用户的真实意图
3. 如果用户说"不要扣分"、"0分钟"、"没有"等，通常表示选择第一个选项（编号0）
4. 如果答案包含具体数字，匹配包含该数字范围的选项

只返回一个数字（选项编号），不要有其他任何文字。如果无法确定，返回-1。
"""
        
        try:
            # 使用gemini-cli处理
            result = subprocess.run(
                ['gemini', prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # 提取数字
                match = re.search(r'^(-?\d+)$', response)
                if match:
                    index = int(match.group(1))
                    if 0 <= index < len(options):
                        return index
                    elif index == -1:
                        return None
            
        except Exception as e:
            print(f"AI处理出错: {e}")
        
        # 如果AI处理失败，使用回退方案
        return self._fallback_processing(answer, options)
    
    def _fallback_processing(self, answer: str, options: List[str]) -> Optional[int]:
        """
        回退处理方案：使用简单的关键词匹配
        """
        answer_lower = answer.lower()
        
        # 特殊处理：如果答案包含"0"或"没有"或"不"，通常选择第一个选项
        if any(keyword in answer_lower for keyword in ['0', '没有', '不', '无', 'no']):
            return 0
        
        # 尝试提取数字
        numbers = re.findall(r'\d+', answer)
        if numbers:
            # 如果有数字，尝试匹配包含该数字的选项
            main_number = int(numbers[0])
            for i, option in enumerate(options):
                option_numbers = re.findall(r'\d+', option)
                for opt_num in option_numbers:
                    if int(opt_num) == main_number:
                        return i
                    # 检查数字范围
                    if '-' in option:
                        range_match = re.search(r'(\d+)-(\d+)', option)
                        if range_match:
                            start, end = int(range_match.group(1)), int(range_match.group(2))
                            if start <= main_number <= end:
                                return i
        
        # 关键词匹配
        max_score = 0
        best_match = None
        
        for i, option in enumerate(options):
            score = 0
            option_lower = option.lower()
            
            # 计算共同词汇
            answer_words = set(answer_lower.split())
            option_words = set(option_lower.split())
            common_words = answer_words & option_words
            score += len(common_words)
            
            # 检查包含关系
            if answer_lower in option_lower or option_lower in answer_lower:
                score += 5
            
            if score > max_score:
                max_score = score
                best_match = i
        
        return best_match if max_score > 0 else None
    
    def batch_process_answers(self, 
                            responses: Dict,
                            questions: List[Dict]) -> Tuple[Dict, List[str]]:
        """
        批量处理答案，返回处理后的响应和警告信息
        
        Args:
            responses: 原始响应字典
            questions: 问题列表
            
        Returns:
            (处理后的响应, 警告信息列表)
        """
        processed_responses = responses.copy()
        warnings = []
        
        for question in questions:
            if question['type'] != 'choice':
                continue
                
            qid = question['id']
            if qid not in responses:
                continue
                
            answer = responses[qid]
            
            # 如果已经是有效的数字索引，跳过
            if isinstance(answer, int) and 0 <= answer < len(question['options']):
                continue
            
            # 尝试转换为整数
            try:
                answer_int = int(answer)
                if 0 <= answer_int < len(question['options']):
                    processed_responses[qid] = answer_int
                    continue
            except (ValueError, TypeError):
                pass
            
            # 使用智能处理
            result = self.process_natural_language_answer(
                str(answer),
                question['question'],
                question['options']
            )
            
            if result is not None:
                processed_responses[qid] = result
                warnings.append(
                    f"已智能识别：问题'{question['question']}'的答案'{answer}' "
                    f"→ 选项{result}: {question['options'][result]}"
                )
            else:
                # 无法识别，尝试选择最保守的选项（通常是第一个）
                processed_responses[qid] = 0
                warnings.append(
                    f"无法识别答案'{answer}'，已默认选择: "
                    f"{question['options'][0]}"
                )
        
        return processed_responses, warnings