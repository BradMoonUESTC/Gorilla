# OpenAI API 组件

## 概述

OpenAI API 组件为 Finite Monkey Engine 提供与 OpenAI 语言模型的集成。它处理 API 调用、模型管理和响应处理，用于漏洞分析和代码理解。

## 功能特性

- **OpenAI 集成**: 直接集成 OpenAI API
- **模型管理**: 灵活的模型选择和配置
- **响应处理**: 结构化响应处理和解析
- **错误处理**: 全面的错误处理和重试逻辑

## 架构

### 核心组件

- **OpenAI 客户端**: OpenAI 集成的主 API 客户端
- **模型管理器**: 模型选择和配置管理
- **响应处理器**: 响应解析和验证
- **错误处理器**: 错误处理和重试机制

### API 函数

组件提供几个关键函数：
- `ask_vul()`: 漏洞分析查询
- `ask_claude()`: 通用代码分析查询
- `ask_openai_for_json()`: 结构化 JSON 响应
- `common_get_embedding()`: 文本嵌入生成

## 使用方法

### 基本 API 使用

```python
from openai_api.openai import ask_vul, ask_claude

# 漏洞分析
vul_response = ask_vul(prompt="分析这个智能合约的漏洞")

# 通用代码分析
analysis_response = ask_claude(prompt="解释这个函数的用途")
```

### 嵌入生成

```python
from openai_api.openai import common_get_embedding

# 为文本生成嵌入
embedding = common_get_embedding("function transfer() public { }")
print(f"嵌入维度: {len(embedding)}")
```

### 结构化响应

```python
from openai_api.openai import ask_openai_for_json

# 获取结构化 JSON 响应
json_response = ask_openai_for_json(
    prompt="分析这段代码并以 JSON 格式返回结果",
    expected_structure={"vulnerabilities": [], "severity": "string"}
)
```

## 集成

OpenAI API 组件与以下模块集成：

- **规划模块**: 提供 AI 驱动的任务规划
- **验证模块**: 用 AI 增强漏洞分析
- **上下文组件**: 为 RAG 生成嵌入
- **推理模块**: 为智能代码推理提供动力

## 配置

### 环境变量

```python
# 必需的环境变量
OPENAI_API_KEY = "your-openai-api-key"

# 可选配置
OPENAI_MODEL = "gpt-4"  # 默认模型
EMBEDDING_MODEL = "text-embedding-3-small"  # 嵌入模型
MAX_TOKENS = 4000  # 每次请求的最大令牌数
TEMPERATURE = 0.1  # 响应创造性 (0.0-1.0)
```

### 模型配置

```python
# 模型配置文件
MODEL_CONFIG = {
    "gpt-4": {
        "max_tokens": 4000,
        "temperature": 0.1
    },
    "gpt-3.5-turbo": {
        "max_tokens": 2000,
        "temperature": 0.1
    }
}
```

## 性能

- **响应速度**: 优化的 API 调用以实现快速响应
- **令牌效率**: 高效的令牌使用和管理
- **速率限制**: 智能速率限制和重试逻辑
- **缓存**: 响应缓存以提高性能

## 依赖

- `openai`: 官方 OpenAI Python 客户端
- `requests`: API 调用的 HTTP 客户端
- `json`: 用于响应解析
- `typing`: 用于类型提示

## 开发

### 添加新模型

1. 更新模型配置
2. 实现模型特定逻辑
3. 添加响应处理
4. 更新文档

### 扩展 API 函数

1. 定义新的 API 函数
2. 实现错误处理
3. 添加响应验证
4. 更新集成点

## API 参考

### ask_vul 函数

```python
def ask_vul(prompt: str, model: str = "gpt-4") -> str:
    """向 OpenAI 发送漏洞分析查询"""
    pass
```

#### 参数

- `prompt`: 分析提示
- `model`: 要使用的 OpenAI 模型（默认：gpt-4）

#### 返回值

- `str`: 漏洞分析的 AI 响应

### ask_claude 函数

```python
def ask_claude(prompt: str, model: str = "gpt-4") -> str:
    """向 OpenAI 发送通用分析查询"""
    pass
```

### common_get_embedding 函数

```python
def common_get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """为文本生成嵌入"""
    pass
```

#### 参数

- `text`: 要嵌入的文本
- `model`: 要使用的嵌入模型

#### 返回值

- `List[float]`: 文本嵌入向量

### ask_openai_for_json 函数

```python
def ask_openai_for_json(prompt: str, expected_structure: Dict) -> Dict:
    """从 OpenAI 获取结构化 JSON 响应"""
    pass
```

## 错误处理

组件包含全面的错误处理：
- API 速率限制
- 网络失败
- 无效响应
- 令牌限制超出
- 身份验证错误

## 速率限制

- **自动重试**: 使用指数退避的自动重试
- **速率限制检测**: 智能速率限制检测
- **请求队列**: 高负载场景的请求队列
- **备用模型**: 需要时回退到替代模型

## 贡献

1. Fork 仓库
2. 创建功能分支
3. 实现您的更改
4. 添加测试和文档
5. 提交拉取请求

## 许可证

本组件是 Finite Monkey Engine 项目的一部分，遵循相同的许可条款。 