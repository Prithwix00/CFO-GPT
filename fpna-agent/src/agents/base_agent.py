# src/agents/base_agent.py
from typing import Any, Dict, List, Optional
from src.utils.lm_studio_client import LMStudioClient
from config.settings import settings
import logging
import re

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class with LM Studio integration using direct API calls"""
    
    def __init__(self, agent_name: str, system_prompt: str = ""):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.lm_client = self._initialize_lm_client()
        
    def _initialize_lm_client(self):
        """Initialize LM Studio client with settings from config"""
        try:
            client = LMStudioClient(
                base_url=settings.LMSTUDIO_BASE_URL,
                model=settings.MODEL_ID,
                timeout=getattr(settings, 'REQUEST_TIMEOUT', 60),  # Reduced from 120
                max_retries=getattr(settings, 'MAX_RETRIES', 2)
            )
            
            # Quick connection test
            if client.test_connection(quick_test=True):
                logger.info(f"✅ Initialized LM Studio client for {self.agent_name}")
                logger.info(f"   Model: {settings.MODEL_ID}")
                logger.info(f"   Base URL: {settings.LMSTUDIO_BASE_URL}")
                
                # List available models
                models = client.get_available_models()
                if models:
                    logger.info(f"   Available models: {', '.join(models)}")
                
                return client
            else:
                raise ConnectionError(f"Cannot connect to LM Studio at {settings.LMSTUDIO_BASE_URL}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio client: {e}")
            raise
    
    def _clean_response(self, response: str) -> str:
        """Clean LLM response by removing thinking tags and incomplete sentences"""
        if not response:
            return response
            
        # Remove <think>...</think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Remove standalone <think> tags
        response = response.replace('<think>', '').replace('</think>', '')
        
        # Remove multiple newlines and trim
        response = re.sub(r'\n\s*\n', '\n\n', response).strip()
        
        # If response still contains incomplete sentences at the end
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('<') and not line.endswith('<'):
                # Check if line looks like an incomplete thought
                if len(line) > 10 and not (line.endswith('...') and len(line.split()) < 5):
                    cleaned_lines.append(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Ensure the response ends with proper punctuation
        if response and response[-1] not in ['.', '!', '?', ')', ']', '}']:
            # Find last complete sentence
            sentences = re.split(r'(?<=[.!?])\s+', response)
            if sentences and len(sentences) > 1:
                response = ' '.join(sentences[:-1])
            elif sentences:
                response = sentences[0]
                
        return response.strip()
    
    def invoke(self, prompt: str, context: Optional[Dict] = None, max_tokens: int = None) -> str:
        """Invoke the agent with a prompt"""
        try:
            messages = []
            
            # Enhanced system prompt to avoid thinking tags
            enhanced_system_prompt = self.system_prompt
            if self.system_prompt:
                enhanced_system_prompt += "\n\nIMPORTANT: Provide your final answer without any <think> tags or thinking process. Give only the final, complete response."
            
            # Add system prompt if provided
            if enhanced_system_prompt:
                messages.append({
                    "role": "system",
                    "content": enhanced_system_prompt[:1000]  # Increased limit
                })
            
            # Add context if provided
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"Context:\n{context_str}\n\nQuestion: {prompt}"
            
            # Limit prompt length for performance but keep important info
            if len(prompt) > 2500:
                # Keep first 2000 chars and last 500 chars
                prompt = prompt[:2000] + "...\n[truncated]\n..." + prompt[-500:]
            
            # Add user prompt with instruction
            enhanced_prompt = prompt + "\n\nIMPORTANT: Provide a complete, final answer. No thinking process, no <think> tags."
            
            messages.append({
                "role": "user",
                "content": enhanced_prompt
            })
            
            # Get response from LM Studio
            response = self.lm_client.chat_completion(
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=min(max_tokens or settings.MAX_TOKENS, 800)  # Limit tokens
            )
            
            # Clean the response
            cleaned_response = self._clean_response(response)
            
            # Log response summary
            if cleaned_response:
                logger.debug(f"Agent {self.agent_name} response (first 100 chars): {cleaned_response[:100]}...")
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Error invoking agent {self.agent_name}: {e}")
            return f"Error: {str(e)}"
    
    def quick_invoke(self, prompt: str) -> str:
        """Quick invocation with minimal tokens for testing"""
        return self.invoke(prompt, max_tokens=200)
    
    def test_agent(self) -> bool:
        """Test if agent can communicate with LM Studio"""
        try:
            response = self.quick_invoke("Respond only with the word 'OK'")
            return "OK" in response.upper()
        except:
            return False