"""
Forge Test Executor - Execute generated test files and process results
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple
from template_system import escape_ansi


class ForgeExecutor:
    """Forge test executor"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def write_and_run_test(self, test_code: str, test_name: str = "GorillaTest") -> Tuple[bool, str]:
        """Write the test file and run `forge test`"""
        
        # 1. Ensure the test directory exists
        test_dir = self.project_path / "test"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Write the test file
        test_file = test_dir / f"{test_name}.t.sol"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)
            print(f"✅ Test file written: {test_file}")
        except Exception as e:
            return False, f"Failed to write test file: {e}"
        
        # 3. Execute forge test
        return self._run_forge_test(test_name)
    
    def _run_forge_test(self, test_name: str) -> Tuple[bool, str]:
        """Execute the `forge test` command"""
        try:
            # Execute forge test command
            result = subprocess.run([
                "forge", "test", 
                "--match-contract", test_name,
                "-vvv"  # verbose output
            ], 
            cwd=self.project_path,
            capture_output=True,
            text=True,
            timeout=60  # 60-second timeout
            )
            
            # Strip ANSI escape sequences
            stdout = escape_ansi(result.stdout)
            stderr = escape_ansi(result.stderr)
            
            output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            
            # Check success
            success = result.returncode == 0 and "FAILED" not in stdout
            
            if success:
                print("✅ Test executed successfully!")
            else:
                print("❌ Test execution failed")
                
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Test execution timed out (60 seconds)"
        except FileNotFoundError:
            return False, "Command 'forge' not found. Please ensure Foundry is installed."
        except Exception as e:
            return False, f"An error occurred while executing tests: {e}"
    
    def check_foundry_installation(self) -> bool:
        """Check if Foundry is installed"""
        try:
            result = subprocess.run(["forge", "--version"], 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def initialize_foundry_project(self) -> bool:
        """Initialize a Foundry project if needed"""
        foundry_toml = self.project_path / "foundry.toml"
        
        if not foundry_toml.exists():
            try:
                # Run forge init
                subprocess.run(["forge", "init", "--no-git", "."], 
                             cwd=self.project_path,
                             check=True)
                print("✅ Foundry project initialized")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Foundry project initialization failed: {e}")
                return False
        
        return True
