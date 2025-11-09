"""
Auto Fixer - Automatically fix test errors using an LLM
"""

import os
import sys
from typing import Tuple

# 添加openai_api到路径
openai_api_path = os.path.join(os.path.dirname(__file__), 'openai_api')
sys.path.append(openai_api_path)
from openai_api.openai import ask_openai_common


class AutoFixer:
    """Automatic test fixer"""
    
    def __init__(self, max_attempts: int = 3, project_path: str = None):
        self.max_attempts = max_attempts
        self.project_path = project_path
    
    def fix_test_code(self, test_code: str, error_output: str, original_description: str) -> Tuple[str, bool]:
        """Automatically fix test code"""
        
        current_code = test_code
        
        for attempt in range(self.max_attempts):
            print(f"🔧 Attempting to fix test code ({attempt + 1}/{self.max_attempts})")
            
            fixed_code = self._generate_fix(current_code, error_output, original_description, attempt)
            
            if fixed_code and fixed_code != current_code:
                current_code = fixed_code
                print(f"✅ Produced fix version {attempt + 1}")
                return current_code, True
            else:
                print(f"❌ Fix attempt {attempt + 1} failed")
        
        print("❌ Reached maximum fix attempts, repair failed")
        return current_code, False
    
    def _generate_fix(self, test_code: str, error_output: str, original_description: str, attempt: int) -> str:
        """Generate a fix using the LLM"""
        
        # Retrieve project context info
        context_info = self._get_project_context()
        error_analysis = self.analyze_error_type(error_output)
        
        prompt = f"""
You are a Solidity test code fixing expert. The following test code failed during execution; please fix it.

=== Project Context Information ===
{context_info}

=== Test Requirement ===
{original_description}

=== Current Test Code ===
```solidity
{test_code}
```

=== Error Information ===
Error Type: {error_analysis}
Detailed Output:
```
{error_output}
```

=== Fix Guidance ===
Fix Attempt: {attempt + 1}/{self.max_attempts}

Based on the error type, focus on:
{self._get_fix_guidance(error_analysis)}

=== Requirements ===
1. Carefully analyze the root cause, especially constructor parameters
2. Ensure all import statements are correct
3. Verify the types and order of constructor/instantiation parameters
4. Preserve the test logic’s intent
5. Use correct Solidity syntax

Return only the fully fixed Solidity code, with no explanations.
"""
        
        try:
            print("🔧 Prompt sent to the fixing LLM:")
            print("-" * 40)
            print(prompt)
            print("-" * 40)
            
            response = ask_openai_common(prompt)
            
            print("🔧 Fixing LLM response:")
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
            
            # If there is no code fence, return the whole response
            return response.strip()
            
        except Exception as e:
            print(f"LLM fix call failed: {e}")
            return ""
    
    def analyze_error_type(self, error_output: str) -> str:
        """Analyze error type"""
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
        """Get project context information"""
        if not self.project_path:
            return "Project path not provided"
        
        from pathlib import Path
        context = []
        
        # Read SimpleERC20 contract info
        erc20_path = Path(self.project_path) / "src" / "SimpleERC20.sol"
        if erc20_path.exists():
            try:
                with open(erc20_path, 'r', encoding='utf-8') as f:
                    erc20_content = f.read()
                    
                # Extract constructor signature
                if "constructor(" in erc20_content:
                    start = erc20_content.find("constructor(")
                    end = erc20_content.find(")", start) + 1
                    constructor_sig = erc20_content[start:end]
                    context.append(f"SimpleERC20 constructor: {constructor_sig}")
                    
                # Extract main functions
                functions = ["transfer", "transferFrom", "approve", "mint", "burn"]
                for func in functions:
                    if f"function {func}(" in erc20_content:
                        context.append(f"- Contains {func} function")
                        
            except Exception as e:
                context.append(f"Failed to read SimpleERC20 contract: {e}")
        else:
            context.append("SimpleERC20 contract file does not exist")
        
        # Read base template info
        template_path = Path(self.project_path) / "test" / "GorillaBase.t.sol"
        if template_path.exists():
            context.append("Base test template: GorillaBase.t.sol exists")
        else:
            context.append("Base test template: GorillaBase.t.sol does not exist")
        
        return "\n".join(context) if context else "Unable to obtain project context"
    
    def _get_fix_guidance(self, error_type: str) -> str:
        """Provide fix guidance based on error type"""
        guidance = {
            "compilation_error": """
- Check the constructor parameter types and order
- SimpleERC20 constructor expects: (string _name, string _symbol, uint8 _decimals, uint256 _totalSupply)
- Ensure string parameters are quoted
- Ensure numeric parameter types are correct
- Verify import statements""",
            
            "runtime_error": """
- Check contract state and balances
- Validate function preconditions
- Ensure accounts have sufficient token balances
- Verify allowance settings""",
            
            "assertion_error": """
- Check that assertion expectations are correct
- Validate that test logic matches the intent
- Ensure balance calculations are correct""",
            
            "dependency_error": """
- Verify import paths
- Ensure all dependent contract files exist
- Validate forge-std imports""",
            
            "unknown_error": """
- Carefully read the error details
- Check for syntax errors
- Verify contract instantiation process
- Ensure all variables are initialized correctly"""
        }
        
        return guidance.get(error_type, guidance["unknown_error"])
