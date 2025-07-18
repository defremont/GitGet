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
from abc import ABC, abstractmethod

# Optional imports for different AI providers
try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_summary(self, prompt: str) -> str:
        """Generate a summary using the AI model"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass

class AnthropicProvider(AIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_summary(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "anthropic",
            "model": self.model,
            "has_reasoning": self.model == "claude-sonnet-4-0",
            "is_free": False,
            "is_cheaper": self.model == "claude-3-5-haiku-latest"
        }

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-nano"):
        if openai is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_summary(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "has_reasoning": self.model == "o4-mini",
            "is_free": self.model in ["gpt-4.1-nano", "gpt-4.1-mini"],
            "is_cheaper": self.model in ["gpt-4.1-nano", "gpt-4.1-mini"]
        }

class GeminiProvider(AIProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        if genai is None:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        genai.configure(api_key=api_key)
        self.model = model
        self.client = genai.GenerativeModel(model)
    
    def generate_summary(self, prompt: str) -> str:
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "google",
            "model": self.model,
            "has_reasoning": False,
            "is_free": True,
            "is_cheaper": self.model == "gemini-2.5-flash"
        }

class PortfolioGenerator:
    def __init__(self, min_commits=1, max_commits_per_project=None, model_provider=None, model_name=None):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.gitlab_token = os.getenv('GITLAB_TOKEN')
        self.gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        self.min_commits = min_commits
        self.max_commits_per_project = max_commits_per_project  # None means no limit
        self.total_user_commits = 0
        
        # AI Provider configuration
        self.ai_provider = self._setup_ai_provider(model_provider, model_name)
        
        self.user_email = None
        self.user_name = None
        self.user_emails = set()  # Track multiple possible emails
        self.user_names = set()   # Track multiple possible names
        
    def get_user_info(self):
        """Get authenticated user information for commit filtering"""
        if self.github_token:
            try:
                headers = {'Authorization': f'token {self.github_token}'}
                response = requests.get('https://api.github.com/user', headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    email = user_data.get('email')
                    name = user_data.get('name') or user_data.get('login')
                    login = user_data.get('login')
                    
                    if email:
                        self.user_emails.add(email.lower())
                        if not self.user_email:
                            self.user_email = email
                    
                    if name:
                        self.user_names.add(name.lower())
                        if not self.user_name:
                            self.user_name = name
                    
                    if login:
                        self.user_names.add(login.lower())
                    
                    print(f"GitHub user: {name} ({email}) [login: {login}]")
                    
                    # Also try to get user emails from GitHub API
                    emails_response = requests.get('https://api.github.com/user/emails', headers=headers)
                    if emails_response.status_code == 200:
                        emails_data = emails_response.json()
                        for email_info in emails_data:
                            if email_info.get('email'):
                                self.user_emails.add(email_info['email'].lower())
                        print(f"Found {len(self.user_emails)} GitHub email addresses")
                        
            except Exception as e:
                print(f"Error getting GitHub user info: {e}")
        
        if self.gitlab_token:
            try:
                headers = {'Authorization': f'Bearer {self.gitlab_token}'}
                response = requests.get(f'{self.gitlab_url}/api/v4/user', headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    email = user_data.get('email')
                    name = user_data.get('name') or user_data.get('username')
                    username = user_data.get('username')
                    
                    if email:
                        self.user_emails.add(email.lower())
                        if not self.user_email:
                            self.user_email = email
                    
                    if name:
                        self.user_names.add(name.lower())
                        if not self.user_name:
                            self.user_name = name
                    
                    if username:
                        self.user_names.add(username.lower())
                    
                    print(f"GitLab user: {name} ({email}) [username: {username}]")
                    
            except Exception as e:
                print(f"Error getting GitLab user info: {e}")
        
        print(f"Debug: Tracking {len(self.user_emails)} emails and {len(self.user_names)} names for commit matching")
        if self.user_emails:
            print(f"  Emails: {', '.join(sorted(self.user_emails))}")
        if self.user_names:
            print(f"  Names: {', '.join(sorted(self.user_names))}")
    
    def _is_user_commit(self, author_email: str, author_name: str) -> bool:
        """Check if a commit is by the authenticated user using flexible matching"""
        author_email = author_email.lower()
        author_name = author_name.lower()
        
        # Check against all known emails
        if author_email and author_email in self.user_emails:
            return True
        
        # Check against all known names
        if author_name and author_name in self.user_names:
            return True
        
        # Fallback to original logic if no matches found
        if self.user_email and author_email and self.user_email.lower() == author_email:
            return True
        elif self.user_name and author_name and self.user_name.lower() == author_name:
            return True
        
        return False
    
    def _setup_ai_provider(self, provider: str = None, model: str = None) -> AIProvider:
        """Set up the AI provider based on configuration"""
        # Default to gemini-2.5-pro if no provider specified
        if provider is None:
            provider = "google"
        if model is None:
            model = "gemini-2.5-pro"
        
        # Get API keys
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Setup provider
        if provider.lower() == "anthropic":
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider")
            return AnthropicProvider(anthropic_key, model)
        elif provider.lower() == "openai":
            if not openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
            return OpenAIProvider(openai_key, model)
        elif provider.lower() == "google":
            if not gemini_key:
                raise ValueError("GEMINI_API_KEY environment variable is required for Google provider")
            return GeminiProvider(gemini_key, model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}. Supported: anthropic, openai, google")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current AI model"""
        return self.ai_provider.get_model_info()
    
    def count_user_commits(self, commits: List[Dict[str, Any]]) -> int:
        """Count commits made by the authenticated user"""
        if not commits:
            return 0
            
        user_commits = 0
        for commit in commits:
            author_email = commit.get('author_email', '').lower()
            author_name = commit.get('author', '').lower()
            
            if self._is_user_commit(author_email, author_name):
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
                readme_content = readme_content.strip()
                # Only include README if it's not empty
                if readme_content:
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
            total_commits_in_repo = 0  # Track total commits from all users
            page = 1
            while True:
                commits_response = requests.get(f'https://api.github.com/repos/{repo_full_name}/commits?per_page=100&page={page}', headers=headers)
                if commits_response.status_code != 200:
                    break
                    
                commits_data = commits_response.json()
                if not commits_data:
                    break
                
                # Count all commits in the repository
                total_commits_in_repo += len(commits_data)
                
                # Filter commits to only include user commits
                for commit in commits_data:
                    author_email = commit['commit']['author'].get('email', '').lower()
                    author_name = commit['commit']['author']['name'].lower()
                    commit_message = commit['commit']['message'].strip()
                    
                    # Include all user commits (no deduplication at this stage)
                    if self._is_user_commit(author_email, author_name):
                        user_commits.append({
                            'message': commit_message,
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
            details['total_commits_fetched'] = total_commits_in_repo  # Total commits from all users
                
        except Exception as e:
            print(f"Error fetching commits for {repo_full_name}: {e}")
            details['user_commits_count'] = 0
            details['total_commits_fetched'] = 0
        
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
                
                # Only include counts if they are > 0
                watchers_count = repo_data.get('watchers_count', 0)
                if watchers_count > 0:
                    details['watchers_count'] = watchers_count
                
                network_count = repo_data.get('network_count', 0)
                if network_count > 0:
                    details['network_count'] = network_count
                
                subscribers_count = repo_data.get('subscribers_count', 0)
                if subscribers_count > 0:
                    details['subscribers_count'] = subscribers_count
                
                # Ignore these attributes: has_issues, has_projects, has_wiki, has_pages, default_branch, open_issues_count, language
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
                readme_content = readme_response.text.strip()
                # Only include README if it's not empty
                if readme_content:
                    details['readme'] = readme_content[:2000]  # Limit to 2000 chars
            else:
                # Try other common README names
                for readme_name in ['README.rst', 'README.txt', 'README']:
                    readme_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/files/{readme_name}/raw?ref=HEAD', headers=headers)
                    if readme_response.status_code == 200:
                        readme_content = readme_response.text.strip()
                        # Only include README if it's not empty
                        if readme_content:
                            details['readme'] = readme_content[:2000]
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
            total_commits_in_repo = 0  # Track total commits from all users
            page = 1
            while True:
                commits_response = requests.get(f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/commits?per_page=100&page={page}', headers=headers)
                if commits_response.status_code != 200:
                    break
                    
                commits_data = commits_response.json()
                if not commits_data:
                    break
                
                # Count all commits in the repository
                total_commits_in_repo += len(commits_data)
                
                # Filter commits to only include user commits
                for commit in commits_data:
                    author_email = commit['author_email'].lower()
                    author_name = commit['author_name'].lower()
                    commit_message = commit['message'].strip()
                    
                    # Include all user commits (no deduplication at this stage)
                    if self._is_user_commit(author_email, author_name):
                        user_commits.append({
                            'message': commit_message,
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
            details['total_commits_fetched'] = total_commits_in_repo  # Total commits from all users
                
        except Exception as e:
            print(f"Error fetching commits for project {project_id}: {e}")
            details['user_commits_count'] = 0
            details['total_commits_fetched'] = 0
        
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
    
    def estimate_lines_of_code(self, projects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Estimate lines of code based on file extensions and project structure"""
        # Average lines per file by extension (rough estimates)
        lines_per_file = {
            'py': 150, 'js': 120, 'ts': 120, 'java': 200, 'cpp': 180, 'c': 160,
            'cs': 180, 'php': 140, 'rb': 120, 'go': 140, 'rs': 160, 'swift': 140,
            'kt': 160, 'html': 80, 'css': 60, 'scss': 70, 'sass': 70, 'vue': 100,
            'jsx': 120, 'tsx': 120, 'sql': 30, 'r': 100, 'matlab': 120, 'sh': 40,
            'yml': 20, 'yaml': 20, 'json': 15, 'xml': 25, 'md': 50, 'txt': 25
        }
        
        total_lines = 0
        language_lines = {}
        
        for project in projects:
            if 'languages' in project:
                for lang, byte_count in project['languages'].items():
                    # Rough conversion: bytes to lines (assuming avg 60 chars per line)
                    estimated_lines = max(1, byte_count // 60)
                    language_lines[lang] = language_lines.get(lang, 0) + estimated_lines
                    total_lines += estimated_lines
            elif 'folder_structure' in project and 'file_types' in project['folder_structure']:
                # Fallback: estimate from file types
                file_types = project['folder_structure']['file_types']
                for ext, count in file_types.items():
                    if ext in lines_per_file:
                        estimated_lines = count * lines_per_file[ext]
                        # Map extension to language
                        lang_mapping = {
                            'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
                            'java': 'Java', 'cpp': 'C++', 'c': 'C', 'cs': 'C#',
                            'php': 'PHP', 'rb': 'Ruby', 'go': 'Go', 'rs': 'Rust',
                            'swift': 'Swift', 'kt': 'Kotlin', 'html': 'HTML',
                            'css': 'CSS', 'scss': 'SCSS', 'sass': 'Sass',
                            'vue': 'Vue', 'jsx': 'React', 'tsx': 'React TypeScript'
                        }
                        lang = lang_mapping.get(ext, ext.upper())
                        language_lines[lang] = language_lines.get(lang, 0) + estimated_lines
                        total_lines += estimated_lines
        
        return {
            'total_lines': total_lines,
            'by_language': language_lines
        }
    
    def clean_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Clean project data by removing unwanted attributes and simplifying user_commits"""
        cleaned_project = project.copy()
        
        # Remove unwanted attributes and large data structures
        attrs_to_remove = [
            'files',  # Remove file lists (can be very large)
            'meets_commit_threshold',
            'topics',
            'is_fork',
            'is_private',
            'size',
            'recent_commits'
        ]
        
        for attr in attrs_to_remove:
            cleaned_project.pop(attr, None)
        
        # Simplify folder_structure to reduce JSON size
        if 'folder_structure' in cleaned_project and isinstance(cleaned_project['folder_structure'], dict):
            folder_structure = cleaned_project['folder_structure']
            
            # Remove folders list (can be very large)
            folder_structure.pop('folders', None)
            
            # Limit file_types to top 5 most common
            if 'file_types' in folder_structure and isinstance(folder_structure['file_types'], dict):
                file_types = folder_structure['file_types']
                # Keep only top 5 file types
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]
                folder_structure['file_types'] = dict(sorted_types)
        
        # Keep README content as-is (no truncation)
        # Keep all languages (no limitation)
        
        # Clean user_commits with optional size reduction for JSON
        if 'user_commits' in cleaned_project and isinstance(cleaned_project['user_commits'], list):
            cleaned_commits = []
            seen_messages = set()  # Track seen messages to filter duplicates
            
            # Sort commits by date (most recent first)
            commits_list = cleaned_project['user_commits']
            if commits_list:
                # Sort by date (most recent first)
                try:
                    commits_list = sorted(commits_list, key=lambda x: x.get('date', ''), reverse=True)
                except:
                    pass  # If sorting fails, use original order
                
                # Apply user-specified commit limit if set
                if self.max_commits_per_project is not None:
                    commits_list = commits_list[:self.max_commits_per_project]
                    print(f"    DEBUG: Limited to {self.max_commits_per_project} most recent commits per user request")
            
            for commit in commits_list:
                if isinstance(commit, dict):
                    message = commit.get('message', '').strip()
                    
                    # Keep original commit message length (no truncation)
                    # Only include if message hasn't been seen (duplicate filtering for JSON size)
                    if message not in seen_messages:
                        seen_messages.add(message)
                        cleaned_commit = {
                            'message': message,
                            'date': commit.get('date', '')
                        }
                        cleaned_commits.append(cleaned_commit)
            
            cleaned_project['user_commits'] = cleaned_commits
            
            # Update user_commits_count to reflect the deduplicated count in JSON
            # But keep original count for filtering logic
            original_count = cleaned_project.get('user_commits_count', 0)
            deduplicated_count = len(cleaned_commits)
            
            # Add debug info about filtering
            if original_count > deduplicated_count:
                print(f"    DEBUG: Filtered {original_count - deduplicated_count} duplicate commit messages for JSON output")
            
            # Keep original count for threshold logic, but note deduplicated count
            cleaned_project['user_commits_count'] = original_count
            cleaned_project['user_commits_deduplicated_count'] = deduplicated_count
        
        # Note: Conditional attributes (stars, forks, description, readme, watchers_count, etc.) 
        # are already handled in the processing methods and only included if they meet criteria
        
        return cleaned_project
    
    def estimate_json_size(self, projects: List[Dict[str, Any]]) -> int:
        """Estimate JSON size in characters (approximates tokens)"""
        try:
            json_str = json.dumps(projects, indent=2)
            return len(json_str)
        except:
            return 0
    
    def reduce_json_size_further(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Further reduce JSON size if it's still too large by simplifying folder structure"""
        print("    WARNING: JSON size is still large. Simplifying folder structure only.")
        print("    Consider using --max-commits option to limit commits per project.")
        
        for project in projects:
            # Only reduce folder structure, respect user preferences for commits/README/languages
            if 'folder_structure' in project:
                # Keep only essential info
                folder_structure = project['folder_structure']
                if isinstance(folder_structure, dict):
                    essential_structure = {
                        'project_type': folder_structure.get('project_type', 'general'),
                        'total_files': folder_structure.get('total_files', 0)
                    }
                    # Keep only top 3 file types
                    if 'file_types' in folder_structure:
                        file_types = folder_structure['file_types']
                        if isinstance(file_types, dict) and file_types:
                            sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
                            essential_structure['file_types'] = dict(sorted_types)
                    project['folder_structure'] = essential_structure
        
        return projects
    
    def process_github_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub repository data with detailed information"""
        processed_repo = {
            'platform': 'GitHub',
            'name': repo['name'],
            'full_name': repo['full_name'],
            'url': repo['html_url'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'topics': repo.get('topics', []),
            'is_fork': repo['fork'],
            'is_private': repo['private'],
            'size': repo.get('size', 0)
        }
        
        # Only include description if it's not null/empty
        description = repo.get('description')
        if description:
            processed_repo['description'] = description
        
        # Only include stars if > 0
        stars = repo.get('stargazers_count', 0)
        if stars > 0:
            processed_repo['stars'] = stars
        
        # Only include forks if > 0
        forks = repo.get('forks_count', 0)
        if forks > 0:
            processed_repo['forks'] = forks
        
        # Ignore language attribute as specified
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['full_name']}...")
        details = self.fetch_github_repo_details(repo['full_name'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        self.total_user_commits += user_commits
        
        # Debug output for commit counting
        if user_commits == 0:
            print(f"    DEBUG: No user commits found for {repo['full_name']}")
            if not self.user_emails and not self.user_names:
                print(f"    DEBUG: No user identification info available (check tokens and API access)")
        else:
            print(f"    Found {user_commits} user commits")
        
        return processed_repo
    
    def process_gitlab_repo(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitLab repository data with detailed information"""
        processed_repo = {
            'platform': 'GitLab',
            'name': repo['name'],
            'full_name': repo['path_with_namespace'],
            'url': repo['web_url'],
            'created_at': repo['created_at'],
            'updated_at': repo['last_activity_at'],
            'topics': repo.get('topics', []),
            'is_fork': repo.get('forked_from_project') is not None,
            'is_private': repo['visibility'] == 'private',
            'size': 0  # GitLab doesn't provide size in basic API
        }
        
        # Only include description if it's not null/empty
        description = repo.get('description')
        if description:
            processed_repo['description'] = description
        
        # Only include stars if > 0
        stars = repo.get('star_count', 0)
        if stars > 0:
            processed_repo['stars'] = stars
        
        # Only include forks if > 0
        forks = repo.get('forks_count', 0)
        if forks > 0:
            processed_repo['forks'] = forks
        
        # Ignore language attribute as specified
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['path_with_namespace']}...")
        details = self.fetch_gitlab_repo_details(repo['id'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        self.total_user_commits += user_commits
        
        # Debug output for commit counting
        if user_commits == 0:
            print(f"    DEBUG: No user commits found for {repo['path_with_namespace']}")
            if not self.user_emails and not self.user_names:
                print(f"    DEBUG: No user identification info available (check tokens and API access)")
        else:
            print(f"    Found {user_commits} user commits")
        
        return processed_repo
    
    def generate_summary(self, projects: List[Dict[str, Any]]) -> str:
        """Generate portfolio summary using Anthropic API"""
        project_data = json.dumps(projects, indent=2)
        
        # Get top 5 projects by various metrics
        top_projects_by_commits = sorted(projects, key=lambda p: p.get('user_commits_count', 0), reverse=True)[:5]
        top_projects_by_stars = sorted([p for p in projects if p.get('stars', 0) > 0], key=lambda p: p.get('stars', 0), reverse=True)[:5]
        
        # Calculate lines of code estimation
        lines_data = self.estimate_lines_of_code(projects)
        total_lines = lines_data['total_lines']
        lines_by_language = lines_data['by_language']
        
        # Format top projects summary
        top_projects_summary = []
        for project in top_projects_by_commits:
            summary = {
                'name': project.get('name', 'Unknown'),
                'commits': project.get('user_commits_count', 0),
                'stars': project.get('stars', 0),
                'description': project.get('description', ''),
                'languages': list(project.get('languages', {}).keys())[:3],
                'project_type': project.get('folder_structure', {}).get('project_type', 'general')
            }
            top_projects_summary.append(summary)
        
        prompt = f"""
You are a professional portfolio writer and technical recruiter. Based on the following detailed project data from GitHub and GitLab repositories, create a comprehensive portfolio summary that highlights the developer's skills, contributions, and expertise.

**Key Statistics:**
- Total Projects: {len(projects)}
- Total User Commits: {sum(p.get('user_commits_count', 0) for p in projects)}
- Total Stars Earned: {sum(p.get('stars', 0) for p in projects)}
- Estimated Lines of Code: {total_lines:,}
- Top Languages by Lines: {', '.join([f'{lang} ({lines:,})' for lang, lines in sorted(lines_by_language.items(), key=lambda x: x[1], reverse=True)[:5]])}

**Top 5 Projects by Contribution:**
{json.dumps(top_projects_summary, indent=2)}

Project Data includes:
- Repository metadata (stars, forks, dates, topics, commit counts)
- README content providing project context and documentation quality
- Folder structure and file organization showing architectural understanding
- Programming languages and technologies with usage statistics
- Commit history showing development patterns and consistency
- Project types and complexity indicators
- Code quality metrics (stars, forks, activity levels)

Project Data:
{project_data}

Please create a comprehensive portfolio summary with the following sections:

## 1. Executive Summary
- Developer profile overview with estimated lines of code ({total_lines:,})
- Years of experience estimation based on project timeline
- Primary technical focus areas
- Notable achievements and standout projects

## 2. Top 5 Featured Projects
Create a detailed section highlighting the top 5 projects from the summary above, including:
- Project name and description
- Technical stack and complexity
- Your contribution level (commits, impact)
- Key features and innovations
- Business value and real-world applicability

## 3. Technical Skills & Expertise
- Programming languages (ranked by proficiency evidence and lines of code)
- Frameworks and libraries (with usage context)
- Development tools and environments
- Architecture patterns and design principles demonstrated
- Database technologies and data handling
- DevOps and deployment practices

## 4. Project Portfolio Analysis
- Most significant projects (based on commits, complexity, and impact)
- Project diversity and problem-solving range
- Evidence of full-stack capabilities
- Open source contributions and community engagement
- Commercial vs. personal project balance

## 5. Development Practices & Code Quality
- Code organization and architectural patterns
- Documentation quality and README standards
- Commit message quality and development workflow
- Testing practices and quality assurance
- Version control and collaboration patterns

## 6. Professional Growth & Learning
- Technology adoption timeline
- Increasing project complexity over time
- Learning new technologies and adaptation
- Problem-solving evolution and expertise development

## 7. Standout Qualities
- Unique technical combinations or specializations
- Innovation and creative problem-solving
- Leadership and mentoring evidence
- Industry-specific expertise

## 8. Portfolio Presentation Recommendations
- Which projects to highlight in interviews
- Technical talking points for each major project
- Areas of expertise to emphasize
- Potential areas for continued development

Analysis Guidelines:
- Weight projects by commit count, stars, forks, and recent activity
- Consider README quality as documentation/communication skills indicator
- Evaluate technology stack diversity and depth
- Look for patterns in commit messages showing professional development practices
- Assess project complexity through folder structure and file types
- Consider real-world applicability and business value of projects
- Emphasize the estimated {total_lines:,} lines of code as a measure of coding experience

Format the response in professional markdown suitable for portfolio presentation.
"""

        try:
            return self.ai_provider.generate_summary(prompt)
        except Exception as e:
            print(f"Error generating summary with AI provider: {e}")
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
    
    def run_stage_1(self, github_username: str = None, gitlab_username: str = None, platform: str = None):
        """Stage 1: Get JSON data from repositories"""
        print("Stage 1: Fetching repository data...")
        
        # Get user information for commit filtering
        self.get_user_info()
        
        all_projects = []
        
        # Check platform restrictions
        fetch_gitlab = platform is None or platform == 'gitlab'
        fetch_github = platform is None or platform == 'github'
        
        # Fetch GitLab repositories
        if fetch_gitlab and (self.gitlab_token or gitlab_username):
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
        elif not fetch_gitlab:
            print("Skipping GitLab repositories due to --platform restriction")

        # Fetch GitHub repositories
        if fetch_github and (self.github_token or github_username):
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
        elif not fetch_github:
            print("Skipping GitHub repositories due to --platform restriction")

        if not all_projects:
            print("No projects found. Please check your credentials and usernames.")
            print("\nDEBUG: Troubleshooting tips:")
            print("1. Verify your GitHub/GitLab tokens have the correct permissions")
            print("2. Check if user info was retrieved correctly (see output above)")
            print("3. Try lowering --min-commits if you have commits but they're not being counted")
            print("4. Ensure your commit email matches your GitHub/GitLab account email")
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
        
        # Estimate JSON size and reduce if necessary
        json_size = self.estimate_json_size(projects_data)
        print(f"Estimated JSON size: {json_size:,} characters")
        
        # If JSON is too large, apply further reduction
        if json_size > 150000:  # Conservative limit to stay under 200k tokens
            print("JSON size is large, applying further reduction...")
            projects_data = self.reduce_json_size_further(projects_data)
            new_size = self.estimate_json_size(projects_data)
            print(f"Reduced JSON size to: {new_size:,} characters")
        
        print("Generating portfolio summary...")
        summary = self.generate_summary(projects_data)
        
        # Save files
        self.save_results(projects_data, summary)
        
        print(f"Stage 2 completed! Portfolio summary generated.")
        return summary
    
    
    def run(self, github_username: str = None, gitlab_username: str = None, use_existing_data: bool = False, stage: int = None, platform: str = None):
        """Main execution method with stage support"""
        print("Starting portfolio generation...")
        
        # Show model info
        model_info = self.get_model_info()
        print(f"Using AI Model: {model_info['provider'].upper()} {model_info['model']}")
        if model_info['is_free']:
            print("  - Free tier available")
        if model_info['has_reasoning']:
            print("  - Has reasoning capabilities")
        if model_info['is_cheaper']:
            print("  - Cheaper option")
        print()
        
        # Handle stage-specific execution
        if stage == 1:
            print("Running Stage 1 only: Data collection")
            self.run_stage_1(github_username, gitlab_username, platform)
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
        projects_data = self.run_stage_1(github_username, gitlab_username, platform)
        if projects_data:
            self.run_stage_2(projects_data)
            print("\nPortfolio generation completed!")
            print("\nFiles generated:")
            print("- Portfolio Summary: Comprehensive overview and analysis")
            print("- Raw Data: Complete JSON data for further analysis")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate portfolio from GitHub and GitLab projects")
    parser.add_argument("--github-username", help="GitHub username (optional if using token)")
    parser.add_argument("--gitlab-username", help="GitLab username (optional if using token)")
    parser.add_argument("--use-existing", action="store_true", help="Use the most recent portfolio data file instead of fetching new data")
    parser.add_argument("--stage", type=int, choices=[1, 2], help="Run specific stage: 1=get JSON data, 2=analyze data (default: run both stages)")
    parser.add_argument("--min-commits", type=int, default=1, help="Minimum user commits required for a project to be included (default: 1)")
    parser.add_argument("--platform", choices=['github', 'gitlab'], help="Analyze only specific platform in stage 1 (default: analyze both)")
    parser.add_argument("--max-commits", type=int, help="Maximum commits per project to include in JSON (default: all commits)")
    parser.add_argument("--model-provider", choices=['anthropic', 'openai', 'google'], default='google', help="AI provider to use (default: google)")
    parser.add_argument("--model-name", help="Specific model name to use (default: gemini-2.5-pro)")
    
    args = parser.parse_args()
    
    try:
        generator = PortfolioGenerator(
            min_commits=args.min_commits, 
            max_commits_per_project=args.max_commits,
            model_provider=args.model_provider,
            model_name=args.model_name
        )
        generator.run(args.github_username, args.gitlab_username, args.use_existing, args.stage, args.platform)
    except Exception as e:
        print(f"Error: {e}")