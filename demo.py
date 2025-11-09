#!/usr/bin/env python3
"""
Gorilla testing system demo script
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem


def main():
    """Demo entry point"""
    
    print("🚀 Gorilla Testing System Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        return
        
    print(f"✅ API Base: {api_base}")
    print(f"✅ API Key: {api_key[:10]}...")
    print()
    
    # Set project path
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    print(f"📁 Project path: {project_path}")
    print()
    
    # Create test system
    system = GorillaTestSystem(project_path)
    
    # Vulnerability exploration test cases
    test_cases = [
        "Test the ERC20 contract for reentrancy, especially the reentrancy risk in withdraw",
        "Test the ERC20 contract for access control; verify whether the mint function can be called by any user",
        "Test the ERC20 contract for allowance mechanism issues; check whether transferFrom properly decreases the allowance",
        "Test the ERC20 contract for integer overflow; look for overflow risks in unchecked blocks",
        "Comprehensive smart contract security audit; find all potential logical and security risks",
    ]
    
    print("🔍 Available vulnerability exploration test cases:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"  {i}. {test_case}")
    print()
    
    # Let the user choose a test case
    try:
        choice = input(f"Choose a test case (1-{len(test_cases)}) or enter a custom description: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(test_cases):
            description = test_cases[int(choice) - 1]
        else:
            description = choice
            
        if not description:
            print("❌ No test description provided")
            return
            
        print(f"\n🎯 Selected test: {description}")
        print("=" * 50)
        
        # Execute test
        success = system.generate_and_run_test(description)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Demo complete! Test executed successfully")
        else:
            print("❌ Demo complete, but test execution failed")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred during the demo: {e}")


if __name__ == "__main__":
    main()
