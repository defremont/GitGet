# Contributing to Portfolio Generator

🎉 Thank you for your interest in contributing to Portfolio Generator! We welcome contributions from developers of all skill levels.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Architecture Guidelines](#architecture-guidelines)
- [Community](#community)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful, inclusive, and professional in all interactions.

### Our Standards

- **Be respectful**: Treat everyone with respect, regardless of their background or experience level
- **Be inclusive**: Welcome newcomers and help them get started
- **Be constructive**: Provide helpful feedback and suggestions
- **Be professional**: Keep discussions focused on the project and technical matters

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python development
- Familiarity with GitHub workflow

### Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/portfolio-generator.git
   cd portfolio-generator
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes** and test them
6. **Submit a pull request**

## Development Setup

### 1. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### 3. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys (for testing)
# At minimum, set one AI provider API key
export GEMINI_API_KEY="your_test_key"
```

### 4. Verify Installation

```bash
# Check configuration
python portfolio_generator_cli.py --check-config

# Run basic test
python portfolio_generator_cli.py --help
```

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🧪 **Tests**
- 🔧 **Code refactoring**
- 🎨 **UI/UX improvements**
- 🌐 **Translations**
- 📦 **Dependencies updates**

### Areas Where We Need Help

- **New AI Providers**: Implement support for additional AI services
- **Repository Platforms**: Add support for Bitbucket, Azure DevOps, etc.
- **Performance**: Optimize API calls and data processing
- **Testing**: Improve test coverage and add integration tests
- **Documentation**: Improve guides, add examples, create tutorials
- **CLI Enhancements**: Add new command-line features
- **Error Handling**: Improve error messages and recovery

## Coding Standards

### Python Code Style

We follow PEP 8 and use automated tools to ensure consistency:

```bash
# Format code with black
black src/ tests/

# Check linting with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Code Guidelines

1. **Follow the existing architecture patterns**
2. **Write clear, descriptive variable and function names**
3. **Add docstrings to all public methods and classes**
4. **Keep functions small and focused**
5. **Use type hints for better code clarity**
6. **Follow the Single Responsibility Principle**
7. **Write tests for new functionality**

### Example Code Structure

```python
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class ExampleProvider(ABC):
    """Abstract base class for example providers."""
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        """Initialize the provider.
        
        Args:
            api_key: API key for authentication
            config: Optional configuration dictionary
        """
        self.api_key = api_key
        self.config = config or {}
    
    @abstractmethod
    def process_data(self, data: List[Dict]) -> Dict:
        """Process data and return results.
        
        Args:
            data: List of data items to process
            
        Returns:
            Dictionary containing processed results
            
        Raises:
            ProviderError: If processing fails
        """
        pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_ai_providers.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

1. **Create test files** in the `tests/` directory
2. **Use descriptive test names** that explain what's being tested
3. **Test both success and failure cases**
4. **Mock external dependencies** (API calls, file systems)
5. **Keep tests independent** and isolated

### Test Structure Example

```python
import pytest
from unittest.mock import Mock, patch
from src.ai_providers import AnthropicProvider


class TestAnthropicProvider:
    """Tests for AnthropicProvider class."""
    
    def test_init_with_valid_api_key(self):
        """Test provider initialization with valid API key."""
        provider = AnthropicProvider("test-key")
        assert provider.api_key == "test-key"
    
    def test_init_with_invalid_api_key(self):
        """Test provider initialization with invalid API key."""
        with pytest.raises(ValueError):
            AnthropicProvider("")
    
    @patch('src.ai_providers.anthropic_provider.anthropic')
    def test_generate_summary_success(self, mock_anthropic):
        """Test successful summary generation."""
        # Setup mock
        mock_response = Mock()
        mock_response.content = [Mock(text="Test summary")]
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response
        
        # Test
        provider = AnthropicProvider("test-key")
        result = provider.generate_summary("Test prompt")
        
        # Assert
        assert result == "Test summary"
```

## Documentation

### Documentation Guidelines

1. **Keep documentation up to date** with code changes
2. **Write clear, concise explanations**
3. **Include examples** for complex features
4. **Use proper markdown formatting**
5. **Add diagrams** for architectural concepts

### Documentation Types

- **README.md**: Project overview and quick start
- **ARCHITECTURE.md**: Detailed architecture documentation
- **API Documentation**: Generated from docstrings
- **User Guides**: Step-by-step tutorials
- **Developer Guides**: Technical implementation details

## Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Run the test suite** and ensure all tests pass
3. **Update documentation** if needed
4. **Follow the coding standards**
5. **Write clear commit messages**

### Commit Message Format

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat(ai-providers): add support for Google Gemini
fix(github-manager): handle rate limiting correctly
docs(readme): update installation instructions
test(data-processor): add unit tests for clean_project_data
```

### Pull Request Template

When submitting a PR, please include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows the project's coding standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated checks** run on all PRs
2. **Code review** by maintainers
3. **Testing** in different environments
4. **Documentation review** if applicable
5. **Merge** after approval

## Issue Guidelines

### Bug Reports

When reporting bugs, please include:

- **Environment details** (Python version, OS, etc.)
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Error messages** or logs
- **Configuration details** (sanitized)

### Feature Requests

When suggesting features, please include:

- **Use case** description
- **Proposed solution** or approach
- **Alternative solutions** considered
- **Additional context** or examples

### Issue Templates

Use the provided issue templates when creating new issues:

- **Bug Report Template**
- **Feature Request Template**
- **Documentation Request Template**
- **Question Template**

## Architecture Guidelines

### Adding New AI Providers

1. **Create a new provider class** inheriting from `AIProvider`
2. **Implement required methods**: `generate_summary()`, `get_model_info()`
3. **Add error handling** with specific exceptions
4. **Update the factory** to support the new provider
5. **Add comprehensive tests**
6. **Update documentation**

### Adding New Repository Managers

1. **Create a new manager class** inheriting from `RepositoryManager`
2. **Implement required methods** for the platform's API
3. **Follow the existing patterns** for data processing
4. **Add platform-specific error handling**
5. **Test with various repository types**
6. **Update configuration management**

### Code Organization

- **Keep modules focused** on single responsibilities
- **Use dependency injection** for testability
- **Follow the existing directory structure**
- **Add appropriate imports** to `__init__.py` files
- **Maintain backward compatibility** when possible

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check existing documentation first
- **Code Review**: Learn from pull request reviews

### Recognition

We recognize contributors in several ways:

- **Contributors section** in README.md
- **Release notes** mention significant contributions
- **GitHub releases** highlight contributor achievements
- **Community shoutouts** for helpful contributions

### Becoming a Maintainer

Active contributors may be invited to become maintainers. Maintainers help with:

- **Code reviews** and pull request management
- **Issue triage** and community support
- **Release planning** and coordination
- **Architecture decisions** and technical direction

---

## Thank You!

Your contributions help make Portfolio Generator better for everyone. Whether you're fixing a typo, adding a feature, or helping other users, every contribution matters.

**Happy coding!** 🚀

---

## Quick Links

- [Project Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)
- [Issue Tracker](https://github.com/yourusername/portfolio-generator/issues)
- [Pull Requests](https://github.com/yourusername/portfolio-generator/pulls)
- [Releases](https://github.com/yourusername/portfolio-generator/releases)