# Portfolio Generator

A Python script that scrapes data from your GitHub and GitLab repositories (public and private) and uses the Anthropic API to generate a comprehensive portfolio summary. See a output example at `output_example.md`.

## Recent Updates

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
# Required
export ANTHROPIC_API_KEY="your_anthropic_api_key"

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
python portfolio_generator.py
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
Analyzes the most recent data file and generates portfolio summary

#### Run Both Stages (Default)
```bash
python portfolio_generator.py
```
Runs both stages sequentially

### Additional Options

#### Minimum Commits Filter
```bash
python portfolio_generator.py --min-commits 5
```
Only includes projects where you have at least 5 commits (default: 1)

#### Platform Selection
```bash
# Analyze only GitHub repositories
python portfolio_generator.py --platform github

# Analyze only GitLab repositories
python portfolio_generator.py --platform gitlab
```

#### Combined Example
```bash
python portfolio_generator.py --github-username myuser --min-commits 10 --stage 1
```

## API Tokens Setup

### GitHub Token:
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a token with `repo` scope for private repos, or `public_repo` for public only
3. Set as `GITHUB_TOKEN` environment variable

### GitLab Token:
1. Go to GitLab User Settings > Access Tokens
2. Create a token with `read_repository` scope
3. Set as `GITLAB_TOKEN` environment variable

### Anthropic API Key:
1. Sign up at https://console.anthropic.com/
2. Generate an API key
3. Set as `ANTHROPIC_API_KEY` environment variable

## Output

The script generates two files:
- `portfolio_data_[timestamp].json` - Raw repository data
- `portfolio_summary_[timestamp].md` - AI-generated portfolio summary

## Features

- Fetches both public and private repositories
- Supports GitHub and GitLab (including self-hosted)
- Extracts key metrics: stars, forks, languages, topics
- Generates professional portfolio summaries using AI
- Handles rate limiting and pagination
- Saves results with timestamps
- **Stage-based execution**: Run data collection and analysis separately
- **Configurable commit threshold**: Filter projects by minimum user commits
- **Total commit tracking**: Shows total commits across all selected projects
- **Platform selection**: Analyze only GitHub or only GitLab repositories
- **Improved commit detection**: Better matching of user commits across multiple email addresses

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--github-username` | GitHub username (optional if using token) | None |
| `--gitlab-username` | GitLab username (optional if using token) | None |
| `--use-existing` | Use most recent portfolio data file instead of fetching new data | False |
| `--stage` | Run specific stage: 1=get JSON data, 2=analyze data | Both stages |
| `--min-commits` | Minimum user commits required for a project to be included | 1 |
| `--platform` | Analyze only specific platform: `github` or `gitlab` | Both platforms |
