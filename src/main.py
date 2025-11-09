"""
Main program - Gorilla test generation and execution system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from dynamic_test_generator import DynamicTestGenerator
from forge_executor import ForgeExecutor
from auto_fixer import AutoFixer


class GorillaTestSystem:
    """Main class for the Gorilla testing system"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.test_generator = DynamicTestGenerator(project_path)
        self.forge_executor = ForgeExecutor(project_path)
        self.auto_fixer = AutoFixer(project_path=project_path)
        
    def generate_and_run_test(self, description: str) -> bool:
        """Full flow to generate and run a test"""
        
        print(f"🚀 Starting to process test requirement: {description}")
        
        # 1. Check environment
        if not self._check_environment():
            return False
            
        # 2. Generate initial test code
        print("📝 Generating test code...")
        test_code = self.test_generator.generate_test_from_description(description)
        if not test_code:
            print("❌ Test code generation failed")
            return False
        
        # 3. Execute tests and auto-fix
        max_fix_attempts = 3
        for attempt in range(max_fix_attempts + 1):
            
            if attempt == 0:
                print("🧪 Running initial test...")
            else:
                print(f"🔧 Running fixed test (attempt {attempt})")
                
            # 执行测试
            success, output = self.forge_executor.write_and_run_test(test_code)
            
            if success:
                print("🎉 Test executed successfully!")
                print("Test output:")
                print(output)
                return True
            else:
                print(f"❌ Test failed (attempt {attempt + 1}/{max_fix_attempts + 1})")
                print("Error output:")
                print(output)
                
                # If not the last attempt, try to automatically fix
                if attempt < max_fix_attempts:
                    print("🔧 Starting auto-fix...")
                    fixed_code, fix_success = self.auto_fixer.fix_test_code(
                        test_code, output, description
                    )
                    
                    if fix_success:
                        test_code = fixed_code
                        print("✅ Code fixed, re-running tests...")
                    else:
                        print("❌ Auto-fix failed")
                        break
        
        print("❌ Final test failed; maximum retries reached")
        return False
    
    def _check_environment(self) -> bool:
        """Check the runtime environment"""
        
        # Check project path
        if not Path(self.project_path).exists():
            print(f"❌ Project path does not exist: {self.project_path}")
            return False
            
        # Check Foundry installation
        if not self.forge_executor.check_foundry_installation():
            print("❌ Foundry is not installed. Please install Foundry first.")
            print("Install command: curl -L https://foundry.paradigm.xyz | bash")
            return False
            
        # Check or initialize Foundry project
        if not self.forge_executor.initialize_foundry_project():
            print("❌ Foundry project initialization failed")
            return False
            
        # Check base template
        template_path = Path(self.project_path) / "test" / "GorillaBase.t.sol"
        if not template_path.exists():
            print(f"❌ Base template file does not exist: {template_path}")
            print("Please create the base template file")
            return False
            
        return True


def main():
    """Main function"""
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) < 3:
        print("Usage: python main.py <project_path> <test_description>")
        print("Example: python main.py ./test-project 'Test ERC20 token transfer function'")
        return
    
    project_path = sys.argv[1]
    description = sys.argv[2]
    
    # Create testing system
    system = GorillaTestSystem(project_path)
    
    # Run test
    success = system.generate_and_run_test(description)
    
    if success:
        print("🎉 Test flow completed!")
        sys.exit(0)
    else:
        print("❌ Test flow failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
