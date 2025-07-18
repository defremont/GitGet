# Portfolio Generator

A Python script that scrapes data from your GitHub and GitLab repositories (public and private) and uses the Anthropic API to generate a comprehensive portfolio summary. See a output example at `output_example.md`.

## Recent Updates

### v1.3.0 - Smart Data Filtering & Clean JSON Output
- **Conditional attribute inclusion**: Only includes stars/forks if > 0, descriptions/READMEs if not empty
- **Total commits tracking**: Shows total commits from all users (not just authenticated user)
- **Cleaner JSON data**: Removes irrelevant repository flags and empty attributes
- **Focused analysis**: AI gets cleaner, more meaningful data for better portfolio generation

### v1.2.0 - Enhanced AI Analysis & Project Details
- **Comprehensive AI prompts**: Significantly improved AI analysis with professional portfolio writing approach
- **Project details file**: New detailed project breakdown sorted by contribution level
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

The script generates three files:
- `portfolio_data_[timestamp].json` - Raw repository data
- `portfolio_summary_[timestamp].md` - AI-generated comprehensive portfolio summary
- `portfolio_projects_[timestamp].md` - Detailed project breakdown sorted by contribution level

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
- **Duplicate filtering**: Ignores commits with identical messages for cleaner analysis
- **Professional AI analysis**: Enhanced prompts for comprehensive portfolio and project analysis
- **Project details file**: Separate detailed breakdown sorted by contribution level with interview prep
- **Smart data filtering**: Conditional inclusion of attributes based on value (stars/forks > 0, non-empty descriptions/READMEs)
- **Total commits tracking**: Shows all commits in repository from all users for better context

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

## Output Files Explained

### Portfolio Summary (`portfolio_summary_[timestamp].md`)
A comprehensive portfolio overview including:
- Executive summary of developer profile
- Technical skills and expertise analysis
- Development practices and code quality assessment
- Professional growth timeline
- Portfolio presentation recommendations

### Project Details (`portfolio_projects_[timestamp].md`)
Detailed project breakdown with:
- Projects sorted by contribution level (most worked on first)
- Technical implementation details for each project
- Architecture and technology stack analysis
- Interview talking points for each project
- Contribution summaries and portfolio highlights

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
