# OpenAI API Component

## Overview

The OpenAI API component provides integration with OpenAI language models for the Finite Monkey Engine. It handles API calls, model management, and response processing for vulnerability analysis and code understanding.

## Features

- OpenAI integration: Direct integration with the OpenAI API
- Model management: Flexible model selection and configuration
- Response handling: Structured response processing and parsing
- Error handling: Comprehensive error handling and retry logic

## Architecture

### Core Components

- OpenAI client: Primary API client for OpenAI integration
- Model manager: Model selection and configuration
- Response processor: Response parsing and validation
- Error handler: Error handling and retry mechanisms

### API Functions

This component exposes several key functions:
- `ask_vul()`: Vulnerability analysis queries
- `ask_claude()`: General code analysis queries
- `ask_openai_for_json()`: Structured JSON responses
- `common_get_embedding()`: Text embedding generation

## Usage

### Basic API Usage

```python
from openai_api.openai import ask_vul, ask_claude

# Vulnerability analysis
vul_response = ask_vul(prompt="Analyze vulnerabilities in this smart contract")

# General code analysis
analysis_response = ask_claude(prompt="Explain what this function does")
```

### Embedding Generation

```python
from openai_api.openai import common_get_embedding

# Generate an embedding for text
embedding = common_get_embedding("function transfer() public { }")
print(f"Embedding dimension: {len(embedding)}")
```

### Structured Response

```python
from openai_api.openai import ask_openai_for_json

# Get a structured JSON response
json_response = ask_openai_for_json(
    prompt="Analyze this code and return the result in JSON",
    expected_structure={"vulnerabilities": [], "severity": "string"}
)
```

## Integration

The OpenAI API component integrates with the following modules:

- Planning: AI-driven task planning
- Verification: AI-assisted vulnerability analysis
- Context: Embedding generation for RAG
- Reasoning: Powering intelligent code reasoning

## Configuration

### Environment Variables

```python
# Required
OPENAI_API_KEY = "your-openai-api-key"

# Optional
OPENAI_MODEL = "gpt-4"  # Default model
EMBEDDING_MODEL = "text-embedding-3-small"  # Embedding model
MAX_TOKENS = 4000  # Max tokens per request
TEMPERATURE = 0.1  # Creativity (0.0-1.0)
```

### Model Config

```python
# Model configuration file
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

## Performance

- Response speed: Optimized API calls for fast responses
- Token efficiency: Efficient token usage and management
- Rate limiting: Smart rate limiting with retries
- Caching: Response caching to improve performance

## Dependencies

- `openai`: Official OpenAI Python client
- `requests`: HTTP client for API calls
- `json`: Response parsing
- `typing`: Type hints

## Development

### Add a New Model

1. Update model configuration
2. Implement model-specific logic
3. Add response handling
4. Update documentation

### Extend API Functions

1. Define a new API function
2. Implement error handling
3. Add response validation
4. Update integration points

## API Reference

### ask_vul

```python
def ask_vul(prompt: str, model: str = "gpt-4") -> str:
    """Send a vulnerability analysis query to OpenAI"""
    pass
```

#### Parameters

- `prompt`: The analysis prompt
- `model`: The OpenAI model to use (default: gpt-4)

#### Returns

- `str`: AI response for vulnerability analysis

### ask_claude

```python
def ask_claude(prompt: str, model: str = "gpt-4") -> str:
    """Send a general analysis query to OpenAI"""
    pass
```

### common_get_embedding

```python
def common_get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Generate an embedding for text"""
    pass
```

#### Parameters

- `text`: The text to embed
+- `model`: The embedding model to use

#### Returns

- `List[float]`: The text embedding vector

### ask_openai_for_json

```python
def ask_openai_for_json(prompt: str, expected_structure: Dict) -> Dict:
    """Get a structured JSON response from OpenAI"""
    pass
```

## Error Handling

The component includes comprehensive error handling:
- API rate limits
- Network failures
- Invalid responses
- Token limit exceeded
- Authentication errors

## Rate Limiting

- Automatic retries with exponential backoff
- Intelligent rate-limit detection
- Request queuing for high-load scenarios
- Fallback models when needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and docs
5. Submit a pull request

## License

This component is part of the Finite Monkey Engine project and follows the same license terms.