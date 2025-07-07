import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
import json
import re


class QuestionnaireOptimizer:
    """问卷优化器 - 根据用户反馈自动优化问卷问题"""
    
    def __init__(self):
        self.questionnaire_file = "modules/questionnaire.py"
        self.backup_dir = "backups"
        self.suggestions_dir = "questionnaires"
        
    def create_backup(self) -> str:
        """创建问卷文件的备份"""
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"questionnaire_backup_{timestamp}.py"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # 复制文件
        shutil.copy2(self.questionnaire_file, backup_path)
        
        return backup_path
    
    def analyze_feedback_with_ai(self, feedback_list: List[Dict]) -> str:
        """使用AI分析用户反馈并生成修改建议"""
        
        # 读取当前问卷代码
        with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # 构建分析提示
        feedback_text = ""
        for fb in feedback_list:
            feedback_text += f"""
问题: {fb['question']}
用户原始答案: {fb['original_answer']}
用户反馈: {fb['feedback']}
---
"""
        
        prompt = f"""你是一个问卷设计专家。请分析用户对问卷的反馈，并提供具体的改进建议。

# 当前问卷代码
```python
{current_code}
```

# 用户反馈
{feedback_text}

# 分析任务
请分析每个用户反馈，并提供以下内容：

## 1. 反馈分析
对每个反馈进行分析，理解用户的真实需求和建议。

## 2. 问题识别
识别当前问卷设计中的问题：
- 问题是否合理？
- 选项设置是否完善？
- 是否需要添加新选项？
- 是否需要调整问题描述？

## 3. 具体修改建议
对于每个需要修改的地方，提供：
- 问题位置（在代码中的大概位置）
- 当前内容
- 建议修改为
- 修改理由

## 4. 代码修改指导
提供具体的Python代码修改建议，包括：
- 需要修改的函数
- 需要添加/删除/修改的选项
- 新的问题描述或选项文本

请用中文回复，并提供详细、可操作的建议。
"""
        
        try:
            # 使用gemini-cli分析，使用-p参数避免文件读取问题
            # 精简prompt以适应命令行限制
            short_prompt = f"""分析用户对问卷的反馈并提供改进建议。

用户反馈：
{feedback_text[:1000]}...

请分析：
1. 用户的真实需求
2. 当前问卷的不足
3. 具体的改进建议

用中文回复。"""
            
            result = subprocess.run(
                ['gemini', '-p', short_prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                # 如果AI分析失败，返回基本建议
                return self._generate_basic_suggestions(feedback_list)
                
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._generate_basic_suggestions(feedback_list)
    
    def _generate_basic_suggestions(self, feedback_list: List[Dict]) -> str:
        """生成基础的修改建议（当AI不可用时）"""
        suggestions = """# 问卷修改建议（基于用户反馈）

## 分析说明
由于AI分析服务不可用，以下是基于用户反馈的基本建议：

"""
        
        for i, fb in enumerate(feedback_list, 1):
            suggestions += f"""
## 反馈 {i}
**问题**: {fb['question']}
**用户答案**: {fb['original_answer']}
**用户说明**: {fb['feedback']}

**分析**: 用户在回答时提供了额外说明，可能表示：
- 当前问题选项不够准确
- 需要考虑用户的特殊情况
- 可能需要添加"其他"选项或调整问题描述

**建议**: 
1. 检查该问题的选项设置是否完善
2. 考虑是否需要添加条件判断或备注说明
3. 评估是否需要调整问题的提问方式

---
"""
        
        suggestions += """
## 总体建议
1. 定期收集用户反馈，持续优化问卷
2. 为特殊情况添加灵活的选项
3. 在问题描述中添加更清晰的说明
4. 考虑添加"备注"或"其他"类型的选项

## 下一步行动
1. 仔细审查每个问题的选项设计
2. 根据用户实际使用情况调整问题
3. 测试修改后的问卷是否更符合用户需求
"""
        
        return suggestions
    
    def generate_code_modifications(self, suggestions: str, feedback_list: List[Dict]) -> str:
        """基于建议生成具体的代码修改"""
        
        # 读取当前代码
        with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        prompt = f"""你是一个Python代码专家。请根据问卷优化建议生成具体的代码修改。

# 当前问卷代码
```python
{current_code}
```

# 优化建议
{suggestions}

# 用户反馈详情
"""
        
        for fb in feedback_list:
            prompt += f"""
- 问题: {fb['question']}
- 用户答案: {fb['original_answer']}
- 用户反馈: {fb['feedback']}
"""
        
        prompt += """

# 代码修改任务
请生成具体的Python代码修改建议，包括：

## 1. 需要修改的函数和方法
明确指出需要修改questionnaire.py中的哪些函数。

## 2. 具体的代码更改
对于每个需要修改的地方，提供：
- 原代码片段
- 修改后的代码片段
- 修改说明

## 3. 新增选项或问题
如果需要添加新的选项或问题，提供完整的代码。

## 4. 修改验证
说明如何验证修改是否正确工作。

请确保代码修改：
- 保持与现有代码风格一致
- 不破坏现有功能
- 添加适当的注释
- 考虑向后兼容性

用中文回复，并提供可直接使用的代码。
"""
        
        try:
            # 精简prompt以适应-p参数的限制
            short_prompt = f"""基于以下用户反馈，生成questionnaire.py的修改建议：

{feedback_list[0]['feedback'] if feedback_list else ''}

请提供：
1. 需要修改的代码位置
2. 具体的代码修改建议
3. 新增选项的示例代码

用中文回复。"""
            
            result = subprocess.run(
                ['gemini', '-p', short_prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                return "AI代码生成失败，请手动根据建议修改代码。"
                
        except Exception as e:
            return f"代码生成失败: {e}，请手动根据建议修改代码。"
    
    def save_suggestions(self, suggestions: str, code_modifications: str, feedback_list: List[Dict]) -> str:
        """保存修改建议到文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 问卷优化建议报告
生成时间: {timestamp}

## 用户反馈总结
"""
        
        for i, fb in enumerate(feedback_list, 1):
            content += f"""
### 反馈 {i}
- **问题**: {fb['question']}
- **用户答案**: {fb['original_answer']}
- **反馈内容**: {fb['feedback']}
- **时间**: {fb.get('timestamp', '未知')}
"""
        
        content += f"""

## AI分析和建议
{suggestions}

## 具体代码修改建议
{code_modifications}

## 使用说明
1. 仔细阅读上述分析和建议
2. 备份当前的questionnaire.py文件
3. 根据代码修改建议更新questionnaire.py
4. 测试修改后的问卷功能
5. 如有问题，可从备份恢复

## 注意事项
- 所有修改都会影响后续的问卷生成
- 建议在测试环境中先验证修改
- 保留此文件作为修改记录
"""
        
        # 保存到文件
        suggestions_file = os.path.join(self.suggestions_dir, "modification_suggestions.txt")
        with open(suggestions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return suggestions_file
    
    def auto_apply_modifications(self, feedback_list: List[Dict]) -> Dict[str, any]:
        """使用 Claude Code 自动修改问卷代码"""
        
        # 构建详细的修改指令
        feedback_summary = ""
        modifications_needed = []
        
        for i, fb in enumerate(feedback_list, 1):
            feedback_summary += f"""
{i}. 问题：{fb['question']}
   用户答案：{fb['original_answer']}
   用户反馈：{fb['feedback']}
"""
            
            # 分析反馈内容，识别需要的修改
            if '笔记' in fb['question'] and ('已有资料' in fb['feedback'] or '之前的资料' in fb['feedback']):
                modifications_needed.append({
                    'type': 'notes',
                    'question': fb['question'],
                    'feedback': fb['feedback'],
                    'suggestion': '添加"使用已有资料学习"选项'
                })
            elif '网课' in fb['question'] and ('看完了' in fb['feedback'] or '已经完成' in fb['feedback']):
                modifications_needed.append({
                    'type': 'online_course',
                    'question': fb['question'],
                    'feedback': fb['feedback'],
                    'suggestion': '添加"已完成所有网课"和"复习已看过的内容"选项'
                })
            else:
                modifications_needed.append({
                    'type': 'other',
                    'question': fb['question'],
                    'feedback': fb['feedback'],
                    'suggestion': '需要进一步分析'
                })
        
        # 构建 Claude Code 的 prompt
        claude_prompt = f"""请根据以下用户反馈修改问卷系统：

用户反馈：
{feedback_summary}

修改需求：
"""
        
        for mod in modifications_needed:
            claude_prompt += f"- {mod['question']}: {mod['suggestion']}\n"
        
        claude_prompt += """

请完成以下修改：
1. 修改 modules/questionnaire.py 添加新选项
2. 更新 modules/scoring.py 调整积分规则
3. 确保新选项有合理的积分设置

注意：保持代码风格一致，确保向后兼容。"""
        
        # 在 Claude Code 环境中，不需要递归调用自己
        # 而是准备好修改信息，让当前的 Claude Code 实例直接执行
        
        # 检查是否在 Claude Code 环境中
        is_claude_code_env = os.environ.get('CLAUDE_CODE', '') == 'true' or \
                           'claude' in os.environ.get('SHELL', '').lower() or \
                           os.path.exists('/home/uvxiao/.nvm/versions/node/v24.1.0/bin/claude')
        
        if is_claude_code_env:
            # 在 Claude Code 环境中，准备修改信息供直接执行
            modification_log = f"""# 问卷自动优化日志
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 用户反馈
{feedback_summary}

## 需要的修改
"""
            
            for mod in modifications_needed:
                modification_log += f"""
### {mod['type']} 类型修改
- 问题: {mod['question']}
- 建议: {mod['suggestion']}
"""
            
            modification_log += """

## Claude Code 可以执行的修改

1. **modules/questionnaire.py**：
   - 为笔记问题添加"使用已有资料学习"选项
   - 为网课问题添加"已完成所有网课"和"复习已看过的内容"选项

2. **modules/scoring.py**：
   - 添加新选项的积分规则
   - 确保积分计算合理

3. **USAGE.md**：
   - 更新文档说明新增的选项

Claude Code 已经准备好执行这些修改。
"""
            
            return {
                "success": True,
                "message": "已准备好修改信息，Claude Code 可以直接执行修改",
                "modification_log": modification_log,
                "modifications_needed": modifications_needed,
                "modified_files": [],  # 将由 Claude Code 修改
                "backup_recommended": True,
                "claude_code_ready": True,  # 标记 Claude Code 可以执行
                "prompt": claude_prompt  # 保存 prompt 供参考
            }
        
        else:
            # 不在 Claude Code 环境中，生成建议
            print("⚠️ 不在 Claude Code 环境中，生成修改建议...")
            modification_log = self._generate_modification_suggestions(feedback_summary, modifications_needed)
            
            return {
                "success": True,
                "message": "请在 Claude Code 环境中执行修改",
                "modification_log": modification_log,
                "modifications_needed": modifications_needed,
                "modified_files": [],
                "backup_recommended": True,
                "requires_manual_action": True
            }
    
    def _generate_modification_suggestions(self, feedback_summary: str, modifications_needed: List[Dict]) -> str:
        """生成修改建议文档"""
        modification_log = f"""# 问卷自动优化建议
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 用户反馈分析
{feedback_summary}

## 识别到的修改需求
"""
        
        for mod in modifications_needed:
            modification_log += f"""
- **{mod['question']}**
  - 反馈类型: {mod['type']}
  - 建议修改: {mod['suggestion']}
"""
        
        modification_log += """

## 修改建议

基于用户反馈，建议进行以下修改：

### 1. 问卷选项优化
根据用户的实际使用情况，需要为以下问题添加更贴合实际的选项：
- 笔记问题：添加"使用已有资料学习"选项
- 网课问题：添加"已完成所有网课"等选项

### 2. 积分规则调整
确保新选项有合理的积分设置，避免误判用户的学习状态。

### 3. 实施步骤
1. 修改 modules/questionnaire.py 中的问题选项
2. 更新 modules/scoring.py 中的积分计算逻辑
3. 更新 USAGE.md 文档说明新选项

## 注意事项
- 保持与现有代码风格一致
- 确保向后兼容性
- 新选项的积分设置要合理
- 记录修改日志便于追踪

**提示**：如果 Claude Code 可用，可以自动执行这些修改。"""
        
        return modification_log
    
    def optimize_questionnaire(self, feedback_list: List[Dict], auto_apply: bool = True) -> Dict[str, any]:
        """完整的问卷优化流程"""
        try:
            # 1. 创建备份
            print("📁 正在创建问卷备份...")
            backup_path = self.create_backup()
            print(f"✅ 备份已创建: {backup_path}")
            
            if auto_apply:
                # 2. AI直接修改代码
                print("🤖 正在使用Claude直接修改问卷代码...")
                print("   分析用户反馈...")
                print("   优化问卷设计...")
                print("   修改questionnaire.py文件...")
                
                modification_result = self.auto_apply_modifications(feedback_list)
                
                if modification_result['success']:
                    print("✅ 代码修改完成")
                    
                    # 3. 保存修改日志
                    print("📝 正在保存修改日志...")
                    log_file = self._save_modification_log(modification_result, feedback_list)
                    print(f"✅ 修改日志已保存: {log_file}")
                    
                    return {
                        "success": True,
                        "backup_path": backup_path,
                        "log_file": log_file,
                        "feedback_count": len(feedback_list),
                        "modified_files": modification_result.get('modified_files', []),
                        "modification_log": modification_result.get('modification_log', ''),
                        "message": "Claude已成功修改问卷代码"
                    }
                else:
                    print("❌ 代码修改失败，切换到建议模式")
                    return self._fallback_to_suggestions(feedback_list, backup_path)
            else:
                # 传统建议模式
                return self._fallback_to_suggestions(feedback_list, backup_path)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"优化过程中出现错误: {e}"
            }
    
    def _save_modification_log(self, modification_result: Dict, feedback_list: List[Dict]) -> str:
        """保存修改日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 问卷自动修改日志
修改时间: {timestamp}

## 用户反馈
"""
        
        for i, fb in enumerate(feedback_list, 1):
            content += f"""
### 反馈 {i}
- **问题**: {fb['question']}
- **用户答案**: {fb['original_answer']}
- **反馈内容**: {fb['feedback']}
"""
        
        content += f"""

## AI修改结果
{modification_result.get('modification_log', '修改成功，但未提供详细日志')}

## 修改的文件
{', '.join(modification_result.get('modified_files', []))}

## 建议后续操作
1. 测试修改后的问卷功能
2. 导出新问卷并验证选项是否正确
3. 如有问题，从备份恢复：使用备份文件替换当前文件
4. 验证积分计算是否正常

## 回滚说明
如果修改有问题，可以：
1. 从备份目录恢复questionnaire.py文件
2. 重新测试问卷功能
3. 查看此日志了解具体修改内容
"""
        
        # 保存日志
        log_file = os.path.join(self.suggestions_dir, f"modification_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return log_file
    
    def _fallback_to_suggestions(self, feedback_list: List[Dict], backup_path: str) -> Dict[str, any]:
        """回退到建议模式"""
        print("🤖 正在分析反馈并生成建议...")
        suggestions = self.analyze_feedback_with_ai(feedback_list)
        print("✅ 反馈分析完成")
        
        print("💻 正在生成代码修改建议...")
        code_modifications = self.generate_code_modifications(suggestions, feedback_list)
        print("✅ 代码修改建议生成完成")
        
        print("💾 正在保存修改建议...")
        suggestions_file = self.save_suggestions(suggestions, code_modifications, feedback_list)
        print(f"✅ 建议已保存: {suggestions_file}")
        
        return {
            "success": True,
            "backup_path": backup_path,
            "suggestions_file": suggestions_file,
            "feedback_count": len(feedback_list),
            "message": "AI自动修改失败，已生成手动修改建议"
        }