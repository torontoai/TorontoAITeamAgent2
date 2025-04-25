"""
Model adapter module for Grok 3 API integration.

This module contains adapter classes for using Grok 3 models in a unified way.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging

from app.models.providers.grok3_provider import Grok3Provider
from app.models.providers.auth_utils import get_grok3_api_key, get_grok3_api_base

# Set up logging
logger = logging.getLogger(__name__)

class Grok3Adapter:
    """
    Adapter class for using Grok 3 models with a unified interface.
    
    This class provides a simplified interface for interacting with Grok 3 models,
    abstracting away the details of the API calls.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        default_model: str = "grok-3",
        max_retries: int = 3,
        timeout: int = 60,
        secure_mode: bool = True
    ):
        """
        Initialize the Grok3Adapter.
        
        Args:
            api_key: Optional API key for authentication.
            api_base: Optional API base URL.
            default_model: Default model to use for generation.
            max_retries: Maximum number of retries for failed requests.
            timeout: Timeout in seconds for API requests.
            secure_mode: Whether to enable secure mode for API requests.
        """
        self.provider = Grok3Provider(
            api_key=api_key,
            api_base=api_base,
            max_retries=max_retries,
            timeout=timeout,
            secure_mode=secure_mode
        )
        self.default_model = default_model
        
        logger.info(f"Initialized Grok3Adapter with default model: {default_model}")
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        reasoning_mode: Optional[str] = None
    ) -> str:
        """
        Generate text using a Grok 3 model.
        
        Args:
            prompt: Text prompt for generation.
            model: Model to use (defaults to self.default_model).
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            system_message: Optional system message for context.
            reasoning_mode: Optional reasoning mode (auto, think, big_brain).
        
        Returns:
            Generated text as a string.
        """
        model = model or self.default_model
        
        response = self.provider.generate_completion(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_message=system_message,
            reasoning_mode=reasoning_mode
        )
        
        # Extract the generated text from the response
        if "choices" in response and len(response["choices"]) > 0:
            if "text" in response["choices"][0]:
                # Text completion format
                return response["choices"][0]["text"]
            elif "message" in response["choices"][0]:
                # Chat completion format
                return response["choices"][0]["message"]["content"]
        
        logger.warning("Unexpected response format from Grok 3 API")
        return ""
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        reasoning_mode: Optional[str] = None
    ) -> str:
        """
        Generate a response in a chat conversation.
        
        Args:
            messages: List of messages in the conversation.
            model: Model to use (defaults to self.default_model).
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            reasoning_mode: Optional reasoning mode (auto, think, big_brain).
        
        Returns:
            Generated response as a string.
        """
        model = model or self.default_model
        
        response = self.provider.generate_completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            reasoning_mode=reasoning_mode
        )
        
        # Extract the generated text from the response
        if "choices" in response and len(response["choices"]) > 0:
            if "message" in response["choices"][0]:
                return response["choices"][0]["message"]["content"]
        
        logger.warning("Unexpected response format from Grok 3 API")
        return ""
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: str = "grok-3-embedding"
    ) -> List[List[float]]:
        """
        Get embeddings for text(s).
        
        Args:
            texts: Text or list of texts to get embeddings for.
            model: Model to use for embeddings.
        
        Returns:
            List of embeddings (each embedding is a list of floats).
        """
        response = self.provider.generate_embeddings(
            input=texts,
            model=model
        )
        
        # Extract embeddings from the response
        if "data" in response and len(response["data"]) > 0:
            return [item["embedding"] for item in response["data"]]
        
        logger.warning("Unexpected response format from Grok 3 API")
        return []
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List available Grok 3 models.
        
        Returns:
            List of available models with their details.
        """
        return self.provider.list_models()
