#!/usr/bin/env python3
"""
Simple LLM Provider - Works with OpenAI, Gemini, Claude, Fireworks, Mistral, and Ollama
"""

import os
import requests
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMResponse:
    """Simple response format."""
    content: str
    model: str
    provider: str

class SimpleLLM:
    """Simple LLM that works with multiple providers."""
    
    def __init__(self, provider=None, model=None):
        self.provider = provider or self._detect_provider()
        self.model = model or self._get_default_model()
        self.client = self._create_client()
    
    def _detect_provider(self):
        """Auto-detect provider from API keys."""
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("FIREWORKS_API_KEY"):
            return "fireworks"
        elif os.getenv("MISTRAL_API_KEY"):
            return "mistral"
        elif self._check_ollama():
            return "ollama"
        else:
            raise ValueError("No API key found! Set OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, FIREWORKS_API_KEY, MISTRAL_API_KEY, or run Ollama locally")
    
    def _get_default_model(self):
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-3.5-turbo",
            "gemini": "gemini-1.5-flash", 
            "anthropic": "claude-3-sonnet-20240229",
            "fireworks": "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "mistral": "mistral-small-latest",
            "ollama": "llama3.2"
        }
        return defaults.get(self.provider, "gpt-3.5-turbo")
    
    def _check_ollama(self):
        """Check if Ollama is running locally."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _create_client(self):
        """Create the appropriate client."""
        if self.provider == "openai":
            import openai
            return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            return genai.GenerativeModel(self.model)
        elif self.provider == "anthropic":
            import anthropic
            return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif self.provider == "fireworks":
            import fireworks
            return fireworks.Fireworks(api_key=os.getenv("FIREWORKS_API_KEY"))
        elif self.provider == "mistral":
            import openai
            return openai.OpenAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )
        elif self.provider == "ollama":
            return None  # Ollama uses direct HTTP requests
    
    def generate(self, prompt, temperature=0):
        """Generate a response."""
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                content = response.choices[0].message.content
                
            elif self.provider == "gemini":
                response = self.client.generate_content(prompt)
                content = response.text
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                
            elif self.provider == "fireworks":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                content = response.choices[0].message.content
                
            elif self.provider == "mistral":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                content = response.choices[0].message.content
                
            elif self.provider == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                content = response.json()["response"]
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider
            )
            
        except Exception as e:
            raise Exception(f"Error with {self.provider}: {e}")

# Simple function to get LLM
def get_llm(provider=None, model=None):
    """Get a simple LLM instance."""
    return SimpleLLM(provider, model)

# Test
if __name__ == "__main__":
    try:
        llm = get_llm()
        print(f"Using: {llm.provider}")
        response = llm.generate("Hello!")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
        print("Set up your API keys in .env file")