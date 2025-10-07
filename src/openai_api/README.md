# OpenAI API Component

## Overview

The OpenAI API component provides integration with OpenAI's language models for the Finite Monkey Engine. It handles API calls, model management, and response processing for vulnerability analysis and code understanding.

## Features

- **OpenAI Integration**: Direct integration with OpenAI API
- **Model Management**: Flexible model selection and configuration
- **Response Processing**: Structured response handling and parsing
- **Error Handling**: Comprehensive error handling and retry logic

## Architecture

### Core Components

- **OpenAI Client**: Main API client for OpenAI integration
- **Model Manager**: Model selection and configuration management
- **Response Processor**: Response parsing and validation
- **Error Handler**: Error handling and retry mechanisms

### API Functions

The component provides several key functions:
- `ask_vul()`: Vulnerability analysis queries
- `ask_claude()`: General code analysis queries
- `ask_openai_for_json()`: Structured JSON responses
- `common_get_embedding()`: Text embedding generation

## Usage

### Basic API Usage

```python
from openai_api.openai import ask_vul, ask_claude

# Vulnerability analysis
vul_response = ask_vul(prompt="Analyze this smart contract for vulnerabilities")

# General code analysis
analysis_response = ask_claude(prompt="Explain this function's purpose")
```

### Embedding Generation

```python
from openai_api.openai import common_get_embedding

# Generate embeddings for text
embedding = common_get_embedding("function transfer() public { }")
print(f"Embedding dimension: {len(embedding)}")
```

### Structured Responses

```python
from openai_api.openai import ask_openai_for_json

# Get structured JSON response
json_response = ask_openai_for_json(
    prompt="Analyze this code and return results as JSON",
    expected_structure={"vulnerabilities": [], "severity": "string"}
)
```

## Integration

The OpenAI API component integrates with:

- **Planning Module**: Provides AI-powered task planning
- **Validation Module**: Enhances vulnerability analysis with AI
- **Context Component**: Generates embeddings for RAG
- **Reasoning Module**: Powers intelligent code reasoning

## Configuration

### Environment Variables

```python
# Required environment variables
OPENAI_API_KEY = "your-openai-api-key"

# Optional configuration
OPENAI_MODEL = "gpt-4"  # Default model
EMBEDDING_MODEL = "text-embedding-3-small"  # Embedding model
MAX_TOKENS = 4000  # Maximum tokens per request
TEMPERATURE = 0.1  # Response creativity (0.0-1.0)
```

### Model Configuration

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

- **Response Speed**: Optimized API calls for fast responses
- **Token Efficiency**: Efficient token usage and management
- **Rate Limiting**: Intelligent rate limiting and retry logic
- **Caching**: Response caching for improved performance

## Dependencies

- `openai`: Official OpenAI Python client
- `requests`: HTTP client for API calls
- `json`: For response parsing
- `typing`: For type hints

## Development

### Adding New Models

1. Update model configuration
2. Implement model-specific logic
3. Add response processing
4. Update documentation

### Extending API Functions

1. Define new API function
2. Implement error handling
3. Add response validation
4. Update integration points

## API Reference

### ask_vul Function

```python
def ask_vul(prompt: str, model: str = "gpt-4") -> str:
    """Send vulnerability analysis query to OpenAI"""
    pass
```

#### Parameters

- `prompt`: Analysis prompt
- `model`: OpenAI model to use (default: gpt-4)

#### Returns

- `str`: AI response for vulnerability analysis

### ask_claude Function

```python
def ask_claude(prompt: str, model: str = "gpt-4") -> str:
    """Send general analysis query to OpenAI"""
    pass
```

### common_get_embedding Function

```python
def common_get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Generate embedding for text"""
    pass
```

#### Parameters

- `text`: Text to embed
- `model`: Embedding model to use

#### Returns

- `List[float]`: Text embedding vector

### ask_openai_for_json Function

```python
def ask_openai_for_json(prompt: str, expected_structure: Dict) -> Dict:
    """Get structured JSON response from OpenAI"""
    pass
```

## Error Handling

The component includes comprehensive error handling for:
- API rate limiting
- Network failures
- Invalid responses
- Token limit exceeded
- Authentication errors

## Rate Limiting

- **Automatic Retry**: Automatic retry with exponential backoff
- **Rate Limit Detection**: Intelligent rate limit detection
- **Request Queuing**: Request queuing for high-load scenarios
- **Fallback Models**: Fallback to alternative models when needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## License

This component is part of the Finite Monkey Engine project and follows the same licensing terms. 