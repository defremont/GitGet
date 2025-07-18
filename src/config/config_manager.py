import os
from typing import Dict, Optional


class ConfigManager:
    """Manager for environment variables and configuration"""
    
    @staticmethod
    def get_github_token() -> Optional[str]:
        """Get GitHub token from environment"""
        return os.getenv('GITHUB_TOKEN')
    
    @staticmethod
    def get_gitlab_token() -> Optional[str]:
        """Get GitLab token from environment"""
        return os.getenv('GITLAB_TOKEN')
    
    @staticmethod
    def get_gitlab_url() -> str:
        """Get GitLab URL from environment or default"""
        return os.getenv('GITLAB_URL', 'https://gitlab.com')
    
    @staticmethod
    def get_ai_api_keys() -> Dict[str, Optional[str]]:
        """Get all AI API keys from environment"""
        return {
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'google': os.getenv('GEMINI_API_KEY')  # Google provider uses GEMINI_API_KEY
        }
    
    @staticmethod
    def validate_ai_provider_key(provider: str) -> bool:
        """Validate that the required API key is available for the provider"""
        keys = ConfigManager.get_ai_api_keys()
        return keys.get(provider.lower()) is not None
    
    @staticmethod
    def get_default_model_for_provider(provider: str) -> str:
        """Get default model name for a provider"""
        defaults = {
            'anthropic': 'claude-3-5-haiku-latest',
            'openai': 'gpt-4.1-nano',
            'google': 'gemini-2.5-pro'
        }
        return defaults.get(provider.lower(), 'gemini-2.5-pro')
    
    @staticmethod
    def print_environment_status() -> None:
        """Print status of environment variables"""
        print("Environment Configuration:")
        print(f"  GitHub Token: {'SET' if ConfigManager.get_github_token() else 'NOT SET'}")
        print(f"  GitLab Token: {'SET' if ConfigManager.get_gitlab_token() else 'NOT SET'}")
        print(f"  GitLab URL: {ConfigManager.get_gitlab_url()}")
        
        # Show actual environment variable names
        env_vars = {
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
        }
        print("  AI API Keys:")
        for env_var, key in env_vars.items():
            provider_name = env_var.replace('_API_KEY', '').replace('GEMINI', 'GOOGLE').title()
            print(f"    {env_var} ({provider_name}): {'SET' if key else 'NOT SET'}")
        print()