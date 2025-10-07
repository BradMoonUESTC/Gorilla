"""
主程序 - Gorilla测试生成和执行系统
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from dynamic_test_generator import DynamicTestGenerator
from forge_executor import ForgeExecutor
from auto_fixer import AutoFixer


class GorillaTestSystem:
    """Gorilla测试系统主类"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.test_generator = DynamicTestGenerator(project_path)
        self.forge_executor = ForgeExecutor(project_path)
        self.auto_fixer = AutoFixer(project_path=project_path)
        
    def generate_and_run_test(self, description: str) -> bool:
        """生成并运行测试的完整流程"""
        
        print(f"🚀 开始处理测试需求: {description}")
        
        # 1. 检查环境
        if not self._check_environment():
            return False
            
        # 2. 生成初始测试代码
        print("📝 生成测试代码...")
        test_code = self.test_generator.generate_test_from_description(description)
        if not test_code:
            print("❌ 测试代码生成失败")
            return False
        
        # 3. 执行测试并自动修复
        max_fix_attempts = 3
        for attempt in range(max_fix_attempts + 1):
            
            if attempt == 0:
                print("🧪 执行初始测试...")
            else:
                print(f"🔧 执行修复后的测试 (第{attempt}次修复)")
                
            # 执行测试
            success, output = self.forge_executor.write_and_run_test(test_code)
            
            if success:
                print("🎉 测试执行成功!")
                print("测试输出:")
                print(output)
                return True
            else:
                print(f"❌ 测试失败 (尝试 {attempt + 1}/{max_fix_attempts + 1})")
                print("错误输出:")
                print(output)
                
                # 如果不是最后一次尝试，进行自动修复
                if attempt < max_fix_attempts:
                    print("🔧 开始自动修复...")
                    fixed_code, fix_success = self.auto_fixer.fix_test_code(
                        test_code, output, description
                    )
                    
                    if fix_success:
                        test_code = fixed_code
                        print("✅ 代码修复完成，重新测试...")
                    else:
                        print("❌ 自动修复失败")
                        break
        
        print("❌ 测试最终失败，已达到最大重试次数")
        return False
    
    def _check_environment(self) -> bool:
        """检查运行环境"""
        
        # 检查项目路径
        if not Path(self.project_path).exists():
            print(f"❌ 项目路径不存在: {self.project_path}")
            return False
            
        # 检查Foundry安装
        if not self.forge_executor.check_foundry_installation():
            print("❌ Foundry未安装，请先安装Foundry")
            print("安装命令: curl -L https://foundry.paradigm.xyz | bash")
            return False
            
        # 检查或初始化Foundry项目
        if not self.forge_executor.initialize_foundry_project():
            print("❌ Foundry项目初始化失败")
            return False
            
        # 检查基础模板
        template_path = Path(self.project_path) / "test" / "GorillaBase.t.sol"
        if not template_path.exists():
            print(f"❌ 基础模板文件不存在: {template_path}")
            print("请创建基础模板文件")
            return False
            
        return True


def main():
    """主函数"""
    
    # 加载环境变量
    load_dotenv()
    
    if len(sys.argv) < 3:
        print("用法: python main.py <项目路径> <测试描述>")
        print("示例: python main.py ./test-project '测试ERC20代币的转账功能'")
        return
    
    project_path = sys.argv[1]
    description = sys.argv[2]
    
    # 创建测试系统
    system = GorillaTestSystem(project_path)
    
    # 执行测试
    success = system.generate_and_run_test(description)
    
    if success:
        print("🎉 测试流程完成!")
        sys.exit(0)
    else:
        print("❌ 测试流程失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
