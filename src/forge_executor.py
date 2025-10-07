"""
Forge测试执行器 - 执行生成的测试文件并处理结果
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple
from template_system import escape_ansi


class ForgeExecutor:
    """Forge测试执行器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def write_and_run_test(self, test_code: str, test_name: str = "GorillaTest") -> Tuple[bool, str]:
        """写入测试文件并执行forge test"""
        
        # 1. 确保测试目录存在
        test_dir = self.project_path / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. 写入测试文件
        test_file = test_dir / f"{test_name}.t.sol"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)
            print(f"✅ 测试文件已写入: {test_file}")
        except Exception as e:
            return False, f"写入测试文件失败: {e}"
        
        # 3. 执行forge test
        return self._run_forge_test(test_name)
    
    def _run_forge_test(self, test_name: str) -> Tuple[bool, str]:
        """执行forge test命令"""
        try:
            # 执行forge test命令
            result = subprocess.run([
                "forge", "test", 
                "--match-contract", test_name,
                "-vvv"  # 详细输出
            ], 
            cwd=self.project_path,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
            )
            
            # 清理ANSI转义序列
            stdout = escape_ansi(result.stdout)
            stderr = escape_ansi(result.stderr)
            
            output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            
            # 检查是否成功
            success = result.returncode == 0 and "FAILED" not in stdout
            
            if success:
                print("✅ 测试执行成功!")
            else:
                print("❌ 测试执行失败")
                
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "测试执行超时 (60秒)"
        except FileNotFoundError:
            return False, "forge命令未找到，请确保已安装Foundry"
        except Exception as e:
            return False, f"执行测试时发生错误: {e}"
    
    def check_foundry_installation(self) -> bool:
        """检查Foundry是否已安装"""
        try:
            result = subprocess.run(["forge", "--version"], 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def initialize_foundry_project(self) -> bool:
        """初始化Foundry项目（如果需要）"""
        foundry_toml = self.project_path / "foundry.toml"
        
        if not foundry_toml.exists():
            try:
                # 运行forge init
                subprocess.run(["forge", "init", "--no-git", "."], 
                             cwd=self.project_path,
                             check=True)
                print("✅ Foundry项目初始化完成")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Foundry项目初始化失败: {e}")
                return False
        
        return True
