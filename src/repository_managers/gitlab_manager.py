from typing import List, Dict, Any, Optional
import requests
from .base import RepositoryManager, RepositoryAPIError


class GitLabManager(RepositoryManager):
    """GitLab repository manager"""
    
    def __init__(self, token: Optional[str] = None, gitlab_url: str = "https://gitlab.com", 
                 min_commits: int = 1, max_commits_per_project: Optional[int] = None):
        super().__init__(token, min_commits, max_commits_per_project)
        self.gitlab_url = gitlab_url
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for GitLab API requests"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information for commit filtering"""
        if not self.token:
            print("Warning: GITLAB_TOKEN not set, will only fetch public repos")
            return {}
        
        try:
            headers = self.get_headers()
            response = self.make_request(f'{self.gitlab_url}/api/v4/user', headers)
            
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
                return user_data
                
        except Exception as e:
            print(f"Error getting GitLab user info: {e}")
            
        return {}
    
    def fetch_repositories(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch repositories from GitLab"""
        headers = self.get_headers()
        repos = []
        
        # Determine URL based on username or authentication
        if username:
            # First get user ID
            print(f"Looking up GitLab user: {username}")
            user_response = self.make_request(f'{self.gitlab_url}/api/v4/users?username={username}', headers)
            print(f"User lookup response: {user_response.status_code}")
            
            if user_response.status_code == 200 and user_response.json():
                user_id = user_response.json()[0]['id']
                url = f'{self.gitlab_url}/api/v4/users/{user_id}/projects'
                print(f"Using URL: {url}")
            else:
                print(f"Could not find GitLab user: {username}")
                return []
        else:
            if self.token:
                user_response = self.make_request(f'{self.gitlab_url}/api/v4/user', headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    print(f"Authenticated as: {user_data.get('username', 'Unknown')}")
                    url = f'{self.gitlab_url}/api/v4/projects?membership=true'
                else:
                    print(f"Authentication failed: {user_response.text}")
                    url = f'{self.gitlab_url}/api/v4/projects?simple=true'
            else:
                print("No GitLab token provided, fetching public projects")
                url = f'{self.gitlab_url}/api/v4/projects?visibility=public&simple=true'
        
        print(f"Fetching from URL: {url}")
        
        page = 1
        while True:
            try:
                if '?' in url:
                    response = self.make_request(f'{url}&page={page}&per_page=50', headers)
                else:
                    response = self.make_request(f'{url}?page={page}&per_page=50', headers)
                
                print(f"Page {page} response: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Error fetching GitLab repos: {response.status_code}")
                    if response.status_code == 401:
                        print("Authentication error - check your GITLAB_TOKEN")
                    elif response.status_code == 403:
                        print("Access forbidden - check token permissions")
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
                
            except requests.exceptions.RequestException as e:
                print(f"Network error on page {page}: {e}")
                break
            except KeyboardInterrupt:
                print("Interrupted by user")
                break
        
        return repos
    
    def fetch_repository_details(self, project_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a GitLab repository"""
        headers = self.get_headers()
        details = {}
        
        # Fetch README
        self._fetch_readme(project_id, headers, details)
        
        # Fetch repository tree
        self._fetch_repository_tree(project_id, headers, details)
        
        # Fetch user commits
        self._fetch_user_commits(project_id, headers, details)
        
        # Analyze languages from files
        if 'files' in details:
            details['languages'] = self._detect_languages_from_files(details['files'])
        
        return details
    
    def _fetch_readme(self, project_id: int, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch README content"""
        try:
            readme_names = ['README.md', 'README.rst', 'README.txt', 'README']
            
            for readme_name in readme_names:
                response = self.make_request(
                    f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/files/{readme_name}/raw?ref=HEAD',
                    headers
                )
                if response.status_code == 200:
                    readme_content = response.text.strip()
                    if readme_content:
                        details['readme'] = readme_content[:2000]
                        break
        except Exception as e:
            print(f"Error fetching README for project {project_id}: {e}")
    
    def _fetch_repository_tree(self, project_id: int, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch repository tree structure"""
        try:
            response = self.make_request(
                f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/tree?recursive=true&per_page=100',
                headers
            )
            if response.status_code == 200:
                tree_data = response.json()
                files = [item['path'] for item in tree_data if item['type'] == 'blob']
                details['files'] = files[:100]
                details['folder_structure'] = self._analyze_folder_structure(files)
        except Exception as e:
            print(f"Error fetching tree for project {project_id}: {e}")
    
    def _fetch_user_commits(self, project_id: int, headers: Dict[str, str], details: Dict[str, Any]) -> None:
        """Fetch user commits from repository"""
        try:
            user_commits = []
            total_commits_in_repo = 0
            page = 1
            
            while True:
                response = self.make_request(
                    f'{self.gitlab_url}/api/v4/projects/{project_id}/repository/commits?per_page=100&page={page}',
                    headers
                )
                if response.status_code != 200:
                    break
                    
                commits_data = response.json()
                if not commits_data:
                    break
                
                total_commits_in_repo += len(commits_data)
                
                for commit in commits_data:
                    author_email = commit['author_email'].lower()
                    author_name = commit['author_name'].lower()
                    commit_message = commit['message'].strip()
                    
                    if self.is_user_commit(author_email, author_name):
                        user_commits.append({
                            'message': commit_message,
                            'date': commit['created_at'],
                            'author': commit['author_name'],
                            'author_email': commit['author_email'],
                            'sha': commit['id'][:8]
                        })
                
                page += 1
                if page > 20:  # Limit to avoid infinite loops
                    break
                        
            details['user_commits'] = user_commits
            details['recent_commits'] = user_commits[:20]  # Keep for backward compatibility
            details['user_commits_count'] = len(user_commits)
            details['total_commits_fetched'] = total_commits_in_repo
                
        except Exception as e:
            print(f"Error fetching commits for project {project_id}: {e}")
            details['user_commits_count'] = 0
            details['total_commits_fetched'] = 0
    
    def _analyze_folder_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze folder structure from file paths"""
        from ..utils.file_analyzer import FileAnalyzer
        return FileAnalyzer.analyze_folder_structure(files)
    
    def _detect_languages_from_files(self, files: List[str]) -> Dict[str, int]:
        """Detect programming languages from file extensions"""
        from ..utils.file_analyzer import FileAnalyzer
        return FileAnalyzer.detect_languages_from_files(files)
    
    def process_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Only include non-empty descriptions
        description = repo.get('description')
        if description:
            processed_repo['description'] = description
        
        # Only include positive values
        stars = repo.get('star_count', 0)
        if stars > 0:
            processed_repo['stars'] = stars
        
        forks = repo.get('forks_count', 0)
        if forks > 0:
            processed_repo['forks'] = forks
        
        # Fetch detailed information
        print(f"  Fetching details for {repo['path_with_namespace']}...")
        details = self.fetch_repository_details(repo['id'])
        processed_repo.update(details)
        
        # Filter repositories with at least min_commits user commits
        user_commits = processed_repo.get('user_commits_count', 0)
        processed_repo['meets_commit_threshold'] = user_commits >= self.min_commits
        
        # Debug output
        if user_commits == 0:
            print(f"    DEBUG: No user commits found for {repo['path_with_namespace']}")
        else:
            print(f"    Found {user_commits} user commits")
        
        return processed_repo