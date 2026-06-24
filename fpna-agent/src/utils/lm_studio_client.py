# src/utils/lm_studio_client.py
import requests
import json
import time
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LMStudioClient:
    """Client for LM Studio's OpenAI-compatible API with better timeout handling"""
    
    def __init__(self, base_url: str = "http://192.168.153.1:1234", 
                 model: str = "deepseek-r1-distill-qwen-7b",
                 timeout: int = 60,  # Reduced from 120
                 max_retries: int = 2):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.chat_endpoint = f"{self.base_url}/v1/chat/completions"
        
    def chat_completion(self, messages: List[Dict], 
                       temperature: float = 0.1, 
                       max_tokens: int = 800) -> str:  # Reduced from 512
        """Send chat completion request to LM Studio with retries"""
        
        # Add stop sequences to prevent thinking tags
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "stop": ["<think>", "</think>", "\n\n\n", "###", "---"]  # Added stop sequences
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LM Studio request attempt {attempt + 1}/{self.max_retries}")
                logger.debug(f"Payload tokens: ~{max_tokens}, Messages: {len(messages)}")
                
                response = requests.post(
                    self.chat_endpoint,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Quick cleanup of response
                    if "<think>" in content:
                        # Try to extract text after </think>
                        parts = content.split("</think>")
                        if len(parts) > 1:
                            content = parts[-1].strip()
                        else:
                            content = content.replace("<think>", "").strip()
                    
                    logger.debug(f"Response received: {content[:100]}...")
                    return content
                else:
                    raise ValueError("Invalid response format from LM Studio")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("LM Studio request timed out after multiple attempts")
                    return "Error: Request timeout. Please try again."
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"LM Studio request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(f"LM Studio connection error: {e}")
                    return f"Error: Connection failed - {str(e)}"
        
        logger.error("Failed to get response from LM Studio after all retries")
        return "Error: Failed to get response from LM Studio."
    
    def test_connection(self, quick_test: bool = True) -> bool:
        """Test if LM Studio is reachable - with quick test option"""
        try:
            if quick_test:
                # Quick test - just check if server is up
                response = requests.get(f"{self.base_url}/v1/models", timeout=10)
                return response.status_code == 200
            else:
                # Full test - try a tiny prompt
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Respond only with the word 'OK'"}
                ]
                response = self.chat_completion(messages, max_tokens=10)
                return "OK" in response.upper()
                
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models in LM Studio"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                return [model["id"] for model in models.get("data", [])]
        except Exception as e:
            logger.warning(f"Failed to get models: {e}")
            return []
    
    def quick_chat(self, prompt: str, system_prompt: str = None, max_tokens: int = 200) -> str:
        """Quick chat method with minimal settings for testing"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens
        )