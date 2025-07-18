from typing import Dict, Any
from .base import AIProvider, AIProviderAPIError

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest"):
        if anthropic is None:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        
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
            raise AIProviderAPIError(f"Anthropic API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "anthropic",
            "model": self.model,
            "has_reasoning": self.model == "claude-sonnet-4-0",
            "is_free": False,
            "is_cheaper": self.model == "claude-3-5-haiku-latest"
        }