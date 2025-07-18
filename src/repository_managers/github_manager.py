from typing import List, Dict, Any, Optional
import base64
import requests
from .base import RepositoryManager, RepositoryAPIError


class GitHubManager(RepositoryManager):
    """GitHub repository manager"""
    
    def __init__(self, token: Optional[str] = None, min_commits: int = 1, max_commits_per_project: Optional[int] = None):
        super().__init__(token, min_commits, max_commits_per_project)
        self.base_url = "https://api.github.com"
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        return headers
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information for commit filtering"""
        if not self.token:
            print("Warning: GITHUB_TOKEN not set, will only fetch public repos with rate limits")
            return {}
        
        try:
            headers = self.get_headers()
            response = self.make_request(f'{self.base_url}/user', headers)
            
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
                
                # Get additional user emails
                emails_response = self.make_request(f'{self.base_url}/user/emails', headers)
                if emails_response.status_code == 200:
                    emails_data = emails_response.json()
                    for email_info in emails_data:
                        if email_info.get('email'):
                            self.user_emails.add(email_info['email'].lower())
                    print(f"Found {len(self.user_emails)} GitHub email addresses")
                
                return user_data
                
        except Exception as e:
            print(f"Error getting GitHub user info: {e}")
            
        return {}
    
    def fetch_repositories(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch repositories from GitHub"""
        headers = self.get_headers()
        repos = []
        
        if username:
            url = f'{self.base_url}/users/{username}/repos'
        else:
            url = f'{self.base_url}/user/repos'
        
        page = 1
        while True:
            response = self.make_request(f'{url}?page={page}&per_page=100', headers)
            
            if response.status_code != 200:
                print(f"Error fetching GitHub repos: {response.status_code}")
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
        
        return repos
    
    def fetch_repository_details(self, repo_full_name: str) -> Dict[str, Any]:
        """Fetch detailed information about a GitHub repository"""
        headers = self.get_headers()
        details = {}
        
        # Fetch README
        self._fetch_readme(repo_full_name, headers, details)
        
        # Fetch repository tree
        self._fetch_repository_tree(repo_full_name, headers, details)
        
        # Fetch user commits
        self._fetch_user_commits(repo_full_name, headers, details)
        
        # Fetch languages
        self._fetch_languages(repo_full_name, headers, details)
        
        # Fetch repository stats
        self._fetch_repository_stats(repo_full_name, headers, details)
        
        return details
    
    def _fetch_readme(self, repo_full_name: str, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch README content"""
        try:
            response = self.make_request(f'{self.base_url}/repos/{repo_full_name}/readme', headers)
            if response.status_code == 200:
                readme_data = response.json()
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                readme_content = readme_content.strip()
                if readme_content:
                    details['readme'] = readme_content[:2000]  # Limit to 2000 chars
        except Exception as e:
            print(f"Error fetching README for {repo_full_name}: {e}")
    
    def _fetch_repository_tree(self, repo_full_name: str, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch repository tree structure"""
        try:
            response = self.make_request(f'{self.base_url}/repos/{repo_full_name}/git/trees/HEAD?recursive=1', headers)
            if response.status_code == 200:
                tree_data = response.json()
                files = [item['path'] for item in tree_data.get('tree', []) if item['type'] == 'blob']
                details['files'] = files[:100]  # Limit to 100 files
                details['folder_structure'] = self._analyze_folder_structure(files)
        except Exception as e:
            print(f"Error fetching tree for {repo_full_name}: {e}")
    
    def _fetch_user_commits(self, repo_full_name: str, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch user commits from repository"""
        try:
            user_commits = []
            total_commits_in_repo = 0
            page = 1
            
            while True:
                response = self.make_request(f'{self.base_url}/repos/{repo_full_name}/commits?per_page=100&page={page}', headers)
                if response.status_code != 200:
                    break
                    
                commits_data = response.json()
                if not commits_data:
                    break
                
                total_commits_in_repo += len(commits_data)
                
                for commit in commits_data:
                    author_email = commit['commit']['author'].get('email', '').lower()
                    author_name = commit['commit']['author']['name'].lower()
                    commit_message = commit['commit']['message'].strip()
                    
                    if self.is_user_commit(author_email, author_name):
                        user_commits.append({
                            'message': commit_message,
                            'date': commit['commit']['author']['date'],
                            'author': commit['commit']['author']['name'],
                            'author_email': commit['commit']['author'].get('email', ''),
                            'sha': commit['sha'][:8]
                        })
                
                page += 1
                if page > 20:  # Limit to avoid infinite loops
                    break
                        
            details['user_commits'] = user_commits
            details['recent_commits'] = user_commits[:20]  # Keep for backward compatibility
            details['user_commits_count'] = len(user_commits)
            details['total_commits_fetched'] = total_commits_in_repo
                
        except Exception as e:
            print(f"Error fetching commits for {repo_full_name}: {e}")
            details['user_commits_count'] = 0
            details['total_commits_fetched'] = 0
    
    def _fetch_languages(self, repo_full_name: str, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch repository languages"""
        try:
            response = self.make_request(f'{self.base_url}/repos/{repo_full_name}/languages', headers)
            if response.status_code == 200:
                details['languages'] = response.json()
        except Exception as e:
            print(f"Error fetching languages for {repo_full_name}: {e}")
    
    def _fetch_repository_stats(self, repo_full_name: str, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch additional repository statistics"""
        try:
            response = self.make_request(f'{self.base_url}/repos/{repo_full_name}', headers)
            if response.status_code == 200:
                repo_data = response.json()
                
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
                    
        except Exception as e:
            print(f"Error fetching repo stats for {repo_full_name}: {e}")
    
    def _analyze_folder_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze folder structure from file paths"""
        from ..utils.file_analyzer import FileAnalyzer
        return FileAnalyzer.analyze_folder_structure(files)
    
    def process_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Only include non-empty descriptions
        description = repo.get('description')
        if description:
            processed_repo['description'] = description
        
        # Only include positive values
        stars = repo.get('stargazers_count', 0)
        if stars > 0:
            processed_repo['stars'] = stars
        
        forks = repo.get('forks_count', 0)
        if forks > 0:
            processed_repo['forks'] = forks
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['full_name']}...")
        details = self.fetch_repository_details(repo['full_name'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        
        # Debug output
        if user_commits == 0:
            print(f"    DEBUG: No user commits found for {repo['full_name']}")
        else:
            print(f"    Found {user_commits} user commits")
        
        return processed_repo