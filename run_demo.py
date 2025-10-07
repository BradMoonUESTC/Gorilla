#!/usr/bin/env python3
"""
自动演示脚本 - 直接运行一个测试用例
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem


def main():
    """自动演示"""
    
    print("🚀 Gorilla测试系统自动演示")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    print(f"📁 项目路径: {project_path}")
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 简单的测试用例
    description = "测试ERC20代币的基本转账功能，创建代币合约，给用户分配代币，然后测试从一个地址向另一个地址转账"
    
    print(f"\n🎯 测试描述: {description}")
    print("=" * 50)
    
    # 执行测试
    try:
        success = system.generate_and_run_test(description)
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 演示完成! 测试成功执行")
            
            # 显示生成的测试文件
            test_file = Path(project_path) / "test" / "GorillaTest.t.sol"
            if test_file.exists():
                print(f"\n📄 生成的测试文件: {test_file}")
                print("文件内容预览:")
                print("-" * 30)
                with open(test_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for i, line in enumerate(lines[:20], 1):  # 显示前20行
                        print(f"{i:2d}| {line}")
                    if len(lines) > 20:
                        print(f"... (还有 {len(lines) - 20} 行)")
        else:
            print("❌ 演示完成，但测试执行失败")
            
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
