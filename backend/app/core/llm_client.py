"""
LLM Client for communicating with Groq API.

This client makes HTTP requests to Groq's ultra-fast LLM API.
Groq provides blazing-fast inference for Llama 3.1 models.
"""
import logging
from typing import Optional, List, Dict
from groq import AsyncGroq
from app.config import settings


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GroqClient:
    """
    Client for Groq's ultra-fast LLM API.
    
    Simple explanation:
    - Your app on Render.com calls this client
    - This client sends request to Groq's servers
    - Groq runs Llama 3.1 70B (very powerful!)
    - Returns answer in 0.5-1 second (super fast!)
    - This client returns answer to your app
    
    Why Groq is awesome:
    - Fastest LLM inference in the world
    - Free tier with generous limits
    - No server management needed
    - Works perfectly with Render.com free tier
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Groq client.
        
        Args:
            api_key: Your Groq API key (from console.groq.com)
                    If None, uses settings.groq_api_key
        """
        self.api_key = api_key or settings.groq_api_key
        self.client = AsyncGroq(api_key=self.api_key)
        self.model = settings.llm_model  # Use model from settings
        logger.info(f"Initialized GroqClient with model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using Llama 3.1 70B.
        
        Args:
            prompt: The question or instruction for the AI
            temperature: Creativity (0.0 = focused, 1.0 = creative)
            max_tokens: Maximum length of response
        
        Returns:
            str: The AI's response
        
        Example:
            >>> client = GroqClient()
            >>> response = await client.generate("What is 2+2?")
            >>> print(response)
            "2+2 equals 4"
        
        Speed:
            Groq is FAST! Typical response time: 0.5-1 second
            Compare to other APIs: 2-5 seconds
        """
        try:
            logger.info(f"Sending prompt to Groq: {prompt[:100]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.info(f"Received response from Groq ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise Exception(f"Failed to call Groq API: {e}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Chat with the AI using conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [
                         {"role": "user", "content": "Hello"},
                         {"role": "assistant", "content": "Hi!"},
                         {"role": "user", "content": "How are you?"}
                     ]
            temperature: Creativity level
            max_tokens: Maximum response length
        
        Returns:
            str: The AI's response
        
        Example:
            >>> client = GroqClient()
            >>> messages = [
            ...     {"role": "user", "content": "What's a good car?"},
            ...     {"role": "assistant", "content": "Toyota Camry is reliable"},
            ...     {"role": "user", "content": "What year?"}
            ... ]
            >>> response = await client.chat(messages)
            >>> print(response)
            "I'd recommend 2015-2020 models for best value"
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise Exception(f"Chat error: {e}")
    
    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.3
    ) -> Dict:
        """
        Generate structured JSON response.
        
        Useful for getting structured data from AI.
        
        Args:
            prompt: Instruction that asks for JSON response
            temperature: Lower = more consistent JSON
        
        Returns:
            dict: Parsed JSON response
        
        Example:
            >>> client = GroqClient()
            >>> prompt = '''
            ... Analyze this search and return JSON:
            ... {"should_expand": true, "reason": "too few results"}
            ... '''
            >>> result = await client.generate_json(prompt)
            >>> print(result)
            {"should_expand": True, "reason": "too few results"}
        """
        try:
            # Add instruction to return JSON
            json_prompt = f"{prompt}\n\nRespond with valid JSON only, no other text."
            
            response = await self.generate(
                json_prompt,
                temperature=temperature,
                max_tokens=500
            )
            
            # Parse JSON
            import json
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response was: {response}")
            raise Exception("AI did not return valid JSON")
        except Exception as e:
            logger.error(f"JSON generation error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if Groq API is accessible.
        
        Returns:
            bool: True if API is working, False otherwise
        """
        try:
            response = await self.generate(
                "Say 'OK'",
                max_tokens=10
            )
            return "ok" in response.lower()
        except:
            return False


# Singleton instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """
    Get the global Groq client instance.
    
    This ensures we only create one client for the entire app.
    Saves memory and API connections.
    
    Returns:
        GroqClient: The global client instance
    """
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client


# Backward compatibility aliases
OllamaClient = GroqClient
get_ollama_client = get_groq_client
_ollama_client = _groq_client