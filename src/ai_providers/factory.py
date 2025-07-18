import os
from typing import Optional
from .base import AIProvider, AIProviderConfigError
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider


class AIProviderFactory:
    """Factory for creating AI providers"""
    
    @staticmethod
    def create_provider(
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> AIProvider:
        """Create an AI provider based on configuration"""
        
        # Default to Google Gemini if no provider specified
        if provider is None:
            provider = "google"
        if model is None:
            model = "gemini-2.5-pro"
        
        # Get API keys
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Create provider
        provider_lower = provider.lower()
        
        if provider_lower == "anthropic":
            if not anthropic_key:
                raise AIProviderConfigError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider")
            return AnthropicProvider(anthropic_key, model)
        
        elif provider_lower == "openai":
            if not openai_key:
                raise AIProviderConfigError("OPENAI_API_KEY environment variable is required for OpenAI provider")
            return OpenAIProvider(openai_key, model)
        
        elif provider_lower == "google":
            if not gemini_key:
                raise AIProviderConfigError("GEMINI_API_KEY environment variable is required for Google provider")
            return GeminiProvider(gemini_key, model)
        
        else:
            raise AIProviderConfigError(f"Unsupported AI provider: {provider}. Supported: anthropic, openai, google")