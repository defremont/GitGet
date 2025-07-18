# Portfolio Generator

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/yourusername/portfolio-generator/releases)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/portfolio-generator/actions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful, modular Python application that analyzes your GitHub and GitLab repositories to generate comprehensive portfolio summaries using multiple AI providers. Built with clean architecture principles for maintainability and extensibility.

🌟 **NEW in v2.0.0**: Complete architectural refactor with modular design, improved error handling, and professional CLI interface!

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key (get one from https://aistudio.google.com/)
export GEMINI_API_KEY="your_gemini_api_key"

# Check configuration
python portfolio_generator_cli.py --check-config

# Generate portfolio with default settings (Google Gemini)
python portfolio_generator_cli.py

# Generate with specific AI provider
python portfolio_generator_cli.py --model-provider anthropic --model-name claude-3-5-haiku-latest
```
<img width="1000" height="557" alt="image" src="https://github.com/user-attachments/assets/71b107ad-ee6c-4c4f-9974-caf6ab70c8da" />

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [AI Models & Providers](#-ai-models--providers)
- [API Setup](#-api-setup)
- [Output](#-output)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Functionality
- **Multi-platform support**: GitHub and GitLab (including self-hosted)
- **Comprehensive analysis**: Public and private repositories
- **Smart filtering**: Configurable commit thresholds and project selection
- **Rate limiting**: Automatic handling with intelligent delays
- **Stage-based execution**: Separate data collection and analysis phases

### 🤖 AI-Powered Analysis
- **Multiple AI providers**: Anthropic Claude, OpenAI GPT, Google Gemini
- **Professional summaries**: Detailed portfolio analysis and recommendations
- **Top project highlights**: AI-identified most significant projects
- **Code metrics**: Estimated lines of code across all projects
- **Interview preparation**: Generated talking points and project highlights

### 🏗️ Architecture
- **Modular design**: Clean separation of concerns
- **Extensible**: Easy to add new AI providers or repository platforms
- **Testable**: Comprehensive error handling and logging
- **Professional CLI**: Rich help system and configuration validation

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
# Clone the repository
git clone https://github.com/yourusername/portfolio-generator.git
cd portfolio-generator

# Install core dependencies
pip install -r requirements.txt

# Optional: Install specific AI providers
pip install anthropic          # For Anthropic Claude
pip install openai            # For OpenAI GPT
pip install google-generativeai  # For Google Gemini
```

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## ⚙️ Configuration

### Environment Variables

Set up your API keys and tokens:

```bash
# AI Provider API Keys (at least one required)
export GEMINI_API_KEY="your_gemini_api_key"          # Google Gemini (recommended - free)
export ANTHROPIC_API_KEY="your_anthropic_api_key"    # Anthropic Claude (paid)
export OPENAI_API_KEY="your_openai_api_key"          # OpenAI GPT (paid/free tiers)

# Repository tokens (optional - for private repos and higher rate limits)
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"

# Optional GitLab configuration
export GITLAB_URL="https://your-gitlab-instance.com"  # For self-hosted GitLab
```

### Configuration Check
```bash
# Verify your configuration
python portfolio_generator_cli.py --check-config
```

## 🎮 Usage

### Basic Usage

```bash
# Generate portfolio with default settings
python portfolio_generator_cli.py

# Use specific usernames (for public repos)
python portfolio_generator_cli.py --github-username myuser --gitlab-username myuser

# Use existing data to regenerate summary
python portfolio_generator_cli.py --use-existing
```

### Advanced Usage

```bash
# Use specific AI provider and model
python portfolio_generator_cli.py --model-provider anthropic --model-name claude-3-5-sonnet-latest

# Analyze only GitHub repositories with limits
python portfolio_generator_cli.py --platform github --max-commits 50 --min-commits 5

# Run only data collection (Stage 1)
python portfolio_generator_cli.py --stage 1

# Run only analysis (Stage 2)
python portfolio_generator_cli.py --stage 2

# Enable debug mode
python portfolio_generator_cli.py --debug
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--github-username` | GitHub username (optional if using token) | None |
| `--gitlab-username` | GitLab username (optional if using token) | None |
| `--platform` | Analyze only specific platform (`github` or `gitlab`) | Both |
| `--use-existing` | Use most recent data file instead of fetching new | False |
| `--stage` | Run specific stage: `1`=data collection, `2`=analysis | Both |
| `--min-commits` | Minimum user commits required for inclusion | 1 |
| `--max-commits` | Maximum commits per project in JSON | All |
| `--model-provider` | AI provider: `anthropic`, `openai`, `google` | `google` |
| `--model-name` | Specific model name | Provider default |
| `--debug` | Enable debug logging | False |
| `--check-config` | Check configuration and exit | False |

## 🏗️ Architecture

The application follows a clean, modular architecture:

```
src/
├── ai_providers/           # AI provider implementations
│   ├── anthropic_provider.py
│   ├── openai_provider.py
│   ├── gemini_provider.py
│   └── factory.py
├── repository_managers/    # Repository platform handlers
│   ├── github_manager.py
│   └── gitlab_manager.py
├── config/                 # Configuration management
│   ├── config_manager.py
│   └── portfolio_config.py
├── utils/                  # Utility functions
│   ├── file_analyzer.py
│   ├── data_processor.py
│   └── logger.py
└── portfolio_generator.py  # Main application
```

### Key Design Principles
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code
- **Dependency Inversion**: High-level modules depend on abstractions
- **Error Handling**: Comprehensive exception handling and logging

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🤖 AI Models & Providers

### 🎯 Recommended Models

| Provider | Model | Cost | Reasoning | Best For |
|----------|-------|------|-----------|----------|
| **Google** | `gemini-2.5-pro` | ✅ Free | ❌ No | **Default choice** - Excellent free analysis |
| **Google** | `gemini-2.5-flash` | ✅ Free | ❌ No | Fastest option |
| **Anthropic** | `claude-3-5-sonnet-latest` | 💰 Paid | ❌ No | High-quality analysis |
| **Anthropic** | `claude-3-5-haiku-latest` | 💰 Paid | ❌ No | Cheaper Claude option |
| **OpenAI** | `gpt-4.1-nano` | 🆓 Free tier | ❌ No | Good free option |
| **OpenAI** | `o4-mini` | 💰 Paid | ✅ Yes | Reasoning capabilities |

### Quick Start Recommendations

**For beginners or cost-conscious users:**
```bash
python portfolio_generator_cli.py  # Uses free Gemini 2.5 Pro
```

**For premium quality:**
```bash
python portfolio_generator_cli.py --model-provider anthropic --model-name claude-3-5-sonnet-latest
```

**For fastest results:**
```bash
python portfolio_generator_cli.py --model-provider google --model-name gemini-2.5-flash
```

## 🔑 API Setup

### Google Gemini (Recommended)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Set as `GEMINI_API_KEY` environment variable

### Anthropic Claude
1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Generate an API key
3. Set as `ANTHROPIC_API_KEY` environment variable

### OpenAI GPT
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key
3. Set as `OPENAI_API_KEY` environment variable

### GitHub Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate token with `repo` scope (or `public_repo` for public only)
3. Set as `GITHUB_TOKEN` environment variable

### GitLab Token
1. Go to GitLab User Settings > Access Tokens
2. Create token with `read_repository` scope
3. Set as `GITLAB_TOKEN` environment variable

## 📊 Output

### Generated Files

1. **`portfolio_data_[timestamp].json`** - Raw repository data
   - Complete repository metadata
   - Commit history and statistics
   - Technology usage analysis
   - Perfect for further analysis

2. **`portfolio_summary_[timestamp].md`** - AI-generated portfolio
   - Executive summary with code metrics
   - Top 5 featured projects
   - Technical skills analysis
   - Development practices assessment
   - Professional growth timeline
   - Interview preparation recommendations

### Example Output Structure

```markdown
# Portfolio Summary

## Executive Summary
- Developer profile with estimated lines of code
- Years of experience based on project timeline
- Primary technical focus areas

## Top 5 Featured Projects
- Detailed project analysis
- Technical stack and complexity
- Contribution levels and impact

## Technical Skills & Expertise
- Programming languages ranked by proficiency
- Frameworks and libraries with context
- Architecture patterns demonstrated

[... and more sections]
```

## 🔧 Troubleshooting

### Common Issues

**No projects found:**
- Check API tokens have correct permissions
- Verify user info is retrieved correctly
- Ensure commit email matches account email

**Zero commits detected:**
- Check git config email: `git config --global user.email`
- Use `--min-commits 0` to include all projects
- Check debug output for email matching

**JSON too large:**
- Use `--max-commits 10` to limit commits per project
- Use `--min-commits 5` to filter projects
- Use `--platform github` or `--platform gitlab`

**Rate limiting:**
- Script handles rate limiting automatically
- Use tokens for higher rate limits
- Consider using `--debug` for detailed output

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
python portfolio_generator_cli.py --debug
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contributing Steps
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [COPYING](COPYING) file for details.

## 📚 Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [License](COPYING)

## 🙏 Acknowledgments

- Thanks to all contributors who help improve this project
- Built with love for the open-source community
- Special thanks to the AI providers for their excellent APIs

---

**Made with ❤️ for developers, by developers**

For support, questions, or feature requests, please [open an issue](https://github.com/yourusername/portfolio-generator/issues).
