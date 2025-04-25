"""
Grok 3 Provider for API integration.

This module provides the core provider class for interacting with the Grok 3 API.
"""

import os
import time
import logging
import json
import requests
from typing import Dict, List, Any, Optional, Union, Tuple

from .auth_utils import get_grok3_api_key, get_grok3_api_base

# Set up logging
logger = logging.getLogger(__name__)

class Grok3Provider:
    """
    Provider class for interacting with the Grok 3 API.
    
    This class provides methods for making requests to the Grok 3 API,
    handling authentication, and managing API responses.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 60,
        secure_mode: bool = True
    ):
        """
        Initialize the Grok3Provider.
        
        Args:
            api_key: Optional API key for authentication. If not provided,
                    will attempt to get from environment or global variable.
            api_base: Optional API base URL. If not provided, will use default.
            max_retries: Maximum number of retries for failed requests.
            timeout: Timeout in seconds for API requests.
            secure_mode: Whether to enable secure mode for API requests.
        """
        self.api_key = api_key or get_grok3_api_key()
        self.api_base = api_base or get_grok3_api_base()
        self.max_retries = max_retries
        self.timeout = timeout
        self.secure_mode = secure_mode
        
        if not self.api_key:
            logger.warning("No API key provided. API calls will likely fail.")
        
        logger.info(f"Initialized Grok3Provider with API base: {self.api_base}")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dictionary of headers for API requests.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Grok 3 API.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint to call.
            data: Optional data to send in the request body.
            params: Optional query parameters.
        
        Returns:
            API response as a dictionary.
        
        Raises:
            Exception: If the API request fails after max_retries.
        """
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    backoff_time = 2 ** attempt + (0.1 * attempt)
                    logger.info(f"Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                else:
                    logger.error(f"API request failed after {self.max_retries} attempts")
                    raise Exception(f"Failed to call Grok 3 API: {str(e)}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from the Grok 3 API.
        
        Returns:
            List of available models.
        """
        response = self._make_request("GET", "/models")
        return response.get("data", [])
    
    def generate_completion(
        self,
        model: str = "grok-3",
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        system_message: Optional[str] = None,
        reasoning_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion from the Grok 3 API.
        
        Args:
            model: Model to use for completion.
            prompt: Text prompt for completion (for text completion).
            messages: List of messages for chat completion.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            stop: Stop sequences to end generation.
            stream: Whether to stream the response.
            system_message: System message for chat completion.
            reasoning_mode: Reasoning mode to use (auto, think, big_brain).
        
        Returns:
            API response as a dictionary.
        
        Raises:
            ValueError: If neither prompt nor messages are provided.
        """
        if not (prompt or messages):
            raise ValueError("Either prompt or messages must be provided")
        
        # Prepare request data
        data = {
            "model": model,
            "temperature": temperature,
            "stream": stream
        }
        
        # Add optional parameters if provided
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        
        if top_p is not None:
            data["top_p"] = top_p
        
        if stop is not None:
            data["stop"] = stop
        
        # Handle reasoning mode
        if reasoning_mode:
            if reasoning_mode not in ["auto", "think", "big_brain"]:
                logger.warning(f"Unknown reasoning mode: {reasoning_mode}. Using default.")
            else:
                data["reasoning_mode"] = reasoning_mode
        
        # Handle text completion vs. chat completion
        if prompt:
            data["prompt"] = prompt
            
            if system_message:
                # For text completion with system message, use messages format
                data["messages"] = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
                # Remove prompt to use messages format
                del data["prompt"]
            
            endpoint = "/completions"
        else:
            # Chat completion
            data["messages"] = messages
            
            # Add system message if provided and not already in messages
            if system_message and not any(m.get("role") == "system" for m in messages):
                data["messages"] = [{"role": "system", "content": system_message}] + data["messages"]
            
            endpoint = "/chat/completions"
        
        # Make the API request
        return self._make_request("POST", endpoint, data=data)
    
    def generate_embeddings(
        self,
        input: Union[str, List[str]],
        model: str = "grok-3-embedding"
    ) -> Dict[str, Any]:
        """
        Generate embeddings from the Grok 3 API.
        
        Args:
            input: Text or list of texts to generate embeddings for.
            model: Model to use for embeddings.
        
        Returns:
            API response with embeddings.
        """
        data = {
            "model": model,
            "input": input if isinstance(input, list) else [input]
        }
        
        return self._make_request("POST", "/embeddings", data=data)
