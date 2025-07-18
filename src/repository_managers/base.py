from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
import requests
import time


class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class RepositoryAPIError(RepositoryError):
    """API error for repository operations"""
    pass


class RepositoryManager(ABC):
    """Abstract base class for repository managers"""
    
    def __init__(self, token: Optional[str] = None, min_commits: int = 1, max_commits_per_project: Optional[int] = None):
        self.token = token
        self.min_commits = min_commits
        self.max_commits_per_project = max_commits_per_project
        self.user_emails: Set[str] = set()
        self.user_names: Set[str] = set()
        self.user_email: Optional[str] = None
        self.user_name: Optional[str] = None
        
    @abstractmethod
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        pass
    
    @abstractmethod
    def fetch_repositories(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch repositories from the platform"""
        pass
    
    @abstractmethod
    def fetch_repository_details(self, repo_identifier: str) -> Dict[str, Any]:
        """Fetch detailed information about a repository"""
        pass
    
    @abstractmethod
    def process_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Process repository data with platform-specific logic"""
        pass
    
    def is_user_commit(self, author_email: str, author_name: str) -> bool:
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
    
    def rate_limit_sleep(self, duration: float = 0.1) -> None:
        """Sleep to respect rate limits"""
        time.sleep(duration)
    
    def make_request(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> requests.Response:
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            self.rate_limit_sleep()
            return response
        except requests.exceptions.RequestException as e:
            raise RepositoryAPIError(f"Request failed: {e}")