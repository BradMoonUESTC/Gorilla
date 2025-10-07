"""
动态规范生成器 - 使用LLM动态生成形式化规范和不变量
"""

import os
import sys
from typing import Dict, List, Any

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common


class DynamicSpecGenerator:
    """动态规范生成器"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def generate_formal_specs(self, contract_code: str, vulnerability_focus: str = None) -> Dict[str, Any]:
        """为给定合约动态生成形式化规范"""
        
        prompt = f"""
你是一个形式化验证专家。请为以下智能合约生成完整的形式化规范。

=== 合约代码 ===
{contract_code}

=== 任务要求 ===
请生成以下类型的形式化规范：

1. **不变量 (Invariants)** - 合约在任何时候都应该满足的条件
2. **前置条件 (Pre-conditions)** - 函数执行前必须满足的条件  
3. **后置条件 (Post-conditions)** - 函数执行后应该满足的条件
4. **安全属性 (Safety Properties)** - 合约不应该违反的安全规则

{f"特别关注: {vulnerability_focus}" if vulnerability_focus else ""}

请按以下JSON格式返回（只返回JSON，不要其他内容）：
{{
    "invariants": [
        {{
            "name": "不变量名称",
            "description": "不变量描述",
            "condition": "Solidity条件表达式",
            "check_code": "验证代码"
        }}
    ],
    "pre_conditions": [
        {{
            "function": "函数名",
            "condition": "前置条件",
            "description": "描述"
        }}
    ],
    "post_conditions": [
        {{
            "function": "函数名", 
            "condition": "后置条件",
            "description": "描述"
        }}
    ],
    "safety_properties": [
        {{
            "name": "安全属性名",
            "description": "安全属性描述",
            "violation_condition": "什么情况下违反",
            "check_code": "检测代码"
        }}
    ]
}}
"""
        
        try:
            print("🧠 LLM正在生成形式化规范...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🧠 LLM生成的形式化规范:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            # 解析JSON响应
            import json
            try:
                specs = json.loads(response)
                return specs
            except json.JSONDecodeError:
                print("⚠️ JSON解析失败，使用默认规范")
                return self._get_default_specs()
                
        except Exception as e:
            print(f"规范生成失败: {e}")
            return self._get_default_specs()
    
    def generate_vulnerability_test_logic(self, contract_code: str, vulnerability_description: str, formal_specs: Dict[str, Any]) -> Dict[str, str]:
        """基于形式化规范生成漏洞测试逻辑"""
        
        prompt = f"""
你是一个智能合约安全专家。基于以下信息生成具体的漏洞测试逻辑。

=== 合约代码 ===
{contract_code}

=== 漏洞描述 ===
{vulnerability_description}

=== 形式化规范 ===
{formal_specs}

=== 任务要求 ===
请生成具体的测试逻辑来检测这个漏洞，包括：

1. **测试逻辑** - 具体的Solidity代码来触发/检测漏洞
2. **规范违反检测** - 检查哪些不变量或安全属性被违反
3. **攻击验证** - 验证攻击是否成功的断言

请严格按照以下格式返回（只返回代码，不要解释）：

testLogic: [具体的测试执行代码，可以是函数调用或直接的Solidity代码]
specViolationChecks: [检查规范违反的代码，多个检查用分号分隔]
attackVerification: [验证攻击成功的断言代码]

示例：
testLogic: vm.prank(attacker); token.mint(attacker, 1000000 * 10**18);
specViolationChecks: assertTrue(token.balanceOf(attacker) > 0, "Unauthorized mint detected"); assertFalse(_checkAuthorizationInvariant(), "Authorization invariant violated");
attackVerification: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Attack should increase attacker balance");
"""
        
        try:
            print("🧠 LLM正在生成测试逻辑...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🧠 LLM生成的测试逻辑:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            return self._parse_test_logic_response(response)
            
        except Exception as e:
            print(f"测试逻辑生成失败: {e}")
            return {
                'testLogic': '// 测试逻辑生成失败',
                'specViolationChecks': '// 规范检查生成失败',
                'attackVerification': '// 攻击验证生成失败'
            }
    
    def _parse_test_logic_response(self, response: str) -> Dict[str, str]:
        """解析测试逻辑响应"""
        result = {
            'testLogic': '// 默认测试逻辑',
            'specViolationChecks': '// 默认规范检查', 
            'attackVerification': '// 默认攻击验证'
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('testLogic:'):
                result['testLogic'] = line.replace('testLogic:', '').strip()
            elif line.startswith('specViolationChecks:'):
                result['specViolationChecks'] = line.replace('specViolationChecks:', '').strip()
            elif line.startswith('attackVerification:'):
                result['attackVerification'] = line.replace('attackVerification:', '').strip()
        
        return result
    
    def _get_default_specs(self) -> Dict[str, Any]:
        """获取默认规范（备用）"""
        return {
            "invariants": [
                {
                    "name": "balance_non_negative",
                    "description": "所有余额必须非负",
                    "condition": "balanceOf(account) >= 0",
                    "check_code": "assertTrue(token.balanceOf(attacker) >= 0, 'Balance must be non-negative')"
                }
            ],
            "pre_conditions": [],
            "post_conditions": [],
            "safety_properties": [
                {
                    "name": "unauthorized_operations",
                    "description": "防止未授权操作",
                    "violation_condition": "非授权用户执行特权操作",
                    "check_code": "// 检查授权"
                }
            ]
        }

