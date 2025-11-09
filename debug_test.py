#!/usr/bin/env python3
"""
调试测试 - 查看LLM的完整交互过程
"""

import os
import sys
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import GorillaTestSystem

def main():
    """调试测试"""
    
    print("🐛 调试模式 - 查看LLM交互过程")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 设置项目路径
    project_path = os.path.join(os.path.dirname(__file__), 'test-project')
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 测试两种模式
    test_cases = [
        {
            "name": "直接漏洞利用模式",
            "description": "测试mint权限控制漏洞"
        },
        {
            "name": "规范违反检测模式", 
            "description": "检测mint函数是否违反权限控制的形式化规范"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 测试 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print("=" * 60)
        
        try:
            success = system.generate_and_run_test(test_case['description'])
            
            print("=" * 60)
            if success:
                print(f"✅ {test_case['name']} 执行成功")
            else:
                print(f"❌ {test_case['name']} 执行失败")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(test_cases):
            input(f"\n按Enter继续下一个测试...")

if __name__ == "__main__":
    main()




