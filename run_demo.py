#!/usr/bin/env python3
"""
Automated demo script - run a single test case directly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem


def main():
    """Automated demo"""
    
    print("🚀 Gorilla Testing System Automated Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Set project path
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    print(f"📁 Project path: {project_path}")
    
    # Create test system
    system = GorillaTestSystem(project_path)
    
    # Simple test case
    description = "Test the basic ERC20 token transfer function: deploy the token contract, allocate tokens to users, then test transferring from one address to another"
    
    print(f"\n🎯 Test description: {description}")
    print("=" * 50)
    
    # Execute test
    try:
        success = system.generate_and_run_test(description)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Demo complete! Test executed successfully")
            
            # Show the generated test file
            test_file = Path(project_path) / "test" / "GorillaTest.t.sol"
            if test_file.exists():
                print(f"\n📄 Generated test file: {test_file}")
                print("File preview:")
                print("-" * 30)
                with open(test_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
                        print(f"{i:2d}| {line}")
                    if len(lines) > 20:
                        print(f"... ({len(lines) - 20} more lines)")
        else:
            print("❌ Demo complete, but test execution failed")
            
    except Exception as e:
        print(f"\n❌ An error occurred during the demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
