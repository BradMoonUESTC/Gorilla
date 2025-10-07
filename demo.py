#!/usr/bin/env python3
"""
Gorilla测试系统演示脚本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem


def main():
    """演示主函数"""
    
    print("🚀 Gorilla测试系统演示")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("❌ 错误: OPENAI_API_KEY 环境变量未设置")
        return
        
    print(f"✅ API Base: {api_base}")
    print(f"✅ API Key: {api_key[:10]}...")
    print()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    print(f"📁 项目路径: {project_path}")
    print()
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 漏洞挖掘测试用例列表
    test_cases = [
        "测试ERC20合约的重入攻击漏洞，特别是withdraw函数的重入风险",
        "测试ERC20合约的权限控制漏洞，验证mint函数是否可以被任意用户调用",
        "测试ERC20合约的allowance机制漏洞，检查transferFrom是否正确减少授权额度",
        "测试ERC20合约的整数溢出漏洞，在unchecked块中寻找溢出风险",
        "全面的智能合约安全审计测试，挖掘所有可能的逻辑漏洞和安全风险",
    ]
    
    print("🔍 可用的漏洞挖掘测试用例:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"  {i}. {test_case}")
    print()
    
    # 让用户选择测试用例
    try:
        choice = input(f"请选择测试用例 (1-{len(test_cases)}) 或输入自定义描述: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(test_cases):
            description = test_cases[int(choice) - 1]
        else:
            description = choice
            
        if not description:
            print("❌ 未提供测试描述")
            return
            
        print(f"\n🎯 选择的测试: {description}")
        print("=" * 50)
        
        # 执行测试
        success = system.generate_and_run_test(description)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 演示完成! 测试成功执行")
        else:
            print("❌ 演示完成，但测试执行失败")
            
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    main()
