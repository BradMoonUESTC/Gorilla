"""
测试生成器 - 基于自然语言输入生成Solidity测试代码
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common

from template_system import (
    read_base_template,
    generate_test_code,
    create_default_template_variables
)
from formal_specs import FormalSpecGenerator
from spec_violation_detector import SpecViolationDetector


class TestGenerator:
    """测试代码生成器"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.spec_generator = FormalSpecGenerator(project_path)
        self.violation_detector = SpecViolationDetector(project_path)
        
    def generate_test_from_description(self, description: str) -> str:
        """基于自然语言描述生成测试代码，支持两种模式：直接漏洞利用和规范违反检测"""
        
        # 1. 读取基础模板
        try:
            template_code = read_base_template(self.project_path)
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return ""
        
        # 2. 判断测试模式
        test_mode = self._determine_test_mode(description)
        print(f"🎯 测试模式: {test_mode}")
        
        if test_mode == "spec_violation":
            # 规范违反检测模式
            variables = self._generate_spec_violation_test(description, template_code)
        else:
            # 直接漏洞利用模式
            variables = self._generate_exploit_test(description, template_code)
        
        # 3. 生成测试代码
        test_code = generate_test_code(template_code, variables)
        
        # 4. 替换类名
        test_code = test_code.replace("GorillaBaseTest", "GorillaTest")
        
        return test_code
    
    def _generate_test_variables(self, description: str, template_code: str) -> Dict[str, str]:
        """使用LLM生成测试变量 - 专注于漏洞挖掘"""
        
        # 读取合约代码以提供更多上下文
        contract_code = self._read_contract_code()
        
        prompt = f"""
根据测试需求，选择并调用对应的漏洞利用函数。

测试需求: {description}

可用函数:
- _testUnauthorizedMint() (用于权限控制/mint相关测试)
- _testAllowanceBypass() (用于allowance/transferFrom相关测试)  
- _testReentrancyAttack() (用于重入攻击/withdraw相关测试)
- _testIntegerOverflow() (用于整数溢出相关测试)

请严格按照以下格式回答，不要添加任何其他内容：

testLogic: _testUnauthorizedMint();
vulnerabilityAssertions: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Unauthorized mint attack failed");

如果是allowance相关测试，则：
testLogic: _testAllowanceBypass();
vulnerabilityAssertions: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Allowance bypass attack failed");

如果是重入攻击相关测试，则：
testLogic: _testReentrancyAttack();
vulnerabilityAssertions: assertTrue(address(token).balance < contractEthBefore, "Reentrancy attack failed");

现在根据测试需求"{description}"选择对应的函数调用："""
        
        try:
            print("🤖 发送给LLM的prompt:")
            print("-" * 40)
            print(prompt)
            print("-" * 40)
            
            response = ask_openai_common(prompt)
            
            print("🤖 LLM返回结果:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            return self._parse_llm_response(response)
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return create_default_template_variables()
    
    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """解析LLM响应，提取模板变量"""
        variables = create_default_template_variables()
        
        # 简化的解析逻辑，只处理testLogic和vulnerabilityAssertions
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
    
    def _determine_test_mode(self, description: str) -> str:
        """判断测试模式：直接漏洞利用 vs 规范违反检测"""
        description_lower = description.lower()
        
        # 关键词判断规范违反模式
        spec_keywords = [
            "不变量", "invariant", "规范", "specification", "前置条件", "后置条件", 
            "pre-condition", "post-condition", "违反", "violation", "形式化", "formal"
        ]
        
        if any(keyword in description_lower for keyword in spec_keywords):
            return "spec_violation"
        else:
            return "exploit"
    
    def _generate_exploit_test(self, description: str, template_code: str) -> Dict[str, str]:
        """生成直接漏洞利用测试"""
        return self._generate_test_variables(description, template_code)
    
    def _generate_spec_violation_test(self, description: str, template_code: str) -> Dict[str, str]:
        """生成规范违反检测测试"""
        
        # 1. 识别漏洞类型
        vulnerability_type = self._identify_vulnerability_type(description)
        print(f"🔍 识别的漏洞类型: {vulnerability_type}")
        
        # 2. 检测规范违反
        contract_code = self._read_contract_code()
        print("📋 正在分析合约代码...")
        violation_info = self.violation_detector.detect_spec_violations(vulnerability_type, contract_code)
        print(f"📋 规范违反分析完成，漏洞类型: {vulnerability_type}")
        
        if violation_info['has_violations']:
            print(f"⚠️  检测到规范违反: {len(violation_info['violations'])} 个")
            for i, violation in enumerate(violation_info['violations'], 1):
                print(f"   {i}. {violation['reason']}")
        else:
            print("✅ 未检测到明显的规范违反")
        
        # 3. 生成规范违反测试代码
        return self._generate_spec_based_test_variables(vulnerability_type, violation_info)
    
    def _identify_vulnerability_type(self, description: str) -> str:
        """识别漏洞类型"""
        description_lower = description.lower()
        
        if 'mint' in description_lower or '权限' in description_lower or 'unauthorized' in description_lower:
            return 'unauthorized_mint'
        elif 'allowance' in description_lower or 'transferfrom' in description_lower or '授权' in description_lower:
            return 'allowance_bypass'
        elif 'reentrancy' in description_lower or 'reentrant' in description_lower or '重入' in description_lower or 'withdraw' in description_lower:
            return 'reentrancy'
        elif 'overflow' in description_lower or '溢出' in description_lower or 'unchecked' in description_lower:
            return 'integer_overflow'
        else:
            return 'unauthorized_mint'  # 默认类型
    
    def _generate_spec_based_test_variables(self, vulnerability_type: str, violation_info: Dict) -> Dict[str, str]:
        """基于规范违反生成测试变量"""
        
        # 获取相关的不变量
        invariants = violation_info['invariants_to_check']
        
        # 基于漏洞类型和规范违反生成测试逻辑
        test_logic_map = {
            'unauthorized_mint': '_testUnauthorizedMint();',
            'allowance_bypass': '_testAllowanceBypass();',
            'reentrancy': '_testReentrancyAttack();',
            'integer_overflow': '_testIntegerOverflow();'
        }
        
        # 生成规范违反检测的断言
        invariant_checks = []
        for inv in invariants:
            invariant_checks.append(inv.violation_check)
        
        # 组合断言
        combined_assertions = '\n        '.join(invariant_checks)
        
        # 如果检测到规范违反，添加详细信息
        if violation_info['has_violations']:
            violation = violation_info['violations'][0]
            comment = f"// 检测到规范违反: {violation['specification']}\n        // 违反原因: {violation['reason']}\n        "
            test_logic = comment + test_logic_map.get(vulnerability_type, '_testUnauthorizedMint();')
        else:
            test_logic = test_logic_map.get(vulnerability_type, '_testUnauthorizedMint();')
        
        return {
            'testLogic': test_logic,
            'vulnerabilityAssertions': combined_assertions
        }
