#!/usr/bin/env python3
"""
Portfolio Generator Script
Scrapes GitHub and GitLab repositories to generate a portfolio summary using Anthropic API
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import anthropic
import base64
from collections import Counter
import glob

class PortfolioGenerator:
    def __init__(self, min_commits=1):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.gitlab_token = os.getenv('GITLAB_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        self.min_commits = min_commits
        self.total_user_commits = 0
        
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        self.user_email = None
        self.user_name = None
        
    def get_user_info(self):
        """Get authenticated user information for commit filtering"""
        if self.github_token:
            try:
                headers = {'Authorization': f'token {self.github_token}'}
                response = requests.get('https://api.github.com/user', headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    self.user_email = user_data.get('email')
                    self.user_name = user_data.get('name') or user_data.get('login')
                    print(f"GitHub user: {self.user_name} ({self.user_email})")
            except Exception as e:
                print(f"Error getting GitHub user info: {e}")
        
        if self.gitlab_token:
            try:
                headers = {'Authorization': f'Bearer {self.gitlab_token}'}
                response = requests.get(f'{self.gitlab_url}/api/v4/user', headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    if not self.user_email:
                        self.user_email = user_data.get('email')
                    if not self.user_name:
                        self.user_name = user_data.get('name') or user_data.get('username')
                    print(f"GitLab user: {self.user_name} ({self.user_email})")
            except Exception as e:
                print(f"Error getting GitLab user info: {e}")
    
    def count_user_commits(self, commits: List[Dict[str, Any]]) -> int:
        """Count commits made by the authenticated user"""
        if not commits:
            return 0
            
        user_commits = 0
        for commit in commits:
            author_email = commit.get('author_email', '').lower()
            author_name = commit.get('author', '').lower()
            
            # Check if commit is by the user
            if self.user_email and author_email and self.user_email.lower() == author_email:
                user_commits += 1
            elif self.user_name and author_name and self.user_name.lower() == author_name:
                user_commits += 1
                
        return user_commits
    
    def load_latest_portfolio_data(self) -> Optional[List[Dict[str, Any]]]:
        """Load the most recent portfolio data file"""
        try:
            # Find the most recent portfolio data file
            data_files = glob.glob('portfolio_data_*.json')
            if not data_files:
                print("No existing portfolio data files found")
                return None
            
            # Sort by modification time, get the most recent
            latest_file = max(data_files, key=os.path.getmtime)
            print(f"Loading existing portfolio data from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Loaded {len(data)} projects from existing data")
            return data
            
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            return None
        
    def fetch_github_repos(self, username: str = None) -> List[Dict[str, Any]]:
        """Fetch repositories from GitHub"""
        if not self.github_token:
            print("Warning: GITHUB_TOKEN not set, will only fetch public repos with rate limits")
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        repos = []
        
        # Fetch user's own repositories
        if username:
            url = f'https://api.github.com/users/{username}/repos'
        else:
            url = 'https://api.github.com/user/repos'
        
        page = 1
        while True:
            response = requests.get(f'{url}?page={page}&per_page=100', headers=headers)
            
            if response.status_code != 200:
                print(f"Error fetching GitHub repos: {response.status_code}")
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
            # Rate limiting
            time.sleep(0.1)
        
        return repos
    
    def fetch_github_repo_details(self, repo_full_name: str) -> Dict[str, Any]:
        """Fetch detailed information about a GitHub repository"""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        details = {}
        
        # Fetch README
        try:
            readme_response = requests.get(f'https://api.github.com/repos/{repo_full_name}/readme', headers=headers)
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                details['readme'] = readme_content[:2000]  # Limit to 2000 chars
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching README for {repo_full_name}: {e}")
        
        # Fetch repository tree (folder structure)
        try:
            tree_response = requests.get(f'https://api.github.com/repos/{repo_full_name}/git/trees/HEAD?recursive=1', headers=headers)
            if tree_response.status_code == 200:
                tree_data = tree_response.json()
                files = [item['path'] for item in tree_data.get('tree', []) if item['type'] == 'blob']
                details['files'] = files[:100]  # Limit to 100 files
                details['folder_structure'] = self.analyze_folder_structure(files)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching tree for {repo_full_name}: {e}")
        
        # Fetch all user commits (paginated)
        try:
            user_commits = []
            page = 1
            while True:
                commits_response = requests.get(f'https://api.github.com/repos/{repo_full_name}/commits?per_page=100&page={page}', headers=headers)
                if commits_response.status_code != 200:
                    break
                    
                commits_data = commits_response.json()
                if not commits_data:
                    break
                
                # Filter commits to only include user commits
                for commit in commits_data:
                    author_email = commit['commit']['author'].get('email', '').lower()
                    author_name = commit['commit']['author']['name'].lower()
                    
                    # Check if commit is by the user
                    if ((self.user_email and author_email and self.user_email.lower() == author_email) or
                        (self.user_name and author_name and self.user_name.lower() == author_name)):
                        user_commits.append({
                            'message': commit['commit']['message'],
                            'date': commit['commit']['author']['date'],
                            'author': commit['commit']['author']['name'],
                            'author_email': commit['commit']['author'].get('email', ''),
                            'sha': commit['sha'][:8]
                        })
                
                page += 1
                time.sleep(0.1)
                
                # Limit to reasonable number of pages to avoid infinite loops
                if page > 20:
                    break
                        
            details['user_commits'] = user_commits
            details['recent_commits'] = user_commits[:20]  # Keep for backward compatibility
            
            # Count user commits
            details['user_commits_count'] = len(user_commits)
            details['total_commits_fetched'] = len(user_commits)
        except Exception as e:
            print(f"Error fetching commits for {repo_full_name}: {e}")
            details['user_commits_count'] = 0
        
        # Fetch languages
        try:
            languages_response = requests.get(f'https://api.github.com/repos/{repo_full_name}/languages', headers=headers)
            if languages_response.status_code == 200:
                details['languages'] = languages_response.json()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching languages for {repo_full_name}: {e}")
        
        # Fetch additional repository stats
        try:
            repo_response = requests.get(f'https://api.github.com/repos/{repo_full_name}', headers=headers)
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                details['watchers_count'] = repo_data.get('watchers_count', 0)
                details['network_count'] = repo_data.get('network_count', 0)
                details['subscribers_count'] = repo_data.get('subscribers_count', 0)
                details['has_issues'] = repo_data.get('has_issues', False)
                details['has_projects'] = repo_data.get('has_projects', False)
                details['has_wiki'] = repo_data.get('has_wiki', False)
                details['has_pages'] = repo_data.get('has_pages', False)
                details['default_branch'] = repo_data.get('default_branch', 'main')
                details['open_issues_count'] = repo_data.get('open_issues_count', 0)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching repo stats for {repo_full_name}: {e}")
        
        return details
    
    def fetch_gitlab_repos(self, username: str = None) -> List[Dict[str, Any]]:
        """Fetch repositories from GitLab"""
        if not self.gitlab_token:
            print("Warning: GITLAB_TOKEN not set, will only fetch public repos")
        
        headers = {}
        if self.gitlab_token:
            headers['Authorization'] = f'Bearer {self.gitlab_token}'
        
        repos = []
        
        # Fetch user's projects
        if username:
            # First get user ID
            print(f"Looking up GitLab user: {username}")
            user_response = requests.get(f'{self.gitlab_url}/api/v4/users?username={username}', headers=headers)
            print(f"User lookup response: {user_response.status_code}")
            if user_response.status_code == 200 and user_response.json():
                user_id = user_response.json()[0]['id']
                url = f'{self.gitlab_url}/api/v4/users/{user_id}/projects'
                print(f"Using URL: {url}")
            else:
                print(f"Could not find GitLab user: {username}")
                print(f"Response: {user_response.text}")
                return []
        else:
            # Try different approaches for authenticated user
            if self.gitlab_token:
                # First try to get current user info
                user_response = requests.get(f'{self.gitlab_url}/api/v4/user', headers=headers)
                print(f"Current user response: {user_response.status_code}")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"Authenticated as: {user_data.get('username', 'Unknown')}")
                    url = f'{self.gitlab_url}/api/v4/projects?membership=true'
                else:
                    print(f"Authentication failed: {user_response.text}")
                    # Fallback to basic projects endpoint
                    url = f'{self.gitlab_url}/api/v4/projects?simple=true'
            else:
                print("No GitLab token provided, fetching public projects")
                url = f'{self.gitlab_url}/api/v4/projects?visibility=public&simple=true'
        
        print(f"Fetching from URL: {url}")
        page = 1
        while True:
            try:
                # Construct the URL properly
                if '?' in url:
                    response = requests.get(f'{url}&page={page}&per_page=50', headers=headers, timeout=30)
                else:
                    response = requests.get(f'{url}?page={page}&per_page=50', headers=headers, timeout=30)
                
                print(f"Page {page} response: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Error fetching GitLab repos: {response.status_code}")
                    print(f"Response body: {response.text}")
                    if response.status_code == 401:
                        print("Authentication error - check your GITLAB_TOKEN")
                        break
                    elif response.status_code == 403:
                        print("Access forbidden - check token permissions")
                        break
                    elif response.status_code == 400:
                        print("Bad request - using basic projects endpoint")
                        # Use basic projects endpoint
                        simple_url = f'{self.gitlab_url}/api/v4/projects'
                        response = requests.get(f'{simple_url}?page={page}&per_page=50', headers=headers, timeout=30)
                        if response.status_code != 200:
                            print(f"Basic endpoint also failed: {response.status_code}")
                            break
                    else:
                        break
                    
                page_repos = response.json()
                if not page_repos:
                    print("No more repositories found")
                    break
                    
                repos.extend(page_repos)
                print(f"Found {len(page_repos)} repos on page {page}, total: {len(repos)}")
                page += 1
                
                # Limit to reasonable number of pages
                if page > 10:
                    print("Stopping at page 10 to avoid rate limits")
                    break
                
                # Rate limiting
                time.sleep(0.3)
                
            except requests.exceptions.RequestException as e:
                print(f"Network error on page {page}: {e}")
                if page == 1:
                    # If first page fails, give up
                    break
                else:
                    # If later page fails, continue with what we have
                    print("Continuing with repositories found so far")
                    break
            except KeyboardInterrupt:
                print("Interrupted by user")
                break
        
        return repos
    
    def fetch_gitlab_repo_details(self, project_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a GitLab repository"""
        headers = {}
        if self.gitlab_token:
            headers['Authorization'] = f'Bearer {self.gitlab_token}'
        
        details = {}
        
        # Fetch README
        try:
            readme_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/files/README.md/raw?ref=HEAD', headers=headers)
            if readme_response.status_code == 200:
                details['readme'] = readme_response.text[:2000]  # Limit to 2000 chars
            else:
                # Try other common README names
                for readme_name in ['README.rst', 'README.txt', 'README']:
                    readme_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/files/{readme_name}/raw?ref=HEAD', headers=headers)
                    if readme_response.status_code == 200:
                        details['readme'] = readme_response.text[:2000]
                        break
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching README for project {project_id}: {e}")
        
        # Fetch repository tree (folder structure)
        try:
            tree_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/tree?recursive=true&per_page=100', headers=headers)
            if tree_response.status_code == 200:
                tree_data = tree_response.json()
                files = [item['path'] for item in tree_data if item['type'] == 'blob']
                details['files'] = files[:100]  # Limit to 100 files
                details['folder_structure'] = self.analyze_folder_structure(files)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching tree for project {project_id}: {e}")
        
        # Fetch all user commits (paginated)
        try:
            user_commits = []
            page = 1
            while True:
                commits_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/commits?per_page=100&page={page}', headers=headers)
                if commits_response.status_code != 200:
                    break
                    
                commits_data = commits_response.json()
                if not commits_data:
                    break
                
                # Filter commits to only include user commits
                for commit in commits_data:
                    author_email = commit['author_email'].lower()
                    author_name = commit['author_name'].lower()
                    
                    # Check if commit is by the user
                    if ((self.user_email and author_email and self.user_email.lower() == author_email) or
                        (self.user_name and author_name and self.user_name.lower() == author_name)):
                        user_commits.append({
                            'message': commit['message'],
                            'date': commit['created_at'],
                            'author': commit['author_name'],
                            'author_email': commit['author_email'],
                            'sha': commit['id'][:8]
                        })
                
                page += 1
                time.sleep(0.1)
                
                # Limit to reasonable number of pages to avoid infinite loops
                if page > 20:
                    break
                        
            details['user_commits'] = user_commits
            details['recent_commits'] = user_commits[:20]  # Keep for backward compatibility
            
            # Count user commits
            details['user_commits_count'] = len(user_commits)
            details['total_commits_fetched'] = len(user_commits)
        except Exception as e:
            print(f"Error fetching commits for project {project_id}: {e}")
            details['user_commits_count'] = 0
        
        # Fetch languages (GitLab doesn't have a direct API, so we'll analyze files)
        if 'files' in details:
            details['languages'] = self.detect_languages_from_files(details['files'])
        
        return details
    
    def analyze_folder_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze folder structure from file paths"""
        folders = set()
        file_types = Counter()
        
        for file_path in files:
            # Extract folders (limit to 4 depth levels)
            parts = file_path.split('/')
            for i in range(min(len(parts) - 1, 4)):
                folder = '/'.join(parts[:i+1])
                folders.add(folder)
            
            # Extract file extensions
            if '.' in parts[-1]:
                ext = parts[-1].split('.')[-1].lower()
                file_types[ext] += 1
        
        # Identify project type based on files
        project_indicators = {
            'web': ['html', 'css', 'js', 'jsx', 'ts', 'tsx', 'vue', 'angular'],
            'mobile': ['swift', 'kt', 'java', 'dart', 'xaml'],
            'backend': ['py', 'java', 'cs', 'go', 'rb', 'php', 'rs'],
            'data': ['ipynb', 'r', 'sql', 'parquet', 'csv'],
            'devops': ['yml', 'yaml', 'tf', 'dockerfile', 'sh']
        }
        
        project_type = 'general'
        max_score = 0
        for ptype, extensions in project_indicators.items():
            score = sum(file_types.get(ext, 0) for ext in extensions)
            if score > max_score:
                max_score = score
                project_type = ptype
        
        return {
            'folders': sorted(list(folders))[:20],  # Limit to 20 folders
            'file_types': dict(file_types.most_common(10)),
            'project_type': project_type,
            'total_files': len(files)
        }
    
    def detect_languages_from_files(self, files: List[str]) -> Dict[str, int]:
        """Detect programming languages from file extensions"""
        extension_map = {
            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript', 'java': 'Java',
            'cpp': 'C++', 'c': 'C', 'cs': 'C#', 'php': 'PHP', 'rb': 'Ruby',
            'go': 'Go', 'rs': 'Rust', 'swift': 'Swift', 'kt': 'Kotlin',
            'html': 'HTML', 'css': 'CSS', 'scss': 'SCSS', 'sass': 'Sass',
            'vue': 'Vue', 'jsx': 'React', 'tsx': 'React TypeScript',
            'sql': 'SQL', 'r': 'R', 'matlab': 'MATLAB', 'sh': 'Shell',
            'yml': 'YAML', 'yaml': 'YAML', 'json': 'JSON', 'xml': 'XML'
        }
        
        languages = Counter()
        for file_path in files:
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                if ext in extension_map:
                    languages[extension_map[ext]] += 1
        
        return dict(languages)
    
    def clean_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Clean project data by removing unwanted attributes and simplifying user_commits"""
        cleaned_project = project.copy()
        
        # Remove unwanted attributes
        attrs_to_remove = [
            'files',
            'meets_commit_threshold',
            'topics',
            'is_fork',
            'is_private',
            'size',
            'recent_commits'
        ]
        
        for attr in attrs_to_remove:
            cleaned_project.pop(attr, None)
        
        # Remove folders from folder_structure if it exists
        if 'folder_structure' in cleaned_project and isinstance(cleaned_project['folder_structure'], dict):
            cleaned_project['folder_structure'].pop('folders', None)
        
        # Clean user_commits to only include message and date
        if 'user_commits' in cleaned_project and isinstance(cleaned_project['user_commits'], list):
            cleaned_commits = []
            for commit in cleaned_project['user_commits']:
                if isinstance(commit, dict):
                    cleaned_commit = {
                        'message': commit.get('message', ''),
                        'date': commit.get('date', '')
                    }
                    cleaned_commits.append(cleaned_commit)
            cleaned_project['user_commits'] = cleaned_commits
        
        return cleaned_project
    
    def process_github_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub repository data with detailed information"""
        processed_repo = {
            'platform': 'GitHub',
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo.get('description', ''),
            'language': repo.get('language', ''),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'url': repo['html_url'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'topics': repo.get('topics', []),
            'is_fork': repo['fork'],
            'is_private': repo['private'],
            'size': repo.get('size', 0)
        }
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['full_name']}...")
        details = self.fetch_github_repo_details(repo['full_name'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        self.total_user_commits += user_commits
        
        return processed_repo
    
    def process_gitlab_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitLab repository data with detailed information"""
        processed_repo = {
            'platform': 'GitLab',
            'name': repo['name'],
            'full_name': repo['path_with_namespace'],
            'description': repo.get('description', ''),
            'language': repo.get('default_branch', ''),
            'stars': repo.get('star_count', 0),
            'forks': repo.get('forks_count', 0),
            'url': repo['web_url'],
            'created_at': repo['created_at'],
            'updated_at': repo['last_activity_at'],
            'topics': repo.get('topics', []),
            'is_fork': repo.get('forked_from_project') is not None,
            'is_private': repo['visibility'] == 'private',
            'size': 0  # GitLab doesn't provide size in basic API
        }
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['path_with_namespace']}...")
        details = self.fetch_gitlab_repo_details(repo['id'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        self.total_user_commits += user_commits
        
        return processed_repo
    
    def generate_summary(self, projects: List[Dict[str, Any]]) -> str:
        """Generate portfolio summary using Anthropic API"""
        project_data = json.dumps(projects, indent=2)
        
        prompt = f"""
You are a professional portfolio writer. Based on the following detailed project data from GitHub and GitLab repositories, create a comprehensive portfolio summary that highlights the developer's skills, contributions, and expertise.

Project Data includes:
- Repository metadata (stars, forks, dates, topics)
- README content providing project context
- Folder structure and file organization
- Programming languages and technologies used
- Recent commit history and development activity
- Project types and complexity indicators

Project Data:
{project_data}

Please create:
1. An executive summary of the developer's profile
2. Key technical skills and technologies used (based on languages, file types, and project structure)
3. Notable projects with descriptions, purpose, and technical implementation details
4. Programming languages and frameworks expertise (with evidence from actual code)
5. Development patterns, code organization, and software architecture understanding
6. Project diversity and problem-solving range
7. Contribution quality based on commit messages and project evolution
8. Recommendations for portfolio presentation

Focus on:
- Technical depth evidenced by folder structure and file types
- Project complexity shown through README descriptions and architecture
- Code quality indicators (stars, forks, activity, commit patterns)
- Technology stack diversity across different project types
- Professional growth shown through project timeline and increasing complexity
- Real-world applicability and problem-solving demonstrated by project purposes

Format the response in markdown for easy reading and presentation.
"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating summary with Anthropic API: {e}")
            return "Error generating portfolio summary."
    
    def save_results(self, projects: List[Dict[str, Any]], summary: str):
        """Save results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw project data
        with open(f'portfolio_data_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(projects, f, indent=2, ensure_ascii=False)
        
        # Save portfolio summary
        with open(f'portfolio_summary_{timestamp}.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Results saved:")
        print(f"- Raw data: portfolio_data_{timestamp}.json")
        print(f"- Portfolio summary: portfolio_summary_{timestamp}.md")
    
    def run_stage_1(self, github_username: str = None, gitlab_username: str = None):
        """Stage 1: Get JSON data from repositories"""
        print("Stage 1: Fetching repository data...")
        
        # Get user information for commit filtering
        self.get_user_info()
        
        all_projects = []
        
        # Fetch GitLab repositories
        if self.gitlab_token or gitlab_username:
            print("Fetching GitLab repositories...")
            gitlab_repos = self.fetch_gitlab_repos(gitlab_username)
            print(f"Processing {len(gitlab_repos)} GitLab repositories with detailed analysis...")
            gitlab_projects = []
            for repo in gitlab_repos:
                if not repo.get('forked_from_project') or repo.get('star_count', 0) > 0:  # Skip unmodified forks
                    processed_repo = self.process_gitlab_repo(repo)
                    if processed_repo.get('meets_commit_threshold', False):
                        gitlab_projects.append(processed_repo)
                    else:
                        print(f"  Skipping {repo['path_with_namespace']} - insufficient user commits ({processed_repo.get('user_commits_count', 0)})")
            all_projects.extend(gitlab_projects)
            print(f"Processed {len(gitlab_projects)} GitLab repositories (filtered by commit threshold)")

        # Fetch GitHub repositories
        if self.github_token or github_username:
            print("Fetching GitHub repositories...")
            github_repos = self.fetch_github_repos(github_username)
            print(f"Processing {len(github_repos)} GitHub repositories with detailed analysis...")
            github_projects = []
            for repo in github_repos:
                if not repo['fork'] or repo['stargazers_count'] > 0:  # Skip unmodified forks
                    processed_repo = self.process_github_repo(repo)
                    if processed_repo.get('meets_commit_threshold', False):
                        github_projects.append(processed_repo)
                    else:
                        print(f"  Skipping {repo['full_name']} - insufficient user commits ({processed_repo.get('user_commits_count', 0)})")
            all_projects.extend(github_projects)
            print(f"Processed {len(github_projects)} GitHub repositories (filtered by commit threshold)")

        if not all_projects:
            print("No projects found. Please check your credentials and usernames.")
            return None
        
        print(f"\nTotal projects found: {len(all_projects)}")
        print(f"Total user commits across all projects: {self.total_user_commits}")
        
        # Clean data before saving
        cleaned_projects = [self.clean_project_data(project) for project in all_projects]
        
        # Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'portfolio_data_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cleaned_projects, f, indent=2, ensure_ascii=False)
        
        print(f"Stage 1 completed! Data saved to: {filename}")
        return all_projects
    
    def run_stage_2(self, projects_data: List[Dict[str, Any]] = None):
        """Stage 2: Analyze the data and generate portfolio summary"""
        print("Stage 2: Analyzing data and generating portfolio summary...")
        
        if projects_data is None:
            projects_data = self.load_latest_portfolio_data()
            if not projects_data:
                print("No data found. Please run stage 1 first or provide data.")
                return
        
        # Count total user commits from the data
        total_commits = sum(project.get('user_commits_count', 0) for project in projects_data)
        print(f"Analyzing {len(projects_data)} projects with {total_commits} total user commits...")
        
        summary = self.generate_summary(projects_data)
        
        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'portfolio_summary_{timestamp}.md'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Stage 2 completed! Portfolio summary saved to: {filename}")
        return summary
    
    def run(self, github_username: str = None, gitlab_username: str = None, use_existing_data: bool = False, stage: int = None):
        """Main execution method with stage support"""
        print("Starting portfolio generation...")
        
        # Handle stage-specific execution
        if stage == 1:
            print("Running Stage 1 only: Data collection")
            self.run_stage_1(github_username, gitlab_username)
            return
        elif stage == 2:
            print("Running Stage 2 only: Data analysis")
            self.run_stage_2()
            return
        
        # Default behavior: run both stages or use existing data
        if use_existing_data:
            existing_data = self.load_latest_portfolio_data()
            if existing_data:
                print("Generating portfolio summary from existing data...")
                self.run_stage_2(existing_data)
                print("\nPortfolio generation completed using existing data!")
                return
            else:
                print("No existing data found, proceeding with fresh data collection...")
        
        # Run both stages
        print("Running both stages: Data collection and analysis")
        projects_data = self.run_stage_1(github_username, gitlab_username)
        if projects_data:
            self.run_stage_2(projects_data)
            print("\nPortfolio generation completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate portfolio from GitHub and GitLab projects")
    parser.add_argument("--github-username", help="GitHub username (optional if using token)")
    parser.add_argument("--gitlab-username", help="GitLab username (optional if using token)")
    parser.add_argument("--use-existing", action="store_true", help="Use the most recent portfolio data file instead of fetching new data")
    parser.add_argument("--stage", type=int, choices=[1, 2], help="Run specific stage: 1=get JSON data, 2=analyze data (default: run both)")
    parser.add_argument("--min-commits", type=int, default=1, help="Minimum user commits required for a project to be included (default: 1)")
    
    args = parser.parse_args()
    
    try:
        generator = PortfolioGenerator(min_commits=args.min_commits)
        generator.run(args.github_username, args.gitlab_username, args.use_existing, args.stage)
    except Exception as e:
        print(f"Error: {e}")