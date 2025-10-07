#!/usr/bin/env python3
"""
快速测试改进后的漏洞挖掘系统
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """快速测试"""
    
    print("🔍 快速测试漏洞挖掘系统")
    print("=" * 40)
    
    # 加载环境变量
    load_dotenv()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 测试权限控制漏洞
    description = "测试ERC20合约的权限控制漏洞，验证mint函数是否可以被任意用户调用"
    
    print(f"🎯 测试描述: {description}")
    print("-" * 40)
    
    try:
        success = system.generate_and_run_test(description)
        
        if success:
            print("✅ 漏洞挖掘测试成功!")
            
            # 显示生成的测试代码关键部分
            from pathlib import Path
            test_file = Path(project_path) / "test" / "GorillaTest.t.sol"
            if test_file.exists():
                with open(test_file, 'r') as f:
                    content = f.read()
                    # 查找testLogic部分
                    if "_test" in content:
                        print("🎉 成功生成了漏洞利用代码!")
                    else:
                        print("⚠️ 可能没有生成有效的漏洞利用代码")
        else:
            print("❌ 测试失败")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()


