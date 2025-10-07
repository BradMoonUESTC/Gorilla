"""
规范违反检测器 - 检测合约是否违反了形式化规范
"""

import re
from typing import Dict, List, Any
from formal_specs import FormalSpecGenerator


class SpecViolationDetector:
    """规范违反检测器"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.spec_generator = FormalSpecGenerator(project_path)
    
    def detect_spec_violations(self, vulnerability_type: str, contract_code: str) -> Dict[str, Any]:
        """检测规范违反"""
        
        violations = []
        
        # 根据漏洞类型检测对应的规范违反
        if vulnerability_type == "unauthorized_mint":
            violations.extend(self._check_mint_authorization(contract_code))
            
        elif vulnerability_type == "allowance_bypass":
            violations.extend(self._check_allowance_mechanism(contract_code))
            
        elif vulnerability_type == "reentrancy":
            violations.extend(self._check_reentrancy_protection(contract_code))
            
        elif vulnerability_type == "integer_overflow":
            violations.extend(self._check_overflow_protection(contract_code))
        
        # 通用不变量检查
        violations.extend(self._check_general_invariants(contract_code))
        
        return {
            "vulnerability_type": vulnerability_type,
            "has_violations": len(violations) > 0,
            "violations": violations,
            "invariants_to_check": self.spec_generator.get_invariants_for_test(vulnerability_type)
        }
    
    def _check_mint_authorization(self, contract_code: str) -> List[Dict[str, str]]:
        """检查铸币授权规范违反"""
        violations = []
        
        # 检查mint函数是否有权限控制
        mint_pattern = r'function mint\([^)]*\)\s*public'
        if re.search(mint_pattern, contract_code):
            # 检查是否有权限修饰符或权限检查
            if not re.search(r'onlyOwner|require.*owner|msg\.sender.*owner', contract_code):
                violations.append({
                    "specification": "mint函数应该有适当的权限控制",
                    "reason": "mint函数缺少权限检查，任何人都可以调用",
                    "severity": "HIGH",
                    "function": "mint"
                })
        
        return violations
    
    def _check_allowance_mechanism(self, contract_code: str) -> List[Dict[str, str]]:
        """检查授权机制规范违反"""
        violations = []
        
        # 检查transferFrom是否正确减少allowance
        transferfrom_pattern = r'function transferFrom\([^)]*\)\s*public[^}]*'
        match = re.search(transferfrom_pattern, contract_code, re.DOTALL)
        
        if match:
            function_body = match.group(0)
            # 检查是否有减少allowance的代码
            if 'allowance[from][msg.sender] -= value' not in function_body and 'allowance[from][msg.sender] = allowance[from][msg.sender] - value' not in function_body:
                violations.append({
                    "specification": "transferFrom应该减少授权额度",
                    "reason": "transferFrom函数没有减少allowance，可能导致重复使用授权",
                    "severity": "HIGH", 
                    "function": "transferFrom"
                })
        
        return violations
    
    def _check_reentrancy_protection(self, contract_code: str) -> List[Dict[str, str]]:
        """检查重入攻击保护规范违反"""
        violations = []
        
        # 检查withdraw函数的重入保护
        withdraw_pattern = r'function withdraw\([^)]*\)[^}]*'
        match = re.search(withdraw_pattern, contract_code, re.DOTALL)
        
        if match:
            function_body = match.group(0)
            # 检查是否在外部调用前更新状态
            external_call_pos = function_body.find('.call{value:')
            state_update_pos = function_body.find('balanceOf[msg.sender] = 0')
            
            if external_call_pos != -1 and state_update_pos != -1 and external_call_pos < state_update_pos:
                violations.append({
                    "specification": "状态更新应该在外部调用之前",
                    "reason": "withdraw函数在外部调用后才更新状态，存在重入攻击风险",
                    "severity": "CRITICAL",
                    "function": "withdraw"
                })
        
        return violations
    
    def _check_overflow_protection(self, contract_code: str) -> List[Dict[str, str]]:
        """检查整数溢出保护规范违反"""
        violations = []
        
        # 检查是否使用了unchecked块
        if 'unchecked' in contract_code:
            violations.append({
                "specification": "算术运算应该有溢出检查",
                "reason": "代码中使用了unchecked块，可能存在整数溢出风险",
                "severity": "MEDIUM",
                "function": "transfer"
            })
        
        return violations
    
    def _check_general_invariants(self, contract_code: str) -> List[Dict[str, str]]:
        """检查通用不变量违反"""
        violations = []
        
        # 检查是否有适当的输入验证
        if 'require(to != address(0)' not in contract_code:
            violations.append({
                "specification": "应该验证地址参数不为零地址",
                "reason": "缺少零地址检查，可能导致代币丢失",
                "severity": "MEDIUM",
                "function": "transfer/mint"
            })
        
        return violations


