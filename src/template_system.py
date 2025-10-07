"""
Solidity模板系统 - 基于技术方案文档实现
支持 //$variable 语法的模板变量替换
"""

import re
from string import Template
from pathlib import Path
from typing import Dict, Any


class SolidityTemplate(Template):
    """自定义模板类，使用 //$ 作为模板变量分隔符"""
    delimiter = "//$"  # 使用 //$ 作为模板变量分隔符


def read_base_template(project_path: str) -> str:
    """从项目中读取基础模板文件"""
    template_path = Path(project_path) / "test" / "GorillaBase.t.sol"
    
    if not template_path.exists():
        raise FileNotFoundError(f"基础模板文件未找到: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_code(template_code: str, variables: Dict[str, Any]) -> str:
    """使用模板变量生成测试代码"""
    template = SolidityTemplate(template_code)
    return template.substitute(variables)


def escape_ansi(text: str) -> str:
    """清理终端颜色代码，便于文本分析"""
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def create_default_template_variables() -> Dict[str, str]:
    """创建默认的模板变量"""
    return {
        "testLogic": "// Vulnerability test logic will be added here",
        "vulnerabilityAssertions": "// Vulnerability assertions will be added here"
    }
