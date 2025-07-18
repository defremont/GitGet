from dataclasses import dataclass
from typing import Optional


@dataclass
class PortfolioConfig:
    """Configuration class for portfolio generation"""
    
    # Repository settings
    github_username: Optional[str] = None
    gitlab_username: Optional[str] = None
    platform: Optional[str] = None  # 'github', 'gitlab', or None for both
    
    # Commit filtering
    min_commits: int = 1
    max_commits_per_project: Optional[int] = None
    
    # AI provider settings
    model_provider: str = "google"
    model_name: Optional[str] = None
    
    # Processing settings
    use_existing_data: bool = False
    stage: Optional[int] = None  # 1, 2, or None for both
    
    # GitLab specific
    gitlab_url: str = "https://gitlab.com"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.platform and self.platform not in ['github', 'gitlab']:
            raise ValueError(f"Invalid platform: {self.platform}. Must be 'github' or 'gitlab'")
        
        if self.stage and self.stage not in [1, 2]:
            raise ValueError(f"Invalid stage: {self.stage}. Must be 1 or 2")
        
        if self.min_commits < 0:
            raise ValueError("min_commits must be non-negative")
        
        if self.max_commits_per_project is not None and self.max_commits_per_project < 1:
            raise ValueError("max_commits_per_project must be positive if specified")
        
        if self.model_provider not in ['anthropic', 'openai', 'google']:
            raise ValueError(f"Invalid model provider: {self.model_provider}. Must be 'anthropic', 'openai', or 'google'")
    
    @classmethod
    def from_args(cls, args) -> 'PortfolioConfig':
        """Create configuration from command line arguments"""
        return cls(
            github_username=args.github_username,
            gitlab_username=args.gitlab_username,
            platform=args.platform,
            min_commits=args.min_commits,
            max_commits_per_project=args.max_commits,
            model_provider=args.model_provider,
            model_name=args.model_name,
            use_existing_data=args.use_existing,
            stage=args.stage,
            gitlab_url=getattr(args, 'gitlab_url', 'https://gitlab.com')
        )