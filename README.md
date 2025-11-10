# Gorilla - LLM-Powered Smart Contract Testing System

Gorilla is an automated smart contract testing system that leverages Large Language Models (LLMs) to dynamically generate formal specifications, detect vulnerabilities, and create comprehensive test suites.

## Features

- 🧠 **Dynamic Specification Generation**: Automatically generates formal specifications and invariants using LLMs
- 🔍 **Vulnerability Detection**: Identifies security issues including access control flaws, reentrancy, and more
- 🧪 **Automated Test Generation**: Creates complete Foundry test suites from natural language descriptions
- 🔧 **Auto-Fix**: Automatically repairs compilation and runtime errors in generated tests
- ⚡ **Foundry Integration**: Seamlessly integrates with the Foundry development framework

## Prerequisites

### 1. Install Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Verify installation:
```bash
forge --version
```

### 2. Install Python Dependencies

```bash
cd /Users/xueyue/Desktop/projects/Gorilla
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: custom endpoint
```

## Testing Modes

Gorilla supports three primary testing modes, each designed for different use cases:

### Mode 1: Quick Demo (Basic Test Generation)

**File**: `run_demo.py`

**Purpose**: Demonstrates basic test generation and execution with a simple ERC20 token transfer test.

**Usage**:
```bash
cd /Users/xueyue/Desktop/projects/Gorilla
source venv/bin/activate
python run_demo.py
```

**What it does**:
- Generates a basic ERC20 token transfer test
- Executes the test using Foundry
- Displays the generated test file
- Shows test results

**Best for**: Quick validation that the system is working correctly.

---

### Mode 2: Dynamic Specification Testing (Advanced)

**File**: `dynamic_test.py`

**Purpose**: Fully dynamic vulnerability exploration with LLM-generated specifications, invariants, and test logic.

**Usage**:
```bash
cd /Users/xueyue/Desktop/projects/Gorilla
source venv/bin/activate
python dynamic_test.py
```

**What it does**:
- Runs three comprehensive test scenarios:
  1. **Dynamic Exploit Test**: Analyzes mint function access control vulnerabilities
  2. **Dynamic Spec Violation Detection**: Generates formal specifications and detects violations
  3. **Dynamic Allowance Test**: Detects allowance mechanism vulnerabilities
- Generates formal specifications dynamically for each scenario
- Creates violation checks based on generated invariants
- Executes tests and reports results

**Test cases included**:

```python
# Test 1: Dynamic Exploit Test
"Analyze the mint function of an ERC20 contract, find access control vulnerabilities, and exploit them"

# Test 2: Dynamic Spec Violation Detection  
"Generate formal specifications for an ERC20 contract and detect whether the mint function violates access control invariants"

# Test 3: Dynamic Allowance Test
"Analyze the implementation of transferFrom and detect potential allowance mechanism vulnerabilities"
```

**Best for**: 
- Comprehensive security analysis
- Exploring unknown vulnerabilities
- Validating formal specifications
- Research and development

---

### Mode 3: Custom Test Generation (CLI)

**File**: `src/main.py`

**Purpose**: Generate and execute custom tests from command-line descriptions.

**Usage**:
```bash
cd /Users/xueyue/Desktop/projects/Gorilla
source venv/bin/activate
python -m src.main <project_path> "<test_description>"
```

**Examples**:

1. **Basic Transfer Test**:
```bash
python -m src.main ./test-project "Test the basic ERC20 token transfer function"
```

2. **Access Control Test**:
```bash
python -m src.main ./test-project "Test that only the owner can mint tokens"
```

3. **Reentrancy Test**:
```bash
python -m src.main ./test-project "Test the contract for reentrancy vulnerabilities in the withdraw function"
```

4. **Allowance Test**:
```bash
python -m src.main ./test-project "Test the approve and transferFrom mechanism for proper allowance handling"
```

5. **Complex Scenario**:
```bash
python -m src.main ./test-project "Deploy an ERC20 token, mint tokens to multiple users, test transfers between them, and verify balances are correct"
```

**Best for**: 
- Custom test scenarios
- Integration into CI/CD pipelines
- Scripting and automation
- Specific vulnerability testing

---

## System Architecture

### Core Components

1. **DynamicSpecGenerator** (`src/dynamic_spec_generator.py`)
   - Generates formal specifications from contract code
   - Creates invariants, pre-conditions, post-conditions, and safety properties
   - Produces test logic for vulnerability detection

2. **SpecViolationDetector** (`src/spec_violation_detector.py`)
   - Detects specification violations in smart contracts
   - Checks for common vulnerability patterns
   - Validates against dynamically generated invariants

3. **DynamicTestGenerator** (`src/dynamic_test_generator.py`)
   - Generates complete Foundry test files from descriptions
   - Integrates formal specifications into tests
   - Creates comprehensive test logic

4. **ForgeExecutor** (`src/forge_executor.py`)
   - Manages Foundry project initialization
   - Compiles and executes tests
   - Captures and parses test results

5. **AutoFixer** (`src/auto_fixer.py`)
   - Automatically fixes compilation errors
   - Repairs runtime test failures
   - Iteratively improves generated code

### Workflow

```
User Description
      ↓
Dynamic Spec Generation
      ↓
Formal Specifications (Invariants, Safety Properties)
      ↓
Test Code Generation
      ↓
Foundry Execution
      ↓
Auto-Fix (if errors)
      ↓
Test Results
```

## Generated Specifications

The system generates four types of formal specifications:

### 1. Invariants
Properties that must always hold:
```solidity
// Example: Balance non-negativity
balanceOf(account) >= 0
```

### 2. Pre-conditions
Requirements before function execution:
```solidity
// Example: Transfer pre-condition
require(balanceOf(from) >= amount)
```

### 3. Post-conditions
Expected state after function execution:
```solidity
// Example: Transfer post-condition
balanceOf(to) == oldBalance + amount
```

### 4. Safety Properties
Security rules that must not be violated:
```solidity
// Example: Access control
Only authorized users can mint tokens
```

## Test Output Structure

Generated tests are saved to:
```
test-project/test/GorillaTest.t.sol
```

Test structure:
```solidity
contract GorillaTest is Test {
    // Contract instances
    SimpleERC20 public token;
    
    // Test accounts
    address owner = address(0x1);
    address user1 = address(0x2);
    address attacker = address(0x3);
    
    function setUp() public {
        // Initialization
    }
    
    function testVulnerability() public {
        // Test logic
        // Specification violation checks
        // Attack verification
    }
}
```

## Supported Vulnerability Types

- **Access Control**: Unauthorized function access (e.g., unprotected mint)
- **Reentrancy**: External call ordering issues
- **Integer Overflow/Underflow**: Arithmetic safety
- **Allowance Bypass**: ERC20 allowance mechanism flaws
- **Zero Address Checks**: Missing address validation
- **Custom**: Any vulnerability describable in natural language

## Advanced Usage

### Customizing Test Generation

Edit test descriptions to focus on specific aspects:

```bash
# Focus on edge cases
python -m src.main ./test-project "Test ERC20 transfer with zero amount and zero address"

# Focus on gas optimization
python -m src.main ./test-project "Test gas consumption of batch transfer operations"

# Focus on events
python -m src.main ./test-project "Verify that Transfer events are emitted correctly"
```

### Analyzing Custom Contracts

1. Add your contract to `test-project/src/`
2. Run dynamic testing:
```bash
python dynamic_test.py
```

3. Or use custom mode:
```bash
python -m src.main ./test-project "Test [YourContract] for [specific vulnerability]"
```

### Batch Testing

Create a script for multiple test scenarios:

```bash
#!/bin/bash
cd /Users/xueyue/Desktop/projects/Gorilla
source venv/bin/activate

python -m src.main ./test-project "Test 1 description"
python -m src.main ./test-project "Test 2 description"
python -m src.main ./test-project "Test 3 description"
```

## Troubleshooting

### Common Issues

1. **Foundry not found**
   ```bash
   # Reinstall Foundry
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **API Key not configured**
   ```bash
   # Check .env file exists and contains:
   OPENAI_API_KEY=your_key_here
   ```

3. **Module not found**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Test compilation fails**
   - The system will attempt auto-fix (up to 3 attempts)
   - Check `test-project/test/GorillaTest.t.sol` for errors
   - Verify contract exists in `test-project/src/`

### Debug Mode

Enable verbose output by checking console logs during execution. Each component prints detailed information:

- 🧠 LLM generation steps
- 📝 Generated specifications
- 🔧 Auto-fix attempts
- ✅ Test results

## Project Structure

```
Gorilla/
├── src/
│   ├── main.py                      # Main entry point
│   ├── dynamic_spec_generator.py    # Specification generation
│   ├── spec_violation_detector.py   # Violation detection
│   ├── dynamic_test_generator.py    # Test generation
│   ├── forge_executor.py            # Foundry integration
│   ├── auto_fixer.py                # Auto-repair system
│   └── openai_api/                  # OpenAI API wrapper
├── test-project/                    # Foundry project
│   ├── src/                         # Smart contracts
│   ├── test/                        # Generated tests
│   └── foundry.toml                 # Foundry config
├── run_demo.py                      # Mode 1: Quick demo
├── dynamic_test.py                  # Mode 2: Dynamic testing
├── requirements.txt                 # Python dependencies
└── .env                             # API configuration
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional vulnerability patterns
- Support for more contract standards (ERC721, ERC1155, etc.)
- Enhanced specification generation
- Performance optimizations
- Additional auto-fix strategies

## License

[Add your license here]

## Citation

If you use Gorilla in your research, please cite:

```bibtex
[Add citation information]
```

## Contact

[Add contact information]

