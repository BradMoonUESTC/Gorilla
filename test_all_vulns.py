#!/usr/bin/env python3
"""
测试所有漏洞类型的脚本
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """测试所有漏洞类型"""
    
    print("🔍 测试所有漏洞类型")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 不同类型的漏洞测试
    vulnerability_tests = [
        {
            "name": "权限控制漏洞",
            "description": "测试ERC20合约的权限控制漏洞，验证mint函数是否可以被任意用户调用"
        },
        {
            "name": "Allowance机制漏洞", 
            "description": "测试ERC20合约的allowance机制漏洞，检查transferFrom是否正确减少授权额度"
        },
        {
            "name": "重入攻击漏洞",
            "description": "测试ERC20合约的重入攻击漏洞，特别是withdraw函数的重入风险"
        }
    ]
    
    for i, test in enumerate(vulnerability_tests, 1):
        print(f"\n🎯 测试 {i}: {test['name']}")
        print(f"描述: {test['description']}")
        print("-" * 40)
        
        try:
            success = system.generate_and_run_test(test['description'])
            
            if success:
                print(f"✅ {test['name']} - 漏洞利用成功!")
            else:
                print(f"❌ {test['name']} - 测试失败")
                
        except Exception as e:
            print(f"❌ {test['name']} - 发生错误: {e}")
        
        if i < len(vulnerability_tests):
            print("\n" + "="*30)

    print(f"\n🎉 所有漏洞测试完成!")

if __name__ == "__main__":
    main()


