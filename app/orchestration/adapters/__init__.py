"""
__init__.py for the adapters module.

This module provides adapters for various orchestration frameworks.
"""

from .autogen_adapter import AutoGenAdapter
from .a2a_adapter import A2AAdapter

__all__ = ['AutoGenAdapter', 'A2AAdapter']
