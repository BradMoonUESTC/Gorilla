#!/usr/bin/env python3
"""
动态测试系统验证 - 测试完全基于LLM的规范和测试生成
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """动态测试验证"""
    
    print("🚀 完全动态的漏洞挖掘系统测试")
    print("=" * 60)
    print("💡 所有规范、不变量和测试逻辑都由LLM动态生成")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 测试用例：完全动态生成
    test_cases = [
        {
            "name": "动态漏洞利用测试",
            "description": "分析ERC20合约的mint函数，发现权限控制漏洞并进行利用"
        },
        {
            "name": "动态规范违反检测",
            "description": "为ERC20合约生成形式化规范，检测mint函数是否违反了权限控制不变量"
        },
        {
            "name": "动态allowance测试",
            "description": "分析transferFrom函数的实现，检测allowance机制的潜在漏洞"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 测试 {i}: {test_case['name']}")
        print(f"📝 描述: {test_case['description']}")
        print("=" * 60)
        
        try:
            success = system.generate_and_run_test(test_case['description'])
            
            print("=" * 60)
            if success:
                print(f"✅ {test_case['name']} - 动态生成和执行成功!")
                
                # 检查生成的测试文件
                from pathlib import Path
                test_file = Path(project_path) / "test" / "GorillaTest.t.sol"
                if test_file.exists():
                    with open(test_file, 'r') as f:
                        content = f.read()
                    
                    # 检查是否包含动态生成的内容
                    if "vm.prank" in content or "token.mint" in content or "token.transferFrom" in content:
                        print("🎉 检测到动态生成的具体测试逻辑!")
                    if "assertTrue" in content or "assertEq" in content:
                        print("🎉 检测到动态生成的验证断言!")
                        
            else:
                print(f"❌ {test_case['name']} - 执行失败")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(test_cases):
            input(f"\n按Enter继续下一个测试...")
    
    print(f"\n🎉 动态测试系统验证完成!")
    print("📊 系统特点:")
    print("  ✅ 规范完全由LLM动态生成")
    print("  ✅ 测试逻辑完全由LLM动态生成")
    print("  ✅ 不依赖预定义的函数或模板")
    print("  ✅ 支持任意复杂度的漏洞分析")

if __name__ == "__main__":
    main()
