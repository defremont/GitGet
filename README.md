# Portfolio Generator

A Python script that scrapes data from your GitHub and GitLab repositories (public and private) and uses multiple AI providers (Anthropic, OpenAI, Google Gemini) to generate a comprehensive portfolio summary with detailed project analysis. See a output example at `output_example.md`.

🌟 **NEW**: Multi-AI provider support with Gemini 2.5 Pro as default! Now includes estimated lines of code and highlights your top 5 projects!

## Recent Updates

### v2.0.0 - Multi-AI Provider Support
- **Multiple AI providers**: Support for Anthropic Claude, OpenAI GPT, and Google Gemini
- **Smart model selection**: Choose from reasoning models, cheaper options, and free tiers
- **Gemini 2.5 Pro default**: Best free model with excellent analysis capabilities
- **Model recommendations**: Built-in guidance for choosing the right model for your needs
- **Backward compatibility**: Existing API keys continue to work

### v1.6.0 - Enhanced Portfolio Analysis & Simplified Workflow
- **Lines of code estimation**: Automatically estimates total lines of code across all projects
- **Top 5 projects highlight**: AI identifies and features your most significant projects
- **Streamlined workflow**: Removed HTML generation for faster, focused portfolio creation
- **Enhanced AI analysis**: Improved project ranking and technical skill assessment
- **Performance improvements**: Faster execution with simplified two-stage process

### v1.3.0 - Smart Data Filtering & Clean JSON Output
- **Conditional attribute inclusion**: Only includes stars/forks if > 0, descriptions/READMEs if not empty
- **Total commits tracking**: Shows total commits from all users (not just authenticated user)
- **Cleaner JSON data**: Removes irrelevant repository flags and empty attributes
- **Focused analysis**: AI gets cleaner, more meaningful data for better portfolio generation

### v1.2.0 - Enhanced AI Analysis & Project Details
- **Comprehensive AI prompts**: Significantly improved AI analysis with professional portfolio writing approach
- **Interactive HTML portfolio**: Complete responsive website with project showcase and professional presentation
- **Duplicate commit filtering**: Ignores commits with identical messages to focus on unique contributions
- **Enhanced sorting**: Projects sorted by commits, stars, forks, and documentation quality
- **Interview preparation**: AI-generated talking points and project highlights for interviews

### v1.1.0 - Improved Commit Detection & Platform Selection
- **Fixed commit counting**: Improved user commit detection by tracking multiple email addresses and usernames
- **Enhanced debugging**: Added detailed output to help troubleshoot commit counting issues
- **Platform selection**: New `--platform` option to analyze only GitHub or only GitLab repositories
- **Better error handling**: More informative error messages and troubleshooting tips

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# AI Provider API Keys (choose one or more)
export GEMINI_API_KEY="your_gemini_api_key"      # Google Gemini (recommended - free)
export ANTHROPIC_API_KEY="your_anthropic_api_key"  # Anthropic Claude (paid)
export OPENAI_API_KEY="your_openai_api_key"      # OpenAI GPT (paid/free tiers)

# Optional (for private repos and higher rate limits)
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"

# Optional (if using self-hosted GitLab)
export GITLAB_URL="https://your-gitlab-instance.com"
```

## Usage

### Basic Usage

#### Using API tokens (recommended for private repos):
```bash
# Default: uses Gemini 2.5 Pro (free)
python portfolio_generator.py

# Using specific AI provider
python portfolio_generator.py --model-provider anthropic --model-name claude-3-5-haiku-latest
python portfolio_generator.py --model-provider openai --model-name gpt-4.1-nano
python portfolio_generator.py --model-provider google --model-name gemini-2.5-flash
```

#### Using usernames (public repos only):
```bash
python portfolio_generator.py --github-username your_github_username --gitlab-username your_gitlab_username
```

#### Use existing data (fast):
```bash
python portfolio_generator.py --use-existing
```

### Stage-based Execution

The script supports two-stage execution for better control:

#### Stage 1: Data Collection Only
```bash
python portfolio_generator.py --stage 1
```
Fetches repository data and saves to `portfolio_data_[timestamp].json`

#### Stage 2: Analysis Only
```bash
python portfolio_generator.py --stage 2
```
Analyzes the most recent data file and generates portfolio summary with top 5 projects and lines of code estimation

#### Run Both Stages (Default)
```bash
python portfolio_generator.py
```
Runs data collection and analysis sequentially

### Additional Options

#### Minimum Commits Filter
```bash
python portfolio_generator.py --min-commits 5
```
Only includes projects where you have at least 5 commits (default: 1)

#### Maximum Commits Per Project (JSON Size Control)
```bash
python portfolio_generator.py --max-commits 10
```
Limits commits per project in JSON to most recent N commits (default: all commits)

#### Platform Selection
```bash
# Analyze only GitHub repositories
python portfolio_generator.py --platform github

# Analyze only GitLab repositories
python portfolio_generator.py --platform gitlab
```

#### Combined Example
```bash
python portfolio_generator.py --github-username myuser --min-commits 10 --max-commits 20 --stage 1
```

## AI Models & Providers

### 🎯 Recommended Models

| Provider | Model | Cost | Reasoning | Best For |
|----------|-------|------|-----------|----------|
| **Google** | `gemini-2.5-pro` | ✅ Free | ❌ No | **Default choice** - Best free model with excellent analysis |
| **Google** | `gemini-2.5-flash` | ✅ Free | ❌ No | Fastest option for quick generation |
| **Anthropic** | `claude-sonnet-4-0` | 💰 Paid | ✅ Yes | Premium reasoning capabilities |
| **Anthropic** | `claude-3-5-haiku-latest` | 💰 Paid | ❌ No | Cheaper Claude option |
| **OpenAI** | `gpt-4.1` | 💰 Paid | ❌ No | Reliable GPT-4 performance |
| **OpenAI** | `gpt-4.1-nano` | 🆓 Free tier | ❌ No | Good free option with limits |
| **OpenAI** | `o4-mini` | 💰 Paid | ✅ Yes | OpenAI's reasoning model |
| **OpenAI** | `gpt-4.1-mini` | 🆓 Free tier | ❌ No | Basic free option |

### 🚀 Quick Start Recommendations

**For beginners or cost-conscious users:**
```bash
# Use default Gemini 2.5 Pro (free and excellent)
python portfolio_generator.py
```

**For users wanting faster results:**
```bash
python portfolio_generator.py --model-provider google --model-name gemini-2.5-flash
```

**For premium reasoning capabilities:**
```bash
python portfolio_generator.py --model-provider anthropic --model-name claude-sonnet-4-0
```

**For budget-conscious users with existing credits:**
```bash
python portfolio_generator.py --model-provider anthropic --model-name claude-3-5-haiku-latest
```

### 📊 Model Comparison

#### Google Gemini
- **gemini-2.5-pro**: Free, excellent analysis quality, no reasoning
- **gemini-2.5-flash**: Free, fastest generation, good for quick portfolios

#### Anthropic Claude
- **claude-sonnet-4-0**: Paid, advanced reasoning, premium quality
- **claude-3-5-haiku-latest**: Paid, cheaper option, good quality

#### OpenAI GPT
- **gpt-4.1**: Paid, reliable performance, no reasoning
- **gpt-4.1-nano**: Free tier available, basic capabilities
- **o4-mini**: Paid, reasoning capabilities, good for complex analysis
- **gpt-4.1-mini**: Free tier available, minimal capabilities

## API Tokens Setup

### Google Gemini API Key (Recommended):
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Set as `GEMINI_API_KEY` environment variable

### Anthropic API Key:
1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Generate an API key
3. Set as `ANTHROPIC_API_KEY` environment variable

### OpenAI API Key:
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key
3. Set as `OPENAI_API_KEY` environment variable

### GitHub Token:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a token with `repo` scope for private repos, or `public_repo` for public only
3. Set as `GITHUB_TOKEN` environment variable

### GitLab Token:
1. Go to GitLab User Settings > Access Tokens
2. Create a token with `read_repository` scope
3. Set as `GITLAB_TOKEN` environment variable


## Output

The script generates the following files:
- **Stage 1**: `portfolio_data_[timestamp].json` - Raw repository data
- **Stage 2**: `portfolio_summary_[timestamp].md` - AI-generated comprehensive portfolio summary with top 5 projects and lines of code estimation

## Features

### 🚀 **Core Functionality**
- Fetches both public and private repositories
- Supports GitHub and GitLab (including self-hosted)
- Extracts comprehensive metrics: stars, forks, languages, commit history
- Handles rate limiting and pagination automatically
- Saves results with timestamps

### 🤖 **AI-Powered Analysis**
- **Professional portfolio summaries**: Comprehensive analysis using Anthropic API
- **Top 5 projects highlight**: AI identifies and features your most significant projects
- **Lines of code estimation**: Automatically calculates approximate lines of code across all projects
- **Interview preparation**: AI-generated talking points and project highlights

### ⚙️ **Advanced Controls**
- **Stage-based execution**: Run data collection and analysis separately
- **Platform selection**: Analyze only GitHub or only GitLab repositories
- **Configurable commit threshold**: Filter projects by minimum user commits
- **User-controlled commit limits**: `--max-commits` option for managing JSON size
- **Smart data filtering**: Conditional inclusion based on value (stars/forks > 0, non-empty content)

### 🔧 **Technical Features**
- **Improved commit detection**: Better matching across multiple email addresses
- **Duplicate filtering**: Ignores identical commit messages for cleaner analysis
- **Total commit tracking**: Shows all commits in repository from all users
- **Enhanced debugging**: Detailed output for troubleshooting
- **Professional error handling**: Informative messages and troubleshooting tips

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--github-username` | GitHub username (optional if using token) | None |
| `--gitlab-username` | GitLab username (optional if using token) | None |
| `--use-existing` | Use most recent portfolio data file instead of fetching new data | False |
| `--stage` | Run specific stage: 1=get JSON data, 2=analyze data | Both stages |
| `--min-commits` | Minimum user commits required for a project to be included | 1 |
| `--platform` | Analyze only specific platform: `github` or `gitlab` | Both platforms |
| `--max-commits` | Maximum commits per project to include in JSON output | All commits |
| `--model-provider` | AI provider: `anthropic`, `openai`, `google` | `google` |
| `--model-name` | Specific model name to use | `gemini-2.5-pro` |

## Output Files Explained

### Portfolio Summary (`portfolio_summary_[timestamp].md`)
A comprehensive portfolio overview including:
- Executive summary of developer profile with estimated lines of code
- Top 5 featured projects with detailed analysis
- Technical skills and expertise analysis ranked by proficiency
- Development practices and code quality assessment
- Professional growth timeline
- Portfolio presentation recommendations

### Raw Data (`portfolio_data_[timestamp].json`)
Complete structured data including:
- All repository metadata (conditionally filtered)
- Commit history and statistics
- Technology usage and file structure
- Perfect for further analysis or custom reporting

## Troubleshooting

### Projects showing 0 commits but you have commits

This usually happens when your commit author email doesn't match your GitHub/GitLab account email. The script now:

1. **Fetches multiple email addresses**: Gets all emails associated with your GitHub account
2. **Tracks usernames**: Matches commits by username as well as email
3. **Provides debug output**: Shows what emails/names are being used for matching

**Solutions:**
- Ensure your git config email matches your GitHub/GitLab account: `git config --global user.email "your@email.com"`
- Check the debug output to see what emails are being tracked
- Use `--min-commits 0` to include all projects regardless of commit count

### JSON too large for AI analysis

If you get "prompt is too long" errors, you have several options:

1. **Limit commits per project**: Use `--max-commits 10` to include only the 10 most recent commits per project
2. **Reduce projects**: Use `--min-commits 5` to include only projects with substantial contributions
3. **Platform selection**: Use `--platform github` or `--platform gitlab` to analyze only one platform

**Example for large portfolios:**
```bash
python portfolio_generator.py --max-commits 15 --min-commits 3
```

**Note:** The portfolio summary now includes estimated lines of code and highlights your top 5 most significant projects.

### No projects found

**Check:**
1. Your API tokens have correct permissions (`repo` scope for GitHub, `read_repository` for GitLab)
2. The debug output shows your user info was retrieved correctly
3. You're not using `--platform` to restrict to a platform you don't have repos on

### Rate limiting issues

- The script automatically handles rate limiting with delays
- GitHub tokens provide much higher rate limits than anonymous access
- GitLab tokens are required for private repos and higher limits

#### Data Filtering Rules:
- **Stars/Forks**: Only included if > 0
- **Description**: Only included if not empty
- **README**: Only included if not empty
- **Watchers/Subscribers/Network counts**: Only included if > 0
- **Total commits**: Shows commits from all users (not just authenticated user)
- **Excluded attributes**: `has_issues`, `has_projects`, `has_wiki`, `has_pages`, `default_branch`, `open_issues_count`, `language`
