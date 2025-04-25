"""
Google Gemini Pro/Ultra Provider for TORONTO AI TEAM AGENT

This module provides integration with Google's Gemini Pro and Ultra models,
offering advanced reasoning capabilities and multimodal understanding.

Features:
- Support for both Gemini Pro and Ultra models
- Multimodal capabilities for processing text and images
- Advanced reasoning modes
- Robust error handling with retries
- Secure API key management
"""

import os
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import base64

# Import auth utilities
from .auth_utils import get_api_key, APIKeyNotFoundError

# Set up logging
logger = logging.getLogger(__name__)


class GeminiModel(Enum):
    """Available Gemini model versions."""
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_ULTRA = "gemini-ultra"
    GEMINI_ULTRA_VISION = "gemini-ultra-vision"


class GeminiReasoningMode(Enum):
    """Reasoning modes for Gemini models."""
    STANDARD = "standard"
    ANALYTICAL = "analytical"  # More analytical reasoning
    CREATIVE = "creative"  # More creative outputs
    BALANCED = "balanced"  # Balanced approach


@dataclass
class GeminiMessage:
    """Represents a message in a Gemini conversation."""
    role: str  # 'user' or 'model'
    content: Union[str, List[Dict[str, Any]]]  # Text or multimodal content


@dataclass
class GeminiImage:
    """Represents an image for multimodal inputs."""
    data: Optional[bytes] = None
    url: Optional[str] = None
    mime_type: str = "image/jpeg"


class GeminiError(Exception):
    """Base exception for Gemini API errors."""
    pass


class GeminiAPIError(GeminiError):
    """Exception raised for Gemini API errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Gemini API Error ({status_code}): {message}")


class GeminiRateLimitError(GeminiAPIError):
    """Exception raised for rate limit errors."""
    def __init__(self, status_code: int, message: str, retry_after: Optional[int] = None):
        super().__init__(status_code, message)
        self.retry_after = retry_after


class GeminiProvider:
    """
    Provider for Google's Gemini models.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: GeminiModel = GeminiModel.GEMINI_PRO,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Google API key (if None, will try to load from environment)
            model: Gemini model to use
            max_retries: Maximum number of retries for API calls
            retry_delay: Initial delay between retries (in seconds)
            base_url: Base URL for the Gemini API
        """
        self.api_key = api_key or get_api_key("GOOGLE_API_KEY")
        if not self.api_key:
            raise APIKeyNotFoundError("Google API key not found")
        
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = base_url
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests."""
        return {
            "Content-Type": "application/json"
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
            raise GeminiRateLimitError(response.status_code, error_message, retry_seconds)
        else:
            raise GeminiAPIError(response.status_code, error_message)
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Gemini API with retry logic.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response as a dictionary
        """
        # Add API key to URL
        url = f"{self.base_url}/{endpoint}?key={self.api_key}"
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
            
            except (requests.RequestException, GeminiRateLimitError) as e:
                if attempt == self.max_retries - 1:
                    raise
                
                if isinstance(e, GeminiRateLimitError) and e.retry_after:
                    sleep_time = e.retry_after
                else:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                
                logger.warning(f"Request failed: {str(e)}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        # This should not be reached due to the raise in the loop
        raise GeminiError("Maximum retries exceeded")
    
    def generate_text(self, 
                     prompt: str, 
                     max_tokens: int = 1000,
                     temperature: float = 0.7,
                     reasoning_mode: Optional[GeminiReasoningMode] = None) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            
        Returns:
            Generated text
        """
        # Check if model supports text-only generation
        if self.model in [GeminiModel.GEMINI_PRO_VISION, GeminiModel.GEMINI_ULTRA_VISION]:
            logger.warning(f"Using vision model {self.model.value} for text-only generation")
        
        # Prepare the request data
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Add reasoning mode if provided
        if reasoning_mode:
            system_instruction = self._get_reasoning_prompt(reasoning_mode)
            if system_instruction:
                data["systemInstruction"] = {
                    "parts": [
                        {
                            "text": system_instruction
                        }
                    ]
                }
        
        # Make the API request
        endpoint = f"models/{self.model.value}:generateContent"
        response = self._make_request(endpoint, data)
        
        # Extract and return the generated text
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            logger.error(f"Unexpected response format: {response}")
            return ""
    
    def generate_multimodal(self, 
                           prompt: str, 
                           images: List[GeminiImage],
                           max_tokens: int = 1000,
                           temperature: float = 0.7,
                           reasoning_mode: Optional[GeminiReasoningMode] = None) -> str:
        """
        Generate text based on text and images using Gemini.
        
        Args:
            prompt: User prompt
            images: List of images
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            
        Returns:
            Generated text
        """
        # Check if model supports multimodal generation
        if self.model not in [GeminiModel.GEMINI_PRO_VISION, GeminiModel.GEMINI_ULTRA_VISION]:
            logger.warning(f"Model {self.model.value} does not support multimodal generation, switching to vision model")
            if self.model == GeminiModel.GEMINI_PRO:
                self.model = GeminiModel.GEMINI_PRO_VISION
            elif self.model == GeminiModel.GEMINI_ULTRA:
                self.model = GeminiModel.GEMINI_ULTRA_VISION
        
        # Prepare parts with text and images
        parts = [{"text": prompt}]
        
        for image in images:
            if image.data:
                # Convert image data to base64
                mime_type = image.mime_type
                b64_data = base64.b64encode(image.data).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": b64_data
                    }
                })
            elif image.url:
                parts.append({
                    "fileData": {
                        "mimeType": image.mime_type,
                        "fileUri": image.url
                    }
                })
        
        # Prepare the request data
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Add reasoning mode if provided
        if reasoning_mode:
            system_instruction = self._get_reasoning_prompt(reasoning_mode)
            if system_instruction:
                data["systemInstruction"] = {
                    "parts": [
                        {
                            "text": system_instruction
                        }
                    ]
                }
        
        # Make the API request
        endpoint = f"models/{self.model.value}:generateContent"
        response = self._make_request(endpoint, data)
        
        # Extract and return the generated text
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            logger.error(f"Unexpected response format: {response}")
            return ""
    
    def chat_completion(self,
                       messages: List[GeminiMessage],
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       reasoning_mode: Optional[GeminiReasoningMode] = None) -> str:
        """
        Generate a chat completion using Gemini.
        
        Args:
            messages: List of messages in the conversation
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            reasoning_mode: Optional reasoning mode to use
            
        Returns:
            Generated model response
        """
        # Convert messages to Gemini format
        contents = []
        
        for message in messages:
            if isinstance(message.content, str):
                contents.append({
                    "role": message.role,
                    "parts": [{"text": message.content}]
                })
            else:
                contents.append({
                    "role": message.role,
                    "parts": message.content
                })
        
        # Prepare the request data
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        # Add reasoning mode if provided
        if reasoning_mode:
            system_instruction = self._get_reasoning_prompt(reasoning_mode)
            if system_instruction:
                data["systemInstruction"] = {
                    "parts": [
                        {
                            "text": system_instruction
                        }
                    ]
                }
        
        # Make the API request
        endpoint = f"models/{self.model.value}:generateContent"
        response = self._make_request(endpoint, data)
        
        # Extract and return the generated text
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            logger.error(f"Unexpected response format: {response}")
            return ""
    
    def _get_reasoning_prompt(self, reasoning_mode: GeminiReasoningMode) -> str:
        """Get the system prompt for a specific reasoning mode."""
        if reasoning_mode == GeminiReasoningMode.ANALYTICAL:
            return (
                "Please approach this task with analytical reasoning. "
                "Break down complex problems into components, analyze data methodically, "
                "and provide logical, evidence-based conclusions. Focus on accuracy and precision."
            )
        elif reasoning_mode == GeminiReasoningMode.CREATIVE:
            return (
                "Please approach this task with creative thinking. "
                "Explore novel connections, generate innovative ideas, and consider "
                "unconventional perspectives. Feel free to think outside traditional boundaries."
            )
        elif reasoning_mode == GeminiReasoningMode.BALANCED:
            return (
                "Please approach this task with a balanced perspective. "
                "Combine analytical reasoning with creative thinking to provide "
                "comprehensive, well-rounded responses that consider multiple viewpoints."
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
        # This is a simple approximation - Gemini doesn't provide a token counting endpoint
        words = text.split()
        return int(len(words) * 1.3)  # Rough approximation
    
    def set_model(self, model: GeminiModel) -> None:
        """
        Set the Gemini model to use.
        
        Args:
            model: Gemini model
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
            "provider": "Google",
            "capabilities": {
                "max_context": 32000 if "ultra" in self.model.value else 16000,
                "reasoning_modes": [mode.value for mode in GeminiReasoningMode],
                "multimodal": "vision" in self.model.value,
                "streaming": True
            }
        }
        
        return model_info
