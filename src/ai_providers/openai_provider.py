from typing import Dict, Any
from .base import AIProvider, AIProviderAPIError

try:
    import openai
except ImportError:
    openai = None


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
            raise AIProviderAPIError(f"OpenAI API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "has_reasoning": self.model == "o4-mini",
            "is_free": self.model in ["gpt-4.1-nano", "gpt-4.1-mini"],
            "is_cheaper": self.model in ["gpt-4.1-nano", "gpt-4.1-mini"]
        }