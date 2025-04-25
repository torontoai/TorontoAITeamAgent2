"""
Anthropic Claude 3 Opus Provider for TORONTO AI TEAM AGENT

This module provides integration with Anthropic's Claude 3 Opus model, offering
advanced reasoning capabilities, a large context window, and high-quality outputs.

Features:
- Advanced reasoning modes for complex tasks
- 200K token context window for processing large documents
- High-quality text generation with nuanced understanding
- Secure API key management
- Robust error handling with retries
"""

import os
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Import auth utilities
from .auth_utils import get_api_key, APIKeyNotFoundError

# Set up logging
logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Available Claude model versions."""
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


class ClaudeReasoningMode(Enum):
    """Reasoning modes for Claude models."""
    STANDARD = "standard"
    THINK = "think"  # More deliberate reasoning
    CREATIVE = "creative"  # More creative outputs
    PRECISE = "precise"  # More precise, factual outputs


@dataclass
class ClaudeMessage:
    """Represents a message in a Claude conversation."""
    role: str  # 'user' or 'assistant'
    content: str


class ClaudeError(Exception):
    """Base exception for Claude API errors."""
    pass


class ClaudeAPIError(ClaudeError):
    """Exception raised for Claude API errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Claude API Error ({status_code}): {message}")


class ClaudeRateLimitError(ClaudeAPIError):
    """Exception raised for rate limit errors."""
    def __init__(self, status_code: int, message: str, retry_after: Optional[int] = None):
        super().__init__(status_code, message)
        self.retry_after = retry_after


class ClaudeProvider:
    """
    Provider for Anthropic's Claude 3 models.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: ClaudeModel = ClaudeModel.CLAUDE_3_OPUS,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 base_url: str = "https://api.anthropic.com/v1"):
        """
        Initialize the Claude provider.
        
        Args:
            api_key: Anthropic API key (if None, will try to load from environment)
            model: Claude model to use
            max_retries: Maximum number of retries for API calls
            retry_delay: Initial delay between retries (in seconds)
            base_url: Base URL for the Anthropic API
        """
        self.api_key = api_key or get_api_key("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise APIKeyNotFoundError("Anthropic API key not found")
        
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = base_url
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    def _handle_error(self, response: requests.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()
        except ValueError:
            error_message = response.text or "Unknown error"
        else:
            error_message = error_data.get("error", {}).get("message", "Unknown error")
        
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise ClaudeRateLimitError(response.status_code, error_message, retry_seconds)
        else:
            raise ClaudeAPIError(response.status_code, error_message)
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Claude API with retry logic.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._prepare_headers()
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle rate limiting with specific retry logic
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        sleep_time = int(retry_after)
                    else:
                        sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    
                    logger.warning(f"Rate limited. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                
                # Handle other errors
                self._handle_error(response)
            
            except (requests.RequestException, ClaudeRateLimitError) as e:
                if attempt == self.max_retries - 1:
                    raise
                
                if isinstance(e, ClaudeRateLimitError) and e.retry_after:
                    sleep_time = e.retry_after
                else:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                
                logger.warning(f"Request failed: {str(e)}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        # This should not be reached due to the raise in the loop
        raise ClaudeError("Maximum retries exceeded")
    
    def generate_text(self, 
                     prompt: str, 
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     reasoning_mode: Optional[ClaudeReasoningMode] = None,
                     system_prompt: Optional[str] = None) -> str:
        """
        Generate text using Claude.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        messages = [ClaudeMessage(role="user", content=prompt)]
        return self.chat_completion(messages, max_tokens, temperature, reasoning_mode, system_prompt)
    
    def chat_completion(self,
                       messages: List[ClaudeMessage],
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       reasoning_mode: Optional[ClaudeReasoningMode] = None,
                       system_prompt: Optional[str] = None) -> str:
        """
        Generate a chat completion using Claude.
        
        Args:
            messages: List of messages in the conversation
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            system_prompt: Optional system prompt
            
        Returns:
            Generated assistant response
        """
        # Prepare the request data
        data = {
            "model": self.model.value,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
        
        # Add system prompt if provided
        if system_prompt:
            data["system"] = system_prompt
        
        # Add reasoning mode if provided
        if reasoning_mode:
            # Claude doesn't have a direct reasoning mode parameter, so we'll add it to the system prompt
            reasoning_prompt = self._get_reasoning_prompt(reasoning_mode)
            if system_prompt:
                data["system"] = f"{system_prompt}\n\n{reasoning_prompt}"
            else:
                data["system"] = reasoning_prompt
        
        # Make the API request
        response = self._make_request("messages", data)
        
        # Extract and return the assistant's message
        return response.get("content", [{"text": ""}])[0]["text"]
    
    def _get_reasoning_prompt(self, reasoning_mode: ClaudeReasoningMode) -> str:
        """Get the system prompt for a specific reasoning mode."""
        if reasoning_mode == ClaudeReasoningMode.THINK:
            return (
                "Please think step-by-step through this problem. "
                "Break down your reasoning process explicitly, considering multiple perspectives "
                "and evaluating different approaches before providing your final answer."
            )
        elif reasoning_mode == ClaudeReasoningMode.CREATIVE:
            return (
                "Please approach this task with creativity and originality. "
                "Feel free to explore unconventional ideas and novel perspectives. "
                "Don't be constrained by conventional thinking."
            )
        elif reasoning_mode == ClaudeReasoningMode.PRECISE:
            return (
                "Please be extremely precise and factual in your response. "
                "Prioritize accuracy and clarity. Avoid speculation and clearly indicate "
                "any uncertainties. Cite specific information where relevant."
            )
        else:  # Standard mode
            return ""
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Input text
            
        Returns:
            Approximate token count
        """
        # This is a simple approximation - Claude doesn't provide a token counting endpoint
        # A more accurate implementation would use a tokenizer like tiktoken
        words = text.split()
        return int(len(words) * 1.3)  # Rough approximation
    
    def set_model(self, model: ClaudeModel) -> None:
        """
        Set the Claude model to use.
        
        Args:
            model: Claude model
        """
        self.model = model
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        model_info = {
            "name": self.model.value,
            "provider": "Anthropic",
            "capabilities": {
                "max_context": 200000 if self.model == ClaudeModel.CLAUDE_3_OPUS else 100000,
                "reasoning_modes": [mode.value for mode in ClaudeReasoningMode],
                "streaming": True,
                "vision": True if self.model != ClaudeModel.CLAUDE_3_HAIKU else False
            }
        }
        
        return model_info
