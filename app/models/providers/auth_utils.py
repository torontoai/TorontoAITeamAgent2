"""
Authentication utilities for Grok 3 API integration.

This module provides utilities for managing authentication with the Grok 3 API.
"""

import os
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

# Environment variable name for the API key
GROK3_API_KEY_ENV = "GROK3_API_KEY"
GROK3_API_BASE_ENV = "GROK3_API_BASE"

# Default API base URL
DEFAULT_API_BASE = "https://api.grok.x.ai/v1"

# Global variables to store API credentials
_api_key = None
_api_base = None


def set_grok3_api_key(api_key: str) -> None:
    """
    Set the Grok 3 API key for authentication.
    
    Args:
        api_key: The API key to use for authentication.
    """
    global _api_key
    _api_key = api_key
    logger.info("Grok 3 API key has been set")


def get_grok3_api_key() -> Optional[str]:
    """
    Get the Grok 3 API key.
    
    Returns:
        The API key if set, otherwise None.
    """
    global _api_key
    
    # If API key is already set, return it
    if _api_key:
        return _api_key
    
    # Try to get API key from environment variable
    api_key = os.environ.get(GROK3_API_KEY_ENV)
    if api_key:
        _api_key = api_key
        logger.info("Grok 3 API key loaded from environment variable")
        return _api_key
    
    logger.warning("Grok 3 API key not found")
    return None


def set_grok3_api_base(api_base: str) -> None:
    """
    Set the Grok 3 API base URL.
    
    Args:
        api_base: The API base URL to use.
    """
    global _api_base
    _api_base = api_base
    logger.info(f"Grok 3 API base URL set to: {api_base}")


def get_grok3_api_base() -> str:
    """
    Get the Grok 3 API base URL.
    
    Returns:
        The API base URL.
    """
    global _api_base
    
    # If API base is already set, return it
    if _api_base:
        return _api_base
    
    # Try to get API base from environment variable
    api_base = os.environ.get(GROK3_API_BASE_ENV)
    if api_base:
        _api_base = api_base
        logger.info("Grok 3 API base URL loaded from environment variable")
        return _api_base
    
    # Use default API base
    logger.info(f"Using default Grok 3 API base URL: {DEFAULT_API_BASE}")
    return DEFAULT_API_BASE
