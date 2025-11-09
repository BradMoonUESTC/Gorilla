"""
Solidity Template System - Implementation based on the technical design
Supports template variable replacement with the //$variable syntax
"""

import re
from string import Template
from pathlib import Path
from typing import Dict, Any


class SolidityTemplate(Template):
    """Custom template class using //$ as the template variable delimiter"""
    delimiter = "//$"  # Use //$ as the template variable delimiter


def read_base_template(project_path: str) -> str:
    """Read the base template file from the project"""
    template_path = Path(project_path) / "test" / "GorillaBase.t.sol"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Base template file not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_code(template_code: str, variables: Dict[str, Any]) -> str:
    """Generate test code using template variables"""
    template = SolidityTemplate(template_code)
    return template.substitute(variables)


def escape_ansi(text: str) -> str:
    """Remove ANSI color codes to facilitate text analysis"""
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def create_default_template_variables() -> Dict[str, str]:
    """Create default template variables"""
    return {
        "testLogic": "// Vulnerability test logic will be added here",
        "vulnerabilityAssertions": "// Vulnerability assertions will be added here"
    }
