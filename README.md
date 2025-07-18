# Portfolio Generator

A Python script that scrapes data from your GitHub and GitLab repositories (public and private) and uses the Anthropic API to generate a comprehensive portfolio summary. See a output example at `output_example.md`.

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

### Using API tokens (recommended for private repos):
```bash
python portfolio_generator.py
```

### Using usernames (public repos only):
```bash
python portfolio_generator.py --github-username your_github_username --gitlab-username your_gitlab_username
```

### Use existing data (fast):
```bash
  python portfolio_generator.py --use-existing
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