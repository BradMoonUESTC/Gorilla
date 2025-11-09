#!/usr/bin/env python3
"""
Script to test all vulnerability types
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """Test all vulnerability types"""
    
    print("🔍 Testing all vulnerability types")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Set project path
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # Create test system
    system = GorillaTestSystem(project_path)
    
    # Different types of vulnerability tests
    vulnerability_tests = [
        {
            "name": "Access Control Vulnerability",
            "description": "Test the ERC20 contract for access control vulnerabilities; verify whether the mint function can be called by any user"
        },
        {
            "name": "Allowance Mechanism Vulnerability", 
            "description": "Test the ERC20 contract for allowance mechanism issues; check whether transferFrom properly decreases the allowance"
        },
        {
            "name": "Reentrancy Vulnerability",
            "description": "Test the ERC20 contract for reentrancy vulnerabilities, especially the reentrancy risk in withdraw"
        }
    ]
    
    for i, test in enumerate(vulnerability_tests, 1):
        print(f"\n🎯 Test {i}: {test['name']}")
        print(f"Description: {test['description']}")
        print("-" * 40)
        
        try:
            success = system.generate_and_run_test(test['description'])
            
            if success:
                print(f"✅ {test['name']} - Exploit succeeded!")
            else:
                print(f"❌ {test['name']} - Test failed")
                
        except Exception as e:
            print(f"❌ {test['name']} - Error: {e}")
        
        if i < len(vulnerability_tests):
            print("\n" + "="*30)

    print(f"\n🎉 All vulnerability tests completed!")

if __name__ == "__main__":
    main()


