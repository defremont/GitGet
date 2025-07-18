from typing import Dict, Any
from .base import AIProvider, AIProviderAPIError

try:
    import google.generativeai as genai
except ImportError:
    genai = None


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
            raise AIProviderAPIError(f"Gemini API error: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "google",
            "model": self.model,
            "has_reasoning": False,
            "is_free": True,
            "is_cheaper": self.model == "gemini-2.5-flash"
        }