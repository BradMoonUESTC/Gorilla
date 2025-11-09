"""
动态测试生成器 - 完全基于LLM动态生成测试用例
"""

import os
import sys
from typing import Dict, List, Any
from pathlib import Path

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common

from template_system import (
    read_base_template,
    generate_test_code,
    create_default_template_variables
)
from dynamic_spec_generator import DynamicSpecGenerator


class DynamicTestGenerator:
    """完全动态的测试生成器"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.spec_generator = DynamicSpecGenerator(project_path)
    
    def generate_test_from_description(self, description: str) -> str:
        """完全基于LLM动态生成测试代码"""
        
        # 1. 读取基础模板
        try:
            template_code = read_base_template(self.project_path)
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return ""
        
        # 2. 读取合约代码
        contract_code = self._read_contract_code()
        
        # 3. 判断测试模式
        test_mode = self._determine_test_mode(description)
        print(f"🎯 测试模式: {test_mode}")
        
        if test_mode == "spec_violation":
            # 规范违反检测模式
            variables = self._generate_dynamic_spec_test(description, contract_code)
        else:
            # 直接漏洞利用模式
            variables = self._generate_dynamic_exploit_test(description, contract_code)
        
        # 4. 生成测试代码
        test_code = generate_test_code(template_code, variables)
        
        # 5. 替换类名
        test_code = test_code.replace("GorillaBaseTest", "GorillaTest")
        
        return test_code
    
    def _determine_test_mode(self, description: str) -> str:
        """判断测试模式"""
        description_lower = description.lower()
        
        spec_keywords = [
            "不变量", "invariant", "规范", "specification", "前置条件", "后置条件", 
            "pre-condition", "post-condition", "违反", "violation", "形式化", "formal"
        ]
        
        if any(keyword in description_lower for keyword in spec_keywords):
            return "spec_violation"
        else:
            return "exploit"
    
    def _generate_dynamic_exploit_test(self, description: str, contract_code: str) -> Dict[str, str]:
        """动态生成漏洞利用测试"""
        
        prompt = f"""
你是一个智能合约安全专家。请为以下测试需求生成具体的漏洞利用代码。

=== 合约代码 ===
{contract_code}

=== 测试需求 ===
{description}

=== 可用的测试环境 ===
- token: SimpleERC20合约实例
- attacker, victim, owner, user1, user2: 测试账户地址
- 所有账户都有100 ETH和初始代币余额
- vm.prank(), vm.deal(), vm.startPrank()等Foundry测试工具

=== 任务要求 ===
请生成具体的Solidity代码来执行漏洞利用测试。不要调用预定义函数，而是直接编写漏洞利用逻辑。

请严格按照以下格式返回（只返回代码，不要解释）：

testLogic: [具体的漏洞利用代码，可以是多行，用分号分隔]
vulnerabilityAssertions: [验证漏洞利用成功的断言]

示例：
testLogic: vm.prank(attacker); token.mint(attacker, 1000000 * 10**18);
vulnerabilityAssertions: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Unauthorized mint attack should succeed");
"""
        
        try:
            print("🤖 LLM正在生成动态漏洞利用测试...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🤖 LLM生成的漏洞利用测试:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            return self._parse_response(response)
            
        except Exception as e:
            print(f"动态测试生成失败: {e}")
            return create_default_template_variables()
    
    def _generate_dynamic_spec_test(self, description: str, contract_code: str) -> Dict[str, str]:
        """动态生成规范违反检测测试"""
        
        # 1. 首先让LLM生成形式化规范
        formal_specs = self.spec_generator.generate_formal_specs(contract_code, description)
        
        # 2. 基于规范生成测试逻辑
        test_logic = self.spec_generator.generate_vulnerability_test_logic(
            contract_code, description, formal_specs
        )
        
        # 3. 组合成最终的测试变量
        return {
            'testLogic': test_logic['testLogic'],
            'vulnerabilityAssertions': f"{test_logic['specViolationChecks']}; {test_logic['attackVerification']}"
        }
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """解析LLM响应"""
        variables = create_default_template_variables()
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('testLogic:'):
                content = line.replace('testLogic:', '').strip()
                if content:
                    variables['testLogic'] = content
            elif line.startswith('vulnerabilityAssertions:'):
                content = line.replace('vulnerabilityAssertions:', '').strip()
                if content:
                    variables['vulnerabilityAssertions'] = content
        
        return variables
    
    def _read_contract_code(self) -> str:
        """读取目标合约代码"""
        try:
            contract_path = Path(self.project_path) / "src" / "SimpleERC20.sol"
            if contract_path.exists():
                with open(contract_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "// 合约文件不存在"
        except Exception as e:
            return f"// 读取合约失败: {e}"




