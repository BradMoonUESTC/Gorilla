"""
自动修复器 - 使用LLM自动修复测试错误
"""

import os
import sys
from typing import Tuple

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common


class AutoFixer:
    """自动测试修复器"""
    
    def __init__(self, max_attempts: int = 3, project_path: str = None):
        self.max_attempts = max_attempts
        self.project_path = project_path
    
    def fix_test_code(self, test_code: str, error_output: str, original_description: str) -> Tuple[str, bool]:
        """自动修复测试代码"""
        
        current_code = test_code
        
        for attempt in range(self.max_attempts):
            print(f"🔧 尝试修复测试代码 (第{attempt + 1}/{self.max_attempts}次)")
            
            fixed_code = self._generate_fix(current_code, error_output, original_description, attempt)
            
            if fixed_code and fixed_code != current_code:
                current_code = fixed_code
                print(f"✅ 生成修复版本 {attempt + 1}")
                return current_code, True
            else:
                print(f"❌ 修复尝试 {attempt + 1} 失败")
        
        print("❌ 达到最大修复尝试次数，修复失败")
        return current_code, False
    
    def _generate_fix(self, test_code: str, error_output: str, original_description: str, attempt: int) -> str:
        """使用LLM生成修复代码"""
        
        # 获取项目上下文信息
        context_info = self._get_project_context()
        error_analysis = self.analyze_error_type(error_output)
        
        prompt = f"""
你是一个Solidity测试代码修复专家。以下测试代码执行时出现了错误，请修复它。

=== 项目上下文信息 ===
{context_info}

=== 测试需求 ===
{original_description}

=== 当前测试代码 ===
```solidity
{test_code}
```

=== 错误信息 ===
错误类型: {error_analysis}
详细输出:
```
{error_output}
```

=== 修复指导 ===
修复尝试次数: {attempt + 1}/{self.max_attempts}

根据错误类型，请重点关注:
{self._get_fix_guidance(error_analysis)}

=== 修复要求 ===
1. 仔细分析错误原因，特别是合约构造函数参数
2. 确保所有导入语句正确
3. 验证合约实例化的参数类型和顺序
4. 保持测试逻辑的完整性
5. 使用正确的Solidity语法

请直接返回修复后的完整Solidity代码，不要包含任何解释文字。
"""
        
        try:
            print("🔧 发送给修复LLM的prompt:")
            print("-" * 40)
            print(prompt)
            print("-" * 40)
            
            response = ask_openai_common(prompt)
            
            print("🔧 修复LLM返回结果:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            # 提取Solidity代码
            if "```solidity" in response:
                start = response.find("```solidity") + len("```solidity")
                end = response.find("```", start)
                if end != -1:
                    return response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    return response[start:end].strip()
            
            # 如果没有代码块标记，返回整个响应
            return response.strip()
            
        except Exception as e:
            print(f"LLM修复调用失败: {e}")
            return ""
    
    def analyze_error_type(self, error_output: str) -> str:
        """分析错误类型"""
        error_output_lower = error_output.lower()
        
        if "compilation failed" in error_output_lower or "solc" in error_output_lower:
            return "compilation_error"
        elif "revert" in error_output_lower or "panic" in error_output_lower:
            return "runtime_error"  
        elif "assertion failed" in error_output_lower or "assert" in error_output_lower:
            return "assertion_error"
        elif "not found" in error_output_lower or "missing" in error_output_lower:
            return "dependency_error"
        else:
            return "unknown_error"
    
    def _get_project_context(self) -> str:
        """获取项目上下文信息"""
        if not self.project_path:
            return "项目路径未提供"
        
        from pathlib import Path
        context = []
        
        # 读取SimpleERC20合约信息
        erc20_path = Path(self.project_path) / "src" / "SimpleERC20.sol"
        if erc20_path.exists():
            try:
                with open(erc20_path, 'r', encoding='utf-8') as f:
                    erc20_content = f.read()
                    
                # 提取构造函数信息
                if "constructor(" in erc20_content:
                    start = erc20_content.find("constructor(")
                    end = erc20_content.find(")", start) + 1
                    constructor_sig = erc20_content[start:end]
                    context.append(f"SimpleERC20构造函数: {constructor_sig}")
                    
                # 提取主要函数
                functions = ["transfer", "transferFrom", "approve", "mint", "burn"]
                for func in functions:
                    if f"function {func}(" in erc20_content:
                        context.append(f"- 包含{func}函数")
                        
            except Exception as e:
                context.append(f"读取SimpleERC20合约失败: {e}")
        else:
            context.append("SimpleERC20合约文件不存在")
        
        # 读取基础模板信息
        template_path = Path(self.project_path) / "test" / "GorillaBase.t.sol"
        if template_path.exists():
            context.append("基础测试模板: GorillaBase.t.sol 存在")
        else:
            context.append("基础测试模板: GorillaBase.t.sol 不存在")
        
        return "\n".join(context) if context else "无法获取项目上下文"
    
    def _get_fix_guidance(self, error_type: str) -> str:
        """根据错误类型提供修复指导"""
        guidance = {
            "compilation_error": """
- 检查合约构造函数参数的类型和顺序
- SimpleERC20构造函数需要: (string _name, string _symbol, uint8 _decimals, uint256 _totalSupply)
- 确保字符串参数用引号包围
- 确保数值参数类型正确
- 检查导入语句是否正确""",
            
            "runtime_error": """
- 检查合约状态和余额
- 验证函数调用的前置条件
- 确保用户有足够的代币余额
- 检查授权(allowance)设置""",
            
            "assertion_error": """
- 检查断言的预期值是否正确
- 验证测试逻辑是否符合预期
- 确保余额计算正确""",
            
            "dependency_error": """
- 检查导入路径是否正确
- 确保所有依赖的合约文件存在
- 验证forge-std导入""",
            
            "unknown_error": """
- 仔细阅读错误信息
- 检查语法错误
- 验证合约实例化过程
- 确保所有变量正确初始化"""
        }
        
        return guidance.get(error_type, guidance["unknown_error"])
