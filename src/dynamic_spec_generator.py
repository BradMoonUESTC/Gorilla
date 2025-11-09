"""
Dynamic Specification Generator - Use an LLM to dynamically generate formal specifications and invariants
"""

import os
import sys
from typing import Dict, List, Any

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common


class DynamicSpecGenerator:
    """Dynamic specification generator"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def generate_formal_specs(self, contract_code: str, vulnerability_focus: str = None) -> Dict[str, Any]:
        """Dynamically generate formal specifications for a given contract"""
        
        prompt = f"""
You are a formal verification expert. Please generate a complete set of formal specifications for the following smart contract.

=== Contract Code ===
{contract_code}

=== Task Requirements ===
Generate the following types of formal specifications:

1. Invariants - Conditions that must always hold for the contract
2. Pre-conditions - Conditions that must hold before a function executes
3. Post-conditions - Conditions that should hold after a function executes
4. Safety Properties - Security rules the contract must not violate

{f"Special focus: {vulnerability_focus}" if vulnerability_focus else ""}

Return strictly in the following JSON format (return JSON only, nothing else):
{{
    "invariants": [
        {{
            "name": "Invariant name",
            "description": "Invariant description",
            "condition": "Solidity condition expression",
            "check_code": "Verification code"
        }}
    ],
    "pre_conditions": [
        {{
            "function": "Function name",
            "condition": "Pre-condition",
            "description": "Description"
        }}
    ],
    "post_conditions": [
        {{
            "function": "Function name", 
            "condition": "Post-condition",
            "description": "Description"
        }}
    ],
    "safety_properties": [
        {{
            "name": "Safety property name",
            "description": "Safety property description",
            "violation_condition": "Conditions under which it is violated",
            "check_code": "Check code"
        }}
    ]
}}
"""
        
        try:
            print("🧠 LLM is generating formal specifications...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🧠 LLM-generated formal specifications:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            # 解析JSON响应
            import json
            try:
                specs = json.loads(response)
                return specs
            except json.JSONDecodeError:
                print("⚠️ JSON parsing failed, using default specifications")
                return self._get_default_specs()
                
        except Exception as e:
            print(f"Specification generation failed: {e}")
            return self._get_default_specs()
    
    def generate_vulnerability_test_logic(self, contract_code: str, vulnerability_description: str, formal_specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate vulnerability test logic based on formal specifications"""
        
        prompt = f"""
You are a smart contract security expert. Generate concrete vulnerability test logic based on the following information.

=== Contract Code ===
{contract_code}

=== Vulnerability Description ===
{vulnerability_description}

=== Formal Specifications ===
{formal_specs}

=== Task Requirements ===
Generate specific test logic to detect this vulnerability, including:

1. Test Logic - Concrete Solidity code to trigger/detect the vulnerability
2. Spec Violation Checks - Which invariants or safety properties are violated
3. Attack Verification - Assertions that verify whether the attack succeeded

Return strictly in the following format (code only, no explanations):

testLogic: [Concrete test execution code, either function calls or inline Solidity]
specViolationChecks: [Code to check spec violations, separated by semicolons]
attackVerification: [Assertions verifying the attack success]

Example:
testLogic: vm.prank(attacker); token.mint(attacker, 1000000 * 10**18);
specViolationChecks: assertTrue(token.balanceOf(attacker) > 0, "Unauthorized mint detected"); assertFalse(_checkAuthorizationInvariant(), "Authorization invariant violated");
attackVerification: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Attack should increase attacker balance");
"""
        
        try:
            print("🧠 LLM is generating test logic...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🧠 LLM-generated test logic:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            return self._parse_test_logic_response(response)
            
        except Exception as e:
            print(f"Test logic generation failed: {e}")
            return {
                'testLogic': '// Failed to generate test logic',
                'specViolationChecks': '// Failed to generate spec checks',
                'attackVerification': '// Failed to generate attack verification'
            }
    
    def _parse_test_logic_response(self, response: str) -> Dict[str, str]:
        """Parse the test logic response"""
        result = {
            'testLogic': '// Default test logic',
            'specViolationChecks': '// Default spec checks', 
            'attackVerification': '// Default attack verification'
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
        """Get default specifications (fallback)"""
        return {
            "invariants": [
                {
                    "name": "balance_non_negative",
                    "description": "All balances must be non-negative",
                    "condition": "balanceOf(account) >= 0",
                    "check_code": "assertTrue(token.balanceOf(attacker) >= 0, 'Balance must be non-negative')"
                }
            ],
            "pre_conditions": [],
            "post_conditions": [],
            "safety_properties": [
                {
                    "name": "unauthorized_operations",
                    "description": "Prevent unauthorized operations",
                    "violation_condition": "Non-authorized user executes privileged operation",
                    "check_code": "// Authorization check"
                }
            ]
        }

