from abc import ABC, abstractmethod
from typing import Dict, Any


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


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class AIProviderConfigError(AIProviderError):
    """Configuration error for AI providers"""
    pass


class AIProviderAPIError(AIProviderError):
    """API error for AI providers"""
    pass