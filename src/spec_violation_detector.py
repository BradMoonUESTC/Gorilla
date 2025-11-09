"""
Specification Violation Detector - Detects whether a contract violates formal specifications (using dynamic spec generation)
"""

import re
from typing import Dict, List, Any
from dynamic_spec_generator import DynamicSpecGenerator


class SpecViolationDetector:
    """Specification violation detector (based on dynamic spec generation)"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.spec_generator = DynamicSpecGenerator(project_path)
    
    def detect_spec_violations(self, vulnerability_type: str, contract_code: str) -> Dict[str, Any]:
        """Detect specification violations (using dynamic spec generation)"""
        
        violations = []
        
        # Detect corresponding specification violations based on vulnerability type
        if vulnerability_type == "unauthorized_mint":
            violations.extend(self._check_mint_authorization(contract_code))
            
        elif vulnerability_type == "allowance_bypass":
            violations.extend(self._check_allowance_mechanism(contract_code))
            
        elif vulnerability_type == "reentrancy":
            violations.extend(self._check_reentrancy_protection(contract_code))
            
        elif vulnerability_type == "integer_overflow":
            violations.extend(self._check_overflow_protection(contract_code))
        
        # General invariant checks
        violations.extend(self._check_general_invariants(contract_code))
        
        # Generate formal specs using the dynamic spec generator
        print("🧠 Generating invariants using the dynamic spec generator...")
        formal_specs = self.spec_generator.generate_formal_specs(
            contract_code, 
            vulnerability_focus=vulnerability_type
        )
        
        # 提取不变量用于测试
        invariants_to_check = self._extract_invariants_from_specs(formal_specs, vulnerability_type)
        
        return {
            "vulnerability_type": vulnerability_type,
            "has_violations": len(violations) > 0,
            "violations": violations,
            "invariants_to_check": invariants_to_check,
            "dynamic_specs": formal_specs
        }
    
    def _check_mint_authorization(self, contract_code: str) -> List[Dict[str, str]]:
        """Check mint authorization specification violations"""
        violations = []
        
        # Check whether the mint function has proper access control
        mint_pattern = r'function mint\([^)]*\)\s*public'
        if re.search(mint_pattern, contract_code):
            # Check if there is an access modifier or access check
            if not re.search(r'onlyOwner|require.*owner|msg\.sender.*owner', contract_code):
                violations.append({
                    "specification": "The mint function should have proper access control",
                    "reason": "The mint function lacks access checks; anyone can call it",
                    "severity": "HIGH",
                    "function": "mint"
                })
        
        return violations
    
    def _check_allowance_mechanism(self, contract_code: str) -> List[Dict[str, str]]:
        """Check allowance mechanism specification violations"""
        violations = []
        
        # Check whether transferFrom properly decreases the allowance
        transferfrom_pattern = r'function transferFrom\([^)]*\)\s*public[^}]*'
        match = re.search(transferfrom_pattern, contract_code, re.DOTALL)
        
        if match:
            function_body = match.group(0)
            # Check whether there is code that decreases the allowance
            if 'allowance[from][msg.sender] -= value' not in function_body and 'allowance[from][msg.sender] = allowance[from][msg.sender] - value' not in function_body:
                violations.append({
                    "specification": "transferFrom should decrease the allowance",
                    "reason": "The transferFrom function does not decrease allowance, which may allow reusing the approved amount repeatedly",
                    "severity": "HIGH", 
                    "function": "transferFrom"
                })
        
        return violations
    
    def _check_reentrancy_protection(self, contract_code: str) -> List[Dict[str, str]]:
        """Check reentrancy protection specification violations"""
        violations = []
        
        # Check reentrancy protection in the withdraw function
        withdraw_pattern = r'function withdraw\([^)]*\)[^}]*'
        match = re.search(withdraw_pattern, contract_code, re.DOTALL)
        
        if match:
            function_body = match.group(0)
            # Check whether state is updated before external calls
            external_call_pos = function_body.find('.call{value:')
            state_update_pos = function_body.find('balanceOf[msg.sender] = 0')
            
            if external_call_pos != -1 and state_update_pos != -1 and external_call_pos < state_update_pos:
                violations.append({
                    "specification": "State updates should occur before external calls",
                    "reason": "The withdraw function updates state after an external call, introducing reentrancy risk",
                    "severity": "CRITICAL",
                    "function": "withdraw"
                })
        
        return violations
    
    def _check_overflow_protection(self, contract_code: str) -> List[Dict[str, str]]:
        """Check integer overflow protection specification violations"""
        violations = []
        
        # Check whether 'unchecked' blocks are used
        if 'unchecked' in contract_code:
            violations.append({
                "specification": "Arithmetic operations should have overflow checks",
                "reason": "The code uses an unchecked block, which may introduce integer overflow risk",
                "severity": "MEDIUM",
                "function": "transfer"
            })
        
        return violations
    
    def _check_general_invariants(self, contract_code: str) -> List[Dict[str, str]]:
        """Check general invariant violations"""
        violations = []
        
        # Check whether appropriate input validation exists
        if 'require(to != address(0)' not in contract_code:
            violations.append({
                "specification": "Address parameters should be validated to be non-zero addresses",
                "reason": "Missing zero address checks may lead to token loss",
                "severity": "MEDIUM",
                "function": "transfer/mint"
            })
        
        return violations
    
    def _extract_invariants_from_specs(self, formal_specs: Dict[str, Any], vulnerability_type: str) -> List[Dict[str, str]]:
        """Extract invariants from dynamically generated formal specifications"""
        invariants = []
        
        # Extract invariants
        if 'invariants' in formal_specs:
            for inv in formal_specs['invariants']:
                invariants.append({
                    'name': inv.get('name', ''),
                    'description': inv.get('description', ''),
                    'condition': inv.get('condition', ''),
                    'violation_check': inv.get('check_code', '')
                })
        
        # Extract safety properties as invariants
        if 'safety_properties' in formal_specs:
            for prop in formal_specs['safety_properties']:
                invariants.append({
                    'name': prop.get('name', ''),
                    'description': prop.get('description', ''),
                    'condition': prop.get('violation_condition', ''),
                    'violation_check': prop.get('check_code', '')
                })
        
        return invariants


