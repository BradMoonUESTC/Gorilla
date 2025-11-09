"""
Dynamic Test Generator - Fully generate test cases with LLM dynamically
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
    """Fully dynamic test generator"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.spec_generator = DynamicSpecGenerator(project_path)
    
    def generate_test_from_description(self, description: str) -> str:
        """Fully generate test code dynamically with LLM"""
        
        # 1. Read base template
        try:
            template_code = read_base_template(self.project_path)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return ""
        
        # 2. Read contract code
        contract_code = self._read_contract_code()
        
        # 3. Determine test mode
        test_mode = self._determine_test_mode(description)
        print(f"🎯 Test mode: {test_mode}")
        
        if test_mode == "spec_violation":
            # Specification violation detection mode
            variables = self._generate_dynamic_spec_test(description, contract_code)
        else:
            # Direct exploit testing mode
            variables = self._generate_dynamic_exploit_test(description, contract_code)
        
        # 4. Generate test code
        test_code = generate_test_code(template_code, variables)
        
        # 5. Replace class name
        test_code = test_code.replace("GorillaBaseTest", "GorillaTest")
        
        return test_code
    
    def _determine_test_mode(self, description: str) -> str:
        """Determine test mode"""
        description_lower = description.lower()
        
        spec_keywords = [
            "invariant", "specification", "pre-condition", "post-condition",
            "violation", "formal", "invariants", "specifications", "precondition", "postcondition"
        ]
        
        if any(keyword in description_lower for keyword in spec_keywords):
            return "spec_violation"
        else:
            return "exploit"
    
    def _generate_dynamic_exploit_test(self, description: str, contract_code: str) -> Dict[str, str]:
        """Dynamically generate exploit test"""
        
        prompt = f"""
You are a smart contract security expert. Please generate concrete exploit code for the following testing requirement.

=== Contract Code ===
{contract_code}

=== Testing Requirement ===
{description}

=== Available Test Environment ===
- token: SimpleERC20 contract instance
- attacker, victim, owner, user1, user2: test account addresses
- All accounts have 100 ETH and initial token balances
- Foundry helpers: vm.prank(), vm.deal(), vm.startPrank(), etc.

=== Task Requirements ===
Generate concrete Solidity code to perform the exploit test. Do not call predefined helper functions; write the exploit logic directly.

Return strictly in the following format (code only, no explanations):

testLogic: [Concrete exploit code, can be multiple lines separated by semicolons]
vulnerabilityAssertions: [Assertions that verify the exploit succeeded]

Example:
testLogic: vm.prank(attacker); token.mint(attacker, 1000000 * 10**18);
vulnerabilityAssertions: assertTrue(token.balanceOf(attacker) > attackerBalanceBefore, "Unauthorized mint attack should succeed");
"""
        
        try:
            print("🤖 LLM is generating a dynamic exploit test...")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            response = ask_openai_common(prompt)
            
            print("🤖 LLM-generated exploit test:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Dynamic test generation failed: {e}")
            return create_default_template_variables()
    
    def _generate_dynamic_spec_test(self, description: str, contract_code: str) -> Dict[str, str]:
        """Dynamically generate specification violation detection test"""
        
        # 1. First ask the LLM to generate formal specifications
        formal_specs = self.spec_generator.generate_formal_specs(contract_code, description)
        
        # 2. Generate test logic based on the specifications
        test_logic = self.spec_generator.generate_vulnerability_test_logic(
            contract_code, description, formal_specs
        )
        
        # 3. Compose final template variables
        return {
            'testLogic': test_logic['testLogic'],
            'vulnerabilityAssertions': f"{test_logic['specViolationChecks']}; {test_logic['attackVerification']}"
        }
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response"""
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
        """Read target contract code"""
        try:
            contract_path = Path(self.project_path) / "src" / "SimpleERC20.sol"
            if contract_path.exists():
                with open(contract_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "// Contract file does not exist"
        except Exception as e:
            return f"// Failed to read contract: {e}"




