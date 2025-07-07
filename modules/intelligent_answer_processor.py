import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple


class IntelligentAnswerProcessor:
    """使用gemini-cli智能处理自然语言答案"""
    
    def __init__(self):
        self.gemini_available = self._check_gemini_available()
        self.user_feedback = []  # 收集用户反馈
        self.gemini_warnings = []  # 收集gemini相关的警告
    
    def _check_gemini_available(self) -> bool:
        """检查gemini-cli是否可用"""
        try:
            result = subprocess.run(['gemini', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _extract_option_number(self, answer: str) -> Optional[int]:
        """
        优先提取答案中的选项编号
        例如："2 有的时候..." -> 2
        """
        # 检查答案开头是否有数字
        match = re.match(r'^(\d+)', answer.strip())
        if match:
            return int(match.group(1))
        
        # 检查答案中是否包含"选项X"或"第X个"等模式
        patterns = [
            r'选项\s*(\d+)',
            r'第\s*(\d+)\s*个',
            r'选\s*(\d+)',
            r'答案\s*[:：]?\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, answer)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_quantity_from_answer(self, answer: str) -> Optional[int]:
        """
        从答案中提取数量信息
        例如："10个小时" -> 600 (分钟)
             "50题" -> 50
             "5000字" -> 5000
        """
        answer_lower = answer.lower()
        
        # 时间相关的提取（转换为分钟）
        time_patterns = [
            (r'(\d+\.?\d*)\s*个?\s*小时', lambda x: int(float(x) * 60)),
            (r'(\d+)\s*分钟', lambda x: int(x)),
            (r'(\d+)h', lambda x: int(x) * 60),
            (r'(\d+)min', lambda x: int(x)),
        ]
        
        for pattern, converter in time_patterns:
            match = re.search(pattern, answer_lower)
            if match:
                return converter(match.group(1))
        
        # 通用数字提取
        # 匹配各种格式：50题、50道、5000字、5000+
        number_patterns = [
            r'(\d+)\s*[题道个字]',
            r'(\d+)\+?',
            r'有\s*(\d+)',
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, answer)
            if match:
                return int(match.group(1))
        
        return None
    
    def _check_user_reason(self, answer: str) -> Optional[str]:
        """
        检查用户是否提供了不需要做某事的理由
        返回理由描述，如果没有则返回None
        """
        reason_keywords = [
            '已经', '完成了', '不需要', '暂时不', '最近不', 
            '之前有', '用之前的', '看完了', '一遍了'
        ]
        
        for keyword in reason_keywords:
            if keyword in answer:
                return f"用户说明：{answer}"
        
        return None
    
    def process_natural_language_answer(self, 
                                      answer: str, 
                                      question: str, 
                                      options: List[str]) -> Tuple[Optional[int], Optional[str]]:
        """
        使用AI处理自然语言答案，返回最匹配的选项索引和反馈信息
        
        Returns:
            (选项索引, 用户反馈/理由)
        """
        # 1. 优先检查是否直接包含选项编号
        option_num = self._extract_option_number(answer)
        
        # 2. 检查是否有不需要的理由（即使有选项编号也要检查）
        reason = self._check_user_reason(answer)
        
        # 如果找到了选项编号且有效，直接返回（但带上理由）
        if option_num is not None and 0 <= option_num < len(options):
            return option_num, reason
        
        # 3. 提取数量信息进行匹配
        quantity = self._extract_quantity_from_answer(answer)
        
        # 特殊检查：如果提取到了正数，确保不会返回"没有"选项
        if quantity and quantity > 0:
            # 检查第一个选项是否是"没有"相关
            first_option_lower = options[0].lower() if options else ""
            if any(neg in first_option_lower for neg in ['没有', '不', '🚫', '无']):
                # 直接使用增强的回退处理，避免返回"没有"
                return self._enhanced_fallback_processing(answer, options, quantity), reason
        
        # 4. 如果没有gemini，使用增强的回退处理
        if not self.gemini_available:
            return self._enhanced_fallback_processing(answer, options, quantity), reason
        
        # 5. 使用gemini进行智能处理
        options_text = "\n".join([f"{i}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""你是一个智能答案处理助手。请根据用户的回答，选择最合适的选项。

问题：{question}

可选选项：
{options_text}

用户的回答：{answer}

重要规则：
1. 如果答案开头就是数字（如"2 有时候..."），直接返回该数字
2. 如果答案包含具体数量（如"10个小时"、"50题"），找包含该数量范围的选项
3. 对于时间，需要转换单位：10个小时 = 600分钟
4. 如果用户说"已经完成"、"不需要"等，但有合理理由，仍选择对应的"没有"选项
5. 注意数字的上下文，"5000字以上"应该匹配"5000+"的选项，而不是"没有"

特别注意：
- "10个小时"绝对不是"没有学习"！应该匹配600分钟对应的选项
- "50题"绝对不是"没有做题"！应该匹配包含50题的选项
- 任何包含正数的答案都不应该被识别为"没有"或"0"选项

请分析后只返回一个数字（选项编号），不要有其他文字。如果无法确定，返回-1。
"""
        
        try:
            result = subprocess.run(
                ['gemini', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=30  # 放宽到30秒
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # 尝试从响应中提取数字（可能在文本中）
                numbers = re.findall(r'-?\d+', response)
                if numbers:
                    # 取第一个数字
                    index = int(numbers[0])
                    if 0 <= index < len(options):
                        return index, reason
                    elif index == -1:
                        # gemini无法确定，使用回退方案
                        fallback_result = self._enhanced_fallback_processing(answer, options, quantity)
                        self.gemini_warnings.append(
                            f"⚠️ Gemini无法确定答案'{answer}'的最佳选项，使用回退方案"
                        )
                        return fallback_result, reason
                    else:
                        # 数字超出范围
                        self.gemini_warnings.append(
                            f"⚠️ Gemini返回的选项编号{index}超出范围(0-{len(options)-1})"
                        )
                else:
                    # gemini返回了非预期格式
                    self.gemini_warnings.append(
                        f"⚠️ Gemini返回了非预期格式：{response[:50]}..."
                    )
            else:
                # gemini命令执行失败
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                self.gemini_warnings.append(
                    f"⚠️ Gemini处理失败：{error_msg}"
                )
            
        except subprocess.TimeoutExpired:
            self.gemini_warnings.append(
                f"⚠️ Gemini处理超时（超过30秒），使用回退方案"
            )
        except Exception as e:
            self.gemini_warnings.append(
                f"⚠️ Gemini处理出错：{str(e)}"
            )
        
        # 如果AI处理失败，使用增强的回退方案
        return self._enhanced_fallback_processing(answer, options, quantity), reason
    
    def _enhanced_fallback_processing(self, answer: str, options: List[str], 
                                    quantity: Optional[int] = None) -> Optional[int]:
        """
        增强的回退处理方案
        """
        answer_lower = answer.lower()
        
        # 如果有提取到的数量，优先使用数量匹配
        if quantity is not None and quantity > 0:
            # 先尝试找最接近的匹配
            best_match = None
            best_threshold = 0
            
            for i, option in enumerate(options):
                option_lower = option.lower()
                
                # 跳过"没有"选项
                if i == 0 and ('没有' in option or '🚫' in option):
                    continue
                
                # 检查精确数字
                if str(quantity) in option:
                    return i
                
                # 检查范围
                range_patterns = [
                    r'(\d+)-(\d+)',
                    r'(\d+)～(\d+)',
                    r'(\d+)~(\d+)',
                    r'(\d+)到(\d+)',
                    r'(\d+)至(\d+)'
                ]
                
                for pattern in range_patterns:
                    match = re.search(pattern, option)
                    if match:
                        start, end = int(match.group(1)), int(match.group(2))
                        if start <= quantity <= end:
                            return i
                
                # 检查"X以上"或"X+"的模式
                above_patterns = [
                    r'(\d+)\+',
                    r'(\d+)[^0-9]*以上',  # 允许数字和"以上"之间有其他字符
                    r'(\d+)[^0-9]*及以上',
                    r'超过[^0-9]*(\d+)',
                    r'大于[^0-9]*(\d+)'
                ]
                
                for pattern in above_patterns:
                    match = re.search(pattern, option)
                    if match:
                        threshold = int(match.group(1))
                        if quantity >= threshold and threshold > best_threshold:
                            best_match = i
                            best_threshold = threshold
            
            # 如果找到了合适的匹配，返回最佳匹配
            if best_match is not None:
                return best_match
        
        # 关键词匹配 - 根据上下文智能判断
        # 对于"没有"的判断要更谨慎
        if '没有' in answer_lower or '不' in answer_lower:
            # 但如果后面有具体数字或说明，可能不是真的"没有"
            if not any(char.isdigit() for char in answer):
                # 确实没有数字，可能真的是"没有"
                for i, option in enumerate(options):
                    if '没有' in option or '不' in option or '🚫' in option:
                        return i
        
        # 如果答案中有任何正数，绝不应该返回第一个选项（通常是"没有"）
        if any(char.isdigit() for char in answer) and quantity and quantity > 0:
            # 跳过第一个选项（通常是"没有"），从第二个开始寻找最佳匹配
            start_index = 1 if len(options) > 1 else 0
        else:
            start_index = 0
        
        # 寻找最佳匹配
        best_score = 0
        best_match = None
        
        for i, option in enumerate(options):
            # 如果有数字且start_index > 0，跳过第一个选项
            if i < start_index:
                continue
                
            score = 0
            option_lower = option.lower()
            
            # 计算共同关键词
            answer_words = set(re.findall(r'\w+', answer_lower))
            option_words = set(re.findall(r'\w+', option_lower))
            common_words = answer_words & option_words
            score += len(common_words) * 2
            
            # 完全包含关系加分
            if answer_lower in option_lower:
                score += 10
            
            # 部分匹配
            for word in answer_words:
                if len(word) > 2 and word in option_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = i
        
        # 如果有数字但没找到匹配，返回第二个选项而不是第一个
        if best_match is None and start_index > 0:
            return start_index
        
        return best_match if best_score > 2 else start_index
    
    def batch_process_answers(self, 
                            responses: Dict,
                            questions: List[Dict]) -> Tuple[Dict, List[str]]:
        """
        批量处理答案，返回处理后的响应和警告信息
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
            
            # 尝试转换为整数（但仍需要检查是否有额外说明）
            try:
                # 如果答案是纯数字（没有其他文字），才直接使用
                answer_str = str(answer).strip()
                if answer_str.isdigit():
                    answer_int = int(answer_str)
                    if 0 <= answer_int < len(question['options']):
                        processed_responses[qid] = answer_int
                        continue
            except (ValueError, TypeError):
                pass
            
            # 使用智能处理
            result, reason = self.process_natural_language_answer(
                str(answer),
                question['question'],
                question['options']
            )
            
            if result is not None:
                processed_responses[qid] = result
                msg = f"已智能识别：问题'{question['question']}'的答案'{answer}' → 选项{result}: {question['options'][result]}"
                if reason:
                    msg += f" ({reason})"
                    self.user_feedback.append({
                        'question': question['question'],
                        'feedback': reason,
                        'original_answer': answer
                    })
                warnings.append(msg)
            else:
                # 无法识别，选择最保守的选项
                processed_responses[qid] = 0
                warnings.append(
                    f"无法识别答案'{answer}'，已默认选择: {question['options'][0]}"
                )
        
        # 添加gemini警告到总警告列表
        if self.gemini_warnings:
            warnings.extend(self.gemini_warnings)
        
        return processed_responses, warnings
    
    def get_user_feedback(self) -> List[Dict]:
        """获取收集到的用户反馈"""
        return self.user_feedback
    
    def clear_feedback(self):
        """清空用户反馈和警告"""
        self.user_feedback = []
        self.gemini_warnings = []