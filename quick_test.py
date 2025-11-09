#!/usr/bin/env python3
"""
Quick test for the improved vulnerability exploration system
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """Quick test"""
    
    print("🔍 Quick test for the vulnerability exploration system")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Set project path
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # Create test system
    system = GorillaTestSystem(project_path)
    
    # Test access control vulnerability
    description = "Test the access control vulnerability of an ERC20 contract; verify whether the mint function can be called by any user"
    
    print(f"🎯 Test description: {description}")
    print("-" * 40)
    
    try:
        success = system.generate_and_run_test(description)
        
        if success:
            print("✅ Vulnerability exploration test succeeded!")
            
            # Show key parts of the generated test code
            from pathlib import Path
            test_file = Path(project_path) / "test" / "GorillaTest.t.sol"
            if test_file.exists():
                with open(test_file, 'r') as f:
                    content = f.read()
                    # Look for test logic
                    if "_test" in content:
                        print("🎉 Successfully generated exploit code!")
                    else:
                        print("⚠️ Potentially failed to generate valid exploit code")
        else:
            print("❌ Test failed")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()


